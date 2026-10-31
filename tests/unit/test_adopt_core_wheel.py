"""scripts/adopt_core_wheel.py and the core-update.yml steps around it, run against copies of this repository's files.

The first adoption happens on GitHub, in a scheduled core-update run. Until then these tests make sure, in every pull
request, that the files still look the way the script expects (so that run does not fail on a stale exact match), that
the result is the one-line form the later bumps move, and that the workflow's own steps agree with it: the tag
check of the refs step, the bump, and the check that only the expected files changed.
The bump pull request cannot edit tests, so once the seed is gone the seed-only tests skip themselves and the rest run
against the adopted files as they are.
"""

import importlib.util
import os
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
# Keyed on a tracked file, not the folder: after the bump merges, `git pull` leaves ignored __pycache__ folders behind.
SEEDED = (ROOT / "packages" / "cloud-assessor-core" / "pyproject.toml").is_file()
HOSTILE_TAGS = [
    "v9|;etouch${IFS}PWNED;#",
    "v1.0.0\nchanged=true",
    "v1.0.0 ",
    "v1.0",
    "v1.0.0-rc.1",
    "1.0.0",
    "v1.0.0;id",
]
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


def _run_block(marker: str) -> str:
    """The `run: |` script of the one step whose header holds `marker` (for example `id: refs`), dedented."""
    lines = WORKFLOW.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip().removeprefix("- ") == marker]
    assert len(starts) == 1, f"expected one step with {marker!r} in core-update.yml"
    i = starts[0]
    while lines[i].strip() != "run: |":
        assert not lines[i + 1].startswith("      - "), f"the step with {marker!r} has no run block"
        i += 1
    body = []
    for line in lines[i + 1 :]:
        if line.strip() and not line.startswith(" " * 10):
            break
        body.append(line[10:])
    return "\n".join(body) + "\n"


def _run_refs(root, tmp_path, requested: str = "", gh_tag: str = "v0.2.1"):
    """The refs step's script as written, with a stand-in `gh` that answers with gh_tag."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    (bin_dir / "gh").write_text(f"#!/bin/sh\nprintf '%s\\n' {gh_tag!r}\n")
    (bin_dir / "gh").chmod(0o755)
    output = tmp_path / "github_output"
    output.write_text("")
    env = {
        "PATH": f"{bin_dir}:/usr/bin:/bin",
        "GITHUB_OUTPUT": str(output),
        "REQUESTED": requested,
        "UPSTREAM": "saulpatinojr/HCW-CloudAssessor_App",
    }
    proc = subprocess.run(["bash", "-c", _run_block("id: refs")], cwd=root, env=env, capture_output=True, text=True)
    return proc, output.read_text()


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


def test_after_the_first_adoption_the_bump_moves_the_pin(tmp_path):
    root = _copy(tmp_path)
    if SEEDED:
        adopt_core_wheel.adopt(root, "v0.2.1")
    current = _current_ref(root)
    assert re.fullmatch(r"v\d+\.\d+\.\d+", current), current
    assert 'python scripts/adopt_core_wheel.py --bump --from "$CURRENT" --tag "$LATEST"' in WORKFLOW
    assert "sed -i" not in WORKFLOW, "the pin is moved by an exact replacement, never a sed script"
    assert adopt_core_wheel.main(["--bump", "--from", current, "--tag", "v99.0.0", "--root", str(root)]) == 0
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'releases/download/v99.0.0/cloud_assessor_core-99.0.0-py3-none-any.whl",  # CORE_REF v99.0.0\n' in pyproject
    assert _current_ref(root) == "v99.0.0"


@pytest.mark.parametrize("tag", HOSTILE_TAGS)
def test_the_bump_refuses_a_hostile_tag_and_writes_nothing(tmp_path, tag):
    root = _copy(tmp_path)
    if SEEDED:
        adopt_core_wheel.adopt(root, "v0.2.1")
    before = (root / "pyproject.toml").read_text(encoding="utf-8")
    current = _current_ref(root)
    assert adopt_core_wheel.main(["--bump", "--from", current, "--tag", tag, "--root", str(root)]) == 1
    assert adopt_core_wheel.main(["--bump", "--from", tag, "--tag", "v99.0.0", "--root", str(root)]) == 1
    assert (root / "pyproject.toml").read_text(encoding="utf-8") == before


@pytest.mark.parametrize("tag", HOSTILE_TAGS)
@pytest.mark.parametrize("via", ["inputs.ref", "releases/latest"])
def test_the_refs_step_refuses_a_hostile_tag_before_writing_any_output(tmp_path, tag, via):
    root = _copy(tmp_path / "repo")
    work = tmp_path / "work"
    work.mkdir()
    proc, output = _run_refs(root, work, requested=tag if via == "inputs.ref" else "", gh_tag=tag)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "::error::refusing the upstream tag" in proc.stdout
    assert output == "", "nothing may reach GITHUB_OUTPUT before the tag is checked"
    assert not list(root.rglob("PWNED")) and not list(work.rglob("PWNED"))


def test_the_refs_step_passes_a_plain_tag(tmp_path):
    root = _copy(tmp_path / "repo")
    work = tmp_path / "work"
    work.mkdir()
    proc, output = _run_refs(root, work, gh_tag="v99.0.0")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert output.splitlines() == ["latest=v99.0.0", f"current={_current_ref(root)}", "changed=true"]


def _apply(repo, runner_temp, latest="v0.2.1", current="v0.1.0-seed") -> tuple[subprocess.CompletedProcess, str]:
    """The pull-request job's apply step as written, against a stand-in checkout and artifact."""
    output = runner_temp / "github_output"
    output.write_text("")
    env = {**os.environ, "RUNNER_TEMP": str(runner_temp), "GITHUB_OUTPUT": str(output), "LATEST": latest}
    env.update({"CURRENT": current, "GIT_CONFIG_GLOBAL": "/dev/null"})
    script = _run_block("id: apply")
    proc = subprocess.run(["bash", "-c", script], cwd=repo, env=env, capture_output=True, text=True)
    return proc, output.read_text()


