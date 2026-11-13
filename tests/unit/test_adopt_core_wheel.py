"""scripts/adopt_core_wheel.py and the core-update.yml steps around it, run against copies of this repository's files.

These tests make sure, in every pull request, that pyproject.toml still looks the way the bump expects (so a
scheduled core-update run does not fail on a stale exact match) and that the workflow's own steps agree with it: the
tag check of the refs step, the bump, and the check that only the expected files changed. (The first adoption from the
local seed under packages/ happened in pull request 69; its code and tests have been removed since.)
"""

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tomllib

import pytest

from ..conftest import ROOT

SPEC = importlib.util.spec_from_file_location("adopt_core_wheel", ROOT / "scripts" / "adopt_core_wheel.py")
adopt_core_wheel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adopt_core_wheel)

WORKFLOW = (ROOT / ".github" / "workflows" / "core-update.yml").read_text(encoding="utf-8")
FILES = ("pyproject.toml",)
HOSTILE_TAGS = [
    "v9|;etouch${IFS}PWNED;#",
    "v1.0.0\nchanged=true",
    "v1.0.0 ",
    "v1.0",
    "v1.0.0-rc.1",
    "1.0.0",
    "v1.0.0;id",
]


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


def test_the_bump_moves_the_pin(tmp_path):
    root = _copy(tmp_path)
    current = _current_ref(root)
    assert re.fullmatch(r"v\d+\.\d+\.\d+", current), current
    assert 'python scripts/adopt_core_wheel.py --bump --from "$CURRENT" --tag "$LATEST"' in WORKFLOW
    assert "sed -i" not in WORKFLOW, "the pin is moved by an exact replacement, never a sed script"
    before = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert adopt_core_wheel.main(["--bump", "--from", current, "--tag", "v99.0.0", "--root", str(root)]) == 0
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'releases/download/v99.0.0/cloud_assessor_core-99.0.0-py3-none-any.whl",  # CORE_REF v99.0.0\n' in pyproject
    assert _current_ref(root) == "v99.0.0"
    # Exactly two lines move: the pin and the version of the engine's static metadata (CORE_METADATA).
    changed = [(a, b) for a, b in zip(before.splitlines(), pyproject.splitlines(), strict=True) if a != b]
    assert changed == [
        (adopt_core_wheel.pinned_line(current), adopt_core_wheel.pinned_line("v99.0.0")),
        (adopt_core_wheel.metadata_line(current), adopt_core_wheel.metadata_line("v99.0.0")),
    ]
    entry = tomllib.loads(pyproject)["tool"]["uv"]["dependency-metadata"][0]
    assert entry["name"] == "cloud-assessor-core" and entry["version"] == "99.0.0"


@pytest.mark.parametrize(
    "edit",
    [
        lambda t, cur: t.replace("  # CORE_METADATA", "  # CORE-METADATA"),
        lambda t, cur: t + adopt_core_wheel.metadata_line(cur) + "\n",
        lambda t, cur: t.replace("# CORE_REF", "#CORE_REF"),
    ],
    ids=["no-metadata-marker", "metadata-twice", "no-core-ref-marker"],
)
def test_the_bump_refuses_a_pyproject_it_does_not_recognise_and_writes_nothing(tmp_path, edit):
    """Both lines move or neither: a pin moved without its CORE_METADATA line would leave uv asking the address."""
    root = _copy(tmp_path)
    current = _current_ref(root)
    text = edit((root / "pyproject.toml").read_text(encoding="utf-8"), current)
    (root / "pyproject.toml").write_text(text, encoding="utf-8")
    assert adopt_core_wheel.main(["--bump", "--from", current, "--tag", "v99.0.0", "--root", str(root)]) == 1
    assert (root / "pyproject.toml").read_text(encoding="utf-8") == text


def test_the_bump_refuses_the_same_tag(tmp_path):
    root = _copy(tmp_path)
    current = _current_ref(root)
    assert adopt_core_wheel.main(["--bump", "--from", current, "--tag", current, "--root", str(root)]) == 1


@pytest.mark.parametrize("tag", HOSTILE_TAGS)
def test_the_bump_refuses_a_hostile_tag_and_writes_nothing(tmp_path, tag):
    root = _copy(tmp_path)
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


