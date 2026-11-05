"""The runtime (`lab`) stage of infrastructure/docker/Dockerfile applies Debian's security updates, in the shape that
keeps that step safe, and every workflow build of the Dockerfile passes the per-run cache bust the step names.

Why the step exists: the base image is pinned by digest, but a Debian security upload reaches the mirrors days before
the official image is rebuilt with it. On 2026-11-05 the website's Docker Scout gate refused the published image for apt
3.0.3 (CVE-2026-109518, fixed in 3.0.4 and published only in trixie-security) while the newest python:3.15-slim-trixie
digest still shipped 3.0.3, so no base move could clear it (website issue 1562; the NetworkEyes App took the same step
in its pull request 349). The upgrade closes that window; base-update.yml still moves the base with the website.

The shape, each part a separate assertion here so a loosened line is named:
  - `ARG PUBLISH_CACHE_BUST=` is declared in the lab stage and named (through printf) in the command of the upgrade RUN,
    so the layer's cache key differs on every workflow run and a rebuild of the same commit can never reuse an older
    upgrade result after a newer security upload reached the mirrors;
  - every `apt-get` in that RUN carries `-o Acquire::Retries=0`: the apt doing the upgrade is still the base's, and
    CVE-2026-109518 needs a download retry to slip an unverified package in;
  - the update carries `--error-on=any`, so a missing index (trixie-security above all) fails the build instead of
    succeeding with a warning and leaving apt unupgraded;
  - the upgrade is `-y --no-install-recommends`, the lists are removed in the same RUN, and it runs before anything is
    copied into the stage;
  - every workflow build of the Dockerfile (ci.yml's `docker build`, both `docker/build-push-action` steps of
    publish-images.yml) passes `PUBLISH_CACHE_BUST=${{ github.run_id }}-${{ github.run_attempt }}`, unique per build.

These are static checks of the text. They do not prove the built image carries the fixed apt; the publish workflow's
Trivy step and the website's Scout gate read the built image.
"""

import re
from pathlib import Path

import pytest

# Computed from this file's place, not imported from conftest, so the file is the same in every add-on repository.
ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = ROOT / "infrastructure" / "docker" / "Dockerfile"
WORKFLOWS = ROOT / ".github" / "workflows"
DOCKER_TEXT = DOCKERFILE.read_text(encoding="utf-8").replace("\r\n", "\n")
RUNTIME_STAGE = "lab"
CACHE_BUST_ARG = "PUBLISH_CACHE_BUST"
CACHE_BUST_VALUE = "PUBLISH_CACHE_BUST=${{ github.run_id }}-${{ github.run_attempt }}"
# Each workflow that builds the Dockerfile, with the number of builds it is expected to hold: a workflow that stops
# building would otherwise satisfy "every build passes the value" with no builds at all.
WORKFLOW_BUILDS = {"ci.yml": 1, "publish-images.yml": 2}
APT_GET = re.compile(r"apt-get((?:\s+-o\s+\S+)*)\s+(update|upgrade|install|dist-upgrade|full-upgrade)\b([^&|;]*)")
# Any package tool in a RUN of the runtime stage counts as package work, so a second RUN cannot slip an install past
# the checked one.
PACKAGE_TOOL = re.compile(r"\b(?:apt-get|apt|aptitude|dpkg)\b")
# Options that turn apt's verification off or let it take an older or unsigned package; none belongs in the step.
UNSAFE_APT = re.compile(
    r"--allow-unauthenticated|--allow-insecure-repositories|--allow-downgrades|AllowInsecureRepositories"
    r"|AllowUnauthenticated|Check-Valid-Until=false|--force-yes"
)


def logical_lines(text: str) -> list[str]:
    """Instruction lines with comments removed and backslash continuations joined, in order."""
    out: list[str] = []
    pending = ""
    for raw in text.split("\n"):
        line = raw.rstrip()
        if not pending and line.lstrip().startswith("#"):
            continue
        if line.endswith("\\"):
            pending += line[:-1] + " "
            continue
        out.append((pending + line).strip())
        pending = ""
    if pending:
        out.append(pending.strip())
    return [line for line in out if line]


def stage_lines(text: str, stage: str) -> list[str]:
    """The logical lines of the named stage (after its FROM, up to the next FROM)."""
    lines = logical_lines(text)
    starts = [i for i, line in enumerate(lines) if re.match(rf"FROM\s+\S+\s+AS\s+{re.escape(stage)}$", line, re.I)]
    assert len(starts) == 1, f"expected exactly one stage named {stage}"
    body: list[str] = []
    for line in lines[starts[0] + 1 :]:
        if line.upper().startswith("FROM "):
            break
        body.append(line)
    return body