@pytest.fixture
def bump_run(tmp_path):
    """A clean checkout holding the bump's paths and a seed, and the artifact job 1 would upload."""
    repo, temp = tmp_path / "repo", tmp_path / "temp"
    for name in (*FILES, "uv.lock", "docs/rules/catalog.md", "packages/cloud-assessor-core/src/x.py", "src/app.py"):
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text("before\n")
    git = {"cwd": repo, "check": True, "capture_output": True, "env": {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null"}}
    subprocess.run(["git", "init", "-q"], **git)
    subprocess.run(["git", "add", "-A"], **git)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base"], **git)
    art = temp / "bump"
    for name in ("pyproject.toml", "uv.lock", ".dockerignore", "docs/rules/catalog.md"):
        (art / "files" / name).parent.mkdir(parents=True, exist_ok=True)
        (art / "files" / name).write_text("after\n")
    (art / "deleted.txt").write_text("packages/cloud-assessor-core/src/x.py\n")
    (art / "outcome.txt").write_text("success\n")
    return repo, temp, art, git


def _status(repo) -> str:
    return subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True).stdout


def test_the_apply_step_takes_the_expected_bump(bump_run):
    repo, temp, _, _ = bump_run
    proc, output = _apply(repo, temp)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert output == "outcome=success\n"
    assert (repo / "pyproject.toml").read_text() == "after\n" and not (repo / "packages").exists()
    assert sorted(_status(repo).splitlines()) == sorted(
        [
            " M .dockerignore",
            " M docs/rules/catalog.md",
            " M pyproject.toml",
            " M uv.lock",
            "D  packages/cloud-assessor-core/src/x.py",
        ]
    )


@pytest.mark.parametrize(
    "tamper",
    [
        "extra-file",
        "deletion-outside",
        "dot-dot",
        "untracked-deletion",
        "symlink",
        "extra-entry",
        "outcome",
        "no-outcome",
    ],
)
def test_the_apply_step_refuses_a_tampered_artifact_and_changes_nothing(bump_run, tamper):
    repo, temp, art, _ = bump_run
    if tamper == "extra-file":
        (art / "files" / "src").mkdir()
        (art / "files" / "src" / "app.py").write_text("planted\n")
    elif tamper == "deletion-outside":
        (art / "deleted.txt").write_text("src/app.py\n")
    elif tamper == "dot-dot":
        (art / "deleted.txt").write_text("packages/cloud-assessor-core/../../src/app.py\n")
    elif tamper == "untracked-deletion":
        (art / "deleted.txt").write_text("packages/cloud-assessor-core/not-tracked.py\n")
    elif tamper == "symlink":
        (art / "files" / "uv.lock").unlink()
        (art / "files" / "uv.lock").symlink_to("/etc/passwd")
    elif tamper == "extra-entry":
        (art / "run.sh").write_text("echo planted\n")
    elif tamper == "outcome":
        (art / "outcome.txt").write_text("success\ncompat=true\n")
    else:
        (art / "outcome.txt").unlink()
    proc, output = _apply(repo, temp)
    assert proc.returncode == 1 and "::error::" in proc.stdout, proc.stdout + proc.stderr
    assert output == "" and _status(repo) == ""


@pytest.mark.parametrize("which", ["latest", "current"])
def test_the_apply_step_refuses_a_malformed_tag(bump_run, which):
    repo, temp, _, _ = bump_run
    hostile = "v9|;etouch${IFS}PWNED;#"
    proc, _ = _apply(repo, temp, **{which: hostile})
    assert proc.returncode == 1 and _status(repo) == ""


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
