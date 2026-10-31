"""scripts/adopt_core_wheel.py and the core-update.yml steps around it, run against copies of this repository's files.

The first adoption happens on GitHub, in a scheduled core-update run. Until then these tests make sure, in every pull
request, that the files still look the way the script expects (so that run does not fail on a stale exact match), that
the result is the one-line form the later bumps move, and that the workflow's own grep and sed lines agree with it.
The bump pull request cannot edit tests, so once the seed is gone the seed-only tests skip themselves and the rest run
against the adopted files as they are.
"""

import importlib.util
import re
import shutil
import subprocess

import pytest

from ..conftest import ROOT

SPEC = importlib.util.spec_from_file_location("adopt_core_wheel", ROOT / "scripts" / "adopt_core_wheel.py")
adopt_core_wheel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adopt_core_wheel)

WORKFLOW = (ROOT / ".github" / "workflows" / "core-update.yml").read_text(encoding="utf-8")
FILES = ("pyproject.toml", "infrastructure/docker/Dockerfile", ".dockerignore")
SEEDED = (ROOT / "packages" / "cloud-assessor-core").is_dir()
seed_only = pytest.mark.skipif(not SEEDED, reason="the first adoption has happened: the engine is the release wheel")
URL_021 = "https://github.com/saulpatinojr/HCW-CloudAssessor_App/releases/download/v0.2.1/cloud_assessor_core-0.2.1-py3-none-any.whl"


def _copy(tmp_path):
    for name in FILES:
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, tmp_path / name)
    return tmp_path


def _workflow_line(prefix: str) -> str:
    lines = [line.strip() for line in WORKFLOW.splitlines() if line.strip().startswith(prefix)]
    assert len(lines) == 1, f"expected one line starting with {prefix!r} in core-update.yml"
    return lines[0]


def _current_ref(root) -> str:
    """The `current=` line of core-update.yml's refs step, run as written."""
    line = _workflow_line('current="$(grep')
    out = subprocess.run(["bash", "-c", f'{line}\necho "$current"'], cwd=root, capture_output=True, text=True)
    return out.stdout.strip()


@seed_only
def test_the_seed_is_marked_so_the_workflow_starts_the_first_adoption():
    assert _current_ref(ROOT) == "v0.1.0-seed"
    assert re.search(r"(?m)^\s*\*-seed\)\s*$", WORKFLOW), "the bump step has no first-adoption branch"
    assert 'python scripts/adopt_core_wheel.py --tag "$LATEST"' in WORKFLOW
    assert "git rm -r -q packages/cloud-assessor-core" in WORKFLOW


@seed_only
def test_first_adoption_rewrites_the_three_files(tmp_path):
    root = _copy(tmp_path)
    assert adopt_core_wheel.main(["--tag", "v0.2.1", "--root", str(root)]) == 0
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert f'  "cloud-assessor-core @ {URL_021}",  # CORE_REF v0.2.1\n' in pyproject
    assert "[tool.uv]" not in pyproject and "[tool.uv.sources]" not in pyproject
    assert 'testpaths = ["tests"]' in pyproject and 'source = ["src"]' in pyproject
    for name in FILES:
        assert "packages/cloud-assessor-core" not in (root / name).read_text(encoding="utf-8"), name
    dockerfile = (root / "infrastructure/docker/Dockerfile").read_text(encoding="utf-8")
    assert "COPY src/cloud_assessment_lab /install/lib/python3.14/site-packages/cloud_assessment_lab" in dockerfile
    assert _current_ref(root) == "v0.2.1"


def test_after_the_first_adoption_the_workflow_sed_moves_the_pin(tmp_path):
    root = _copy(tmp_path)
    if SEEDED:
        adopt_core_wheel.adopt(root, "v0.2.1")
    current = _current_ref(root)
    assert re.fullmatch(r"v\d+\.\d+\.\d+", current), current
    sed = _workflow_line("sed -i -E")
    script = f'CURRENT={current}; LATEST=v99.0.0; cur_ver="${{CURRENT#v}}"; new_ver="${{LATEST#v}}"\n{sed}'
    subprocess.run(["bash", "-c", script], cwd=root, check=True)
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert "releases/download/v99.0.0/cloud_assessor_core-99.0.0-py3-none-any.whl" in pyproject
    assert _current_ref(root) == "v99.0.0"


@seed_only
def test_a_file_that_does_not_match_leaves_everything_unchanged(tmp_path):
    root = _copy(tmp_path)
    dockerfile = root / "infrastructure/docker/Dockerfile"
    dockerfile.write_text(dockerfile.read_text(encoding="utf-8").replace("COPY packages/", "COPY ./packages/"))
    before = {name: (root / name).read_text(encoding="utf-8") for name in FILES}
    assert adopt_core_wheel.main(["--tag", "v0.2.1", "--root", str(root)]) == 1
    assert {name: (root / name).read_text(encoding="utf-8") for name in FILES} == before


@seed_only
def test_second_run_refuses_because_the_seed_line_is_gone(tmp_path):
    root = _copy(tmp_path)
    adopt_core_wheel.adopt(root, "v0.2.1")
    with pytest.raises(adopt_core_wheel.AdoptionError):
        adopt_core_wheel.adopt(root, "v0.2.1")


@seed_only
@pytest.mark.parametrize("tag", ["0.2.1", "v0.2", "v0.2.1-rc.1", "v0.2.1; rm -rf /", ""])
def test_only_a_plain_release_tag_is_accepted(tmp_path, tag):
    root = _copy(tmp_path)
    with pytest.raises(adopt_core_wheel.AdoptionError):
        adopt_core_wheel.adopt(root, tag)
    with pytest.raises(adopt_core_wheel.AdoptionError):
        adopt_core_wheel.adopt(root, tag, "http://127.0.0.1/x.whl")


def test_bump_pull_request_adds_only_paths_that_always_exist():
    block = WORKFLOW.split("add-paths: |\n", 1)[1].split("\n          body:", 1)[0]
    paths = [line.strip() for line in block.splitlines() if line.strip()]
    assert paths == [
        "pyproject.toml",
        "uv.lock",
        "infrastructure/docker/Dockerfile",
        ".dockerignore",
        "docs/rules/catalog.md",
    ]
    for path in paths:
        assert (ROOT / path).is_file(), path