def runtime_stage_problems(text: str) -> list[str]:
    problems: list[str] = []
    body = stage_lines(text, RUNTIME_STAGE)
    if f"ARG {CACHE_BUST_ARG}=" not in body:
        problems.append(f"the {RUNTIME_STAGE} stage does not declare `ARG {CACHE_BUST_ARG}=`")
    apt_runs = [line for line in body if line.startswith("RUN ") and PACKAGE_TOOL.search(line)]
    if len(apt_runs) != 1:
        problems.append(
            f"expected exactly one RUN doing package work in the {RUNTIME_STAGE} stage, found {len(apt_runs)}"
        )
        return problems
    run = apt_runs[0]
    first_copy = next((i for i, line in enumerate(body) if line.upper().startswith("COPY ")), len(body))
    if body.index(run) > first_copy:
        problems.append("the security-update RUN comes after a COPY; it must run before anything enters the stage")
    if not re.search(rf"printf\s+'[^']*%s[^']*'\s+\"?\$\{{?{CACHE_BUST_ARG}\}}?\"?", run):
        problems.append(f"the security-update RUN does not name {CACHE_BUST_ARG} through printf (no per-run cache key)")
    calls = APT_GET.findall(run)
    subcommands = [sub for _opts, sub, _rest in calls]
    if UNSAFE_APT.search(run):
        problems.append(f"the security-update RUN turns apt's verification off: {UNSAFE_APT.search(run).group(0)}")
    for opts, sub, rest in calls:
        # Exactly one Retries option, and it is 0: apt takes the last `-o` it is given, so a second `Retries=3`
        # after the `=0` would turn the retry path back on.
        if re.findall(r"Acquire::Retries=(\S+)", opts + rest) != ["0"]:
            problems.append(f"`apt-get {sub}` does not run with exactly one `-o Acquire::Retries=0`")
        if sub == "update" and "--error-on=any" not in rest:
            problems.append("`apt-get update` runs without `--error-on=any`")
        if sub == "upgrade" and not ("-y" in rest.split() and "--no-install-recommends" in rest.split()):
            problems.append("`apt-get upgrade` is not `-y --no-install-recommends`")
    if "update" not in subcommands:
        problems.append("the security-update RUN has no `apt-get update`")
    if "upgrade" not in subcommands:
        problems.append("the security-update RUN has no `apt-get upgrade`")
    if subcommands and subcommands[:2] != ["update", "upgrade"]:
        problems.append(f"apt-get order is {subcommands}; update then upgrade must come first")
    if "rm -rf /var/lib/apt/lists/*" not in run:
        problems.append("the security-update RUN does not remove /var/lib/apt/lists/*")
    return problems


def _code(text: str) -> str:
    return "\n".join(line for line in text.replace("\r\n", "\n").split("\n") if not line.lstrip().startswith("#"))


def _build_args(step: str) -> str:
    """The value of a step's build-args key: a scalar, or the lines of a `|` block."""
    match = re.search(r"(?m)^( *)build-args:[ \t]*(.*)$", step)
    if match is None:
        return ""
    indent, value = match.groups()
    if value.strip() != "|":
        return value.strip()
    block: list[str] = []
    for line in step[match.end() :].split("\n")[1:]:
        if line.strip() == "":
            continue
        if len(line) - len(line.lstrip(" ")) <= len(indent):
            break
        block.append(line.strip())
    return "\n".join(block)


def workflow_build_problems(text: str) -> tuple[int, list[str]]:
    """(number of Dockerfile builds found, problems)."""
    code = _code(text)
    problems: list[str] = []
    builds = 0
    for step in re.split(r"(?m)^ {6}- ", code)[1:]:
        if re.search(r"(?m)^\s*uses:\s*docker/build-push-action@", step) and re.search(
            r"(?m)^\s*file:\s*(?:\./)?infrastructure/docker/Dockerfile\s*$", step
        ):
            builds += 1
            if CACHE_BUST_VALUE not in _build_args(step).split("\n"):
                problems.append(f"a build-push-action step builds the Dockerfile without `{CACHE_BUST_VALUE}`")
        run = re.search(r"(?ms)^\s*run:\s*\|\n(.*?)(?=^ {8}\S|\Z)", step)
        if run is None:
            continue
        for line in logical_lines(run.group(1)):
            if "docker build" in line and "infrastructure/docker/Dockerfile" in line:
                builds += 1
                if CACHE_BUST_VALUE not in line:
                    problems.append(f"`docker build` of the Dockerfile without `{CACHE_BUST_VALUE}`: {line}")
    return builds, problems


def test_runtime_stage_applies_security_updates_in_the_pinned_shape() -> None:
    assert runtime_stage_problems(DOCKER_TEXT) == []