def test_the_refs_step_fails_without_a_core_ref(tmp_path):
    """No CORE_REF used to mean "the seed is still local"; now it can only mean a broken pin, so the run fails."""
    root = _copy(tmp_path / "repo")
    pyproject = root / "pyproject.toml"
    pyproject.write_text(pyproject.read_text(encoding="utf-8").replace("# CORE_REF", "# PIN"), encoding="utf-8")
    work = tmp_path / "work"
    work.mkdir()
    proc, output = _run_refs(root, work, gh_tag="v99.0.0")
    assert proc.returncode == 1 and "::error::no CORE_REF" in proc.stdout, proc.stdout + proc.stderr
    assert output == ""


def test_the_script_refuses_to_run_without_bump(tmp_path):
    root = _copy(tmp_path)
    before = (root / "pyproject.toml").read_text(encoding="utf-8")
    current = _current_ref(root)
    assert adopt_core_wheel.main(["--tag", "v99.0.0", "--root", str(root)]) == 1
    assert adopt_core_wheel.main(["--bump", "--tag", "v99.0.0", "--root", str(root)]) == 1
    assert adopt_core_wheel.main(["--from", current, "--tag", "v99.0.0", "--root", str(root)]) == 1
    assert (root / "pyproject.toml").read_text(encoding="utf-8") == before


# Stand-in for `uv lock`: a deterministic change to uv.lock, with no network.
FAKE_UV = "#!/bin/sh\nprintf 'locked %s\\n' \"$*\" >> uv.lock\n"
NEW_CATALOG = (
    "# Criteria catalog\n\nGenerated by `scripts/check-catalog.py --doc`.\n\nCatalog version 9.9.9, x <= 20.\n"
)


def _tools(tmp_path):
    """A bin directory with the stand-in uv and this interpreter as `python`."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    (bin_dir / "uv").write_text(FAKE_UV)
    (bin_dir / "uv").chmod(0o755)
    (bin_dir / "python").symlink_to(sys.executable)
    return bin_dir


def _git(repo, *args):
    env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null"}
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True, env=env)


def _apply(repo, temp, bin_dir, latest, current) -> tuple[subprocess.CompletedProcess, str]:
    """The pull-request job's apply step as written, against a clean checkout and an artifact."""
    output = temp / "github_output"
    output.write_text("")
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "RUNNER_TEMP": str(temp)}
    env.update({"GITHUB_OUTPUT": str(output), "LATEST": latest, "CURRENT": current, "GIT_CONFIG_GLOBAL": "/dev/null"})
    proc = subprocess.run(["bash", "-c", _run_block("id: apply")], cwd=repo, env=env, capture_output=True, text=True)
    return proc, output.read_text()


@pytest.fixture
def bump_run(tmp_path):
    """A clean checkout of this repository's bump files, and the artifact the bump job would upload for it.

    The bump job's side is simulated with the same script and the stand-in uv, then its real collect step runs.
    """
    repo, job_a, temp = tmp_path / "repo", tmp_path / "job-a", tmp_path / "temp"
    names = [*FILES, "uv.lock", "docs/rules/catalog.md", "scripts/adopt_core_wheel.py"]
    for name in names:
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, repo / name)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("app\n")
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
    bin_dir = _tools(tmp_path)
    current = _current_ref(repo)
    latest = "v99.0.0"
    _git(tmp_path, "clone", "-q", str(repo), str(job_a))
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"}
    bump_args = ["--bump", "--from", current, "--tag", latest]
    subprocess.run(["python", "scripts/adopt_core_wheel.py", *bump_args], cwd=job_a, env=env, check=True)
    lock_args = ["lock", "--no-build", "--upgrade-package", "cloud-assessor-core"]
    subprocess.run(["uv", *lock_args], cwd=job_a, env=env, check=True)
    (job_a / "docs" / "rules" / "catalog.md").write_text(NEW_CATALOG)
    collect = _run_block("name: Collect the bump for the pull-request job")
    env_collect = {**os.environ, "RUNNER_TEMP": str(temp), "COMPAT": "success"}
    subprocess.run(["bash", "-c", collect], cwd=job_a, env=env_collect, check=True, capture_output=True)
    return repo, temp, temp / "bump", bin_dir, latest, current


def _status(repo) -> list[str]:
    return sorted(_git(repo, "status", "--porcelain").stdout.splitlines())