def _real_run() -> str:
    body = stage_lines(DOCKER_TEXT, RUNTIME_STAGE)
    return next(line for line in body if line.startswith("RUN ") and "apt-get" in line)


UPGRADE_LINE = " && apt-get -o Acquire::Retries=0 upgrade -y --no-install-recommends \\\n"
CLEAN_LINE = " && apt-get clean \\\n"
# (label, fragment of the real Dockerfile, what replaces it). Each case loosens one part of the step; the checker must
# name a problem for every one of them. The fragments are looked up inside the test, so a Dockerfile that has already
# lost one of them fails the shape test above with its reason, not this module at import.
LOOSENED = [
    ("no upgrade at all", UPGRADE_LINE, ""),
    ("update without --error-on=any", " update --error-on=any", " update"),
    ("update retries on", "apt-get -o Acquire::Retries=0 update", "apt-get update"),
    ("upgrade retries on", "apt-get -o Acquire::Retries=0 upgrade", "apt-get upgrade"),
    ("upgrade installs recommends", "upgrade -y --no-install-recommends", "upgrade -y"),
    ("no ARG", f"ARG {CACHE_BUST_ARG}=\n", ""),
    (
        "printf does not name the ARG",
        "printf 'security updates, run: %s\\n' \"${PUBLISH_CACHE_BUST}\"",
        "printf 'security updates\\n'",
    ),
    ("lists kept", " && rm -rf /var/lib/apt/lists/*\nRUN python", "\nRUN python"),
    (
        "an install with retries on",
        CLEAN_LINE,
        " && apt-get install -y --no-install-recommends ca-certificates \\\n" + CLEAN_LINE,
    ),
    (
        "a second RUN with apt-get",
        "COPY --from=build /install /usr/local",
        "RUN apt-get update\nCOPY --from=build /install /usr/local",
    ),
    (
        "a second RUN with dpkg after the copies",
        "WORKDIR /app",
        "RUN dpkg -i /tmp/extra.deb\nWORKDIR /app",
    ),
    ("upgrade allows unauthenticated packages", "upgrade -y", "upgrade -y --allow-unauthenticated"),
    (
        "a later Retries=3 wins over the Retries=0",
        "apt-get -o Acquire::Retries=0 upgrade",
        "apt-get -o Acquire::Retries=0 -o Acquire::Retries=3 upgrade",
    ),
]


@pytest.mark.parametrize(("label", "fragment", "replacement"), LOOSENED, ids=[case[0] for case in LOOSENED])
def test_a_loosened_security_update_step_is_noticed(label: str, fragment: str, replacement: str) -> None:
    assert fragment in DOCKER_TEXT, f"{label}: the fragment this case loosens is not in the Dockerfile: {fragment!r}"
    mutated = DOCKER_TEXT.replace(fragment, replacement, 1)
    assert runtime_stage_problems(mutated), f"{label}: the check did not notice"


def test_the_upgrade_runs_before_anything_is_copied_in() -> None:
    body = stage_lines(DOCKER_TEXT, RUNTIME_STAGE)
    copies = [i for i, line in enumerate(body) if line.upper().startswith("COPY ")]
    assert copies and body.index(_real_run()) < copies[0]


@pytest.mark.parametrize("name", sorted(WORKFLOW_BUILDS))
def test_every_workflow_build_of_the_dockerfile_passes_the_cache_bust(name: str) -> None:
    text = (WORKFLOWS / name).read_text(encoding="utf-8")
    builds, problems = workflow_build_problems(text)
    assert problems == []
    want = WORKFLOW_BUILDS[name]
    assert builds == want, f"{name}: expected {want} builds of the Dockerfile, found {builds}"


@pytest.mark.parametrize("name", sorted(WORKFLOW_BUILDS))
def test_a_workflow_build_without_the_cache_bust_is_noticed(name: str) -> None:
    text = (WORKFLOWS / name).read_text(encoding="utf-8")
    assert CACHE_BUST_VALUE in text
    mutated = text.replace(CACHE_BUST_VALUE, "EDITION=lab", 1)
    _builds, problems = workflow_build_problems(mutated)
    assert problems, f"{name}: dropping the cache bust from one build was not noticed"


def test_no_other_workflow_builds_the_dockerfile_unchecked() -> None:
    """A new workflow that builds the image must be added to WORKFLOW_BUILDS, so its builds are checked too."""
    for path in sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")]):
        if path.name in WORKFLOW_BUILDS:
            continue
        builds, _problems = workflow_build_problems(path.read_text(encoding="utf-8"))
        assert builds == 0, f"{path.name} builds the Dockerfile but is not listed in WORKFLOW_BUILDS"