def test_the_apply_step_takes_a_bump_identical_to_its_own(bump_run):
    repo, temp, _, bin_dir, latest, current = bump_run
    proc, output = _apply(repo, temp, bin_dir, latest, current)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert output == "outcome=success\n"
    assert (repo / "docs" / "rules" / "catalog.md").read_text() == NEW_CATALOG
    assert _status(repo) == [" M docs/rules/catalog.md", " M pyproject.toml", " M uv.lock"]


def _append(path, text):
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


TAMPERING = {
    "pyproject-extra-line": lambda art: _append(art / "files" / "pyproject.toml", 'evil = "yes"\n'),
    "uv-lock-changed": lambda art: _append(art / "files" / "uv.lock", "# changed\n"),
    "dockerfile-edited": lambda art: _append_or_create(art / "files/infrastructure/docker/Dockerfile", "RUN evil\n"),
    "deletion": lambda art: _append(art / "deleted.txt", "src/app.py\n"),
    "extra-file": lambda art: (art / "files" / "src").mkdir() or (art / "files" / "src" / "app.py").write_text("x\n"),
    "symlink": lambda art: (
        (art / "files" / "uv.lock").unlink() or (art / "files" / "uv.lock").symlink_to("/etc/passwd")
    ),
    "extra-entry": lambda art: (art / "run.sh").write_text("echo planted\n"),
    "outcome": lambda art: (art / "outcome.txt").write_text("success\ncompat=true\n"),
    "no-outcome": lambda art: (art / "outcome.txt").unlink(),
    "catalog-html": lambda art: _append(art / "files" / "docs" / "rules" / "catalog.md", "<script>x</script>\n"),
    "catalog-control": lambda art: _append(art / "files" / "docs" / "rules" / "catalog.md", "bell\x07\n"),
    "catalog-heading": lambda art: (art / "files" / "docs" / "rules" / "catalog.md").write_text("# Other\n"),
    "catalog-size": lambda art: _append(art / "files" / "docs" / "rules" / "catalog.md", "a" * 300_000 + "\n"),
}


def _append_or_create(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((path.read_text(encoding="utf-8") if path.exists() else "") + text, encoding="utf-8")


@pytest.mark.parametrize("tamper", sorted(TAMPERING))
def test_the_apply_step_refuses_a_tampered_artifact_and_changes_nothing(bump_run, tamper):
    repo, temp, art, bin_dir, latest, current = bump_run
    TAMPERING[tamper](art)
    proc, output = _apply(repo, temp, bin_dir, latest, current)
    assert proc.returncode == 1 and "::error::" in proc.stdout, proc.stdout + proc.stderr
    assert output == "" and _status(repo) == []


@pytest.mark.parametrize("which", ["latest", "current"])
def test_the_apply_step_refuses_a_malformed_tag(bump_run, which):
    repo, temp, _, bin_dir, latest, current = bump_run
    tags = {"latest": latest, "current": current, which: "v9|;etouch${IFS}PWNED;#"}
    proc, _ = _apply(repo, temp, bin_dir, tags["latest"], tags["current"])
    assert proc.returncode == 1 and _status(repo) == [] and not list(repo.rglob("PWNED"))


def test_the_apply_step_runs_only_mains_script_and_uv_lock():
    lines = [line for line in _run_block("id: apply").splitlines() if not line.strip().startswith("#")]
    script = re.sub(r'"[^"\n]*"', '""', "\n".join(lines))  # commands only: no comments, no quoted messages
    assert re.findall(r"\buv\s+(\S+)", script) == ["lock"]
    assert all("--no-build" in line for line in script.splitlines() if re.search(r"\buv\s+lock\b", line))
    assert set(re.findall(r"\bpython3?\s+(\S+)", script)) == {"scripts/adopt_core_wheel.py"}


def test_bump_pull_request_adds_only_paths_that_always_exist():
    block = WORKFLOW.split("add-paths: |\n", 1)[1].split("\n          body:", 1)[0]
    paths = [line.strip() for line in block.splitlines() if line.strip()]
    assert paths == [
        "pyproject.toml",
        "uv.lock",
        "docs/rules/catalog.md",
    ]
    for path in paths:
        assert (ROOT / path).is_file(), path
