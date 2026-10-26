"""base-update.yml opens its pull request with a GitHub App token, only when there is something to move, and keeps
untrusted text out of shell scripts.

These are static checks of the workflow text; they do not prove the credential works or that a run opens a pull request.
The first drift after the App is installed on this repository is that proof (see the header of the workflow).
"""

import importlib.util
import re

from ..conftest import ROOT

_spec = importlib.util.spec_from_file_location("follow_website_base", ROOT / "scripts" / "follow_website_base.py")
assert _spec is not None and _spec.loader is not None
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)

TEXT = (ROOT / ".github" / "workflows" / "base-update.yml").read_text(encoding="utf-8").replace("\r\n", "\n")
JOBS = dict(re.findall(r"(?ms)^  ([a-z-]+):\n(.*?)(?=^  [a-z-]+:\n|\Z)", TEXT.split("\njobs:\n", 1)[1]))
PLAN_STEPS = re.split(r"(?m)^ {6}- ", JOBS["plan"])[1:]
OPEN_STEPS = re.split(r"(?m)^ {6}- ", JOBS["open-pr"])[1:]
APP_STEP_OUTPUT = r"\$\{\{\s*steps\.app-token\.outputs\.token\s*\}\}"
CODE = "\n".join(line for line in TEXT.split("\n") if not line.lstrip().startswith("#"))


def _only(steps: list[str], action: str) -> str:
    found = [s for s in steps if re.search(rf"(?m)^\s*uses:\s*{re.escape(action)}@", s)]
    assert len(found) == 1, f"expected exactly one step using {action}"
    return found[0]


def _run_bodies(text: str) -> list[str]:
    """Every `run:` value: a one-line value, or the lines of a block scalar (`|`, `|-`, `>`...)."""
    bodies: list[str] = []
    lines = text.split("\n")
    for index, line in enumerate(lines):
        match = re.match(r"^(\s*)(?:- )?run:\s*(.*)$", line)
        if not match:
            continue
        indent, rest = len(match.group(1)), match.group(2)
        if re.fullmatch(r"[|>][+-]?", rest):
            block = []
            for follower in lines[index + 1 :]:
                if follower.strip() and len(follower) - len(follower.lstrip()) <= indent:
                    break
                block.append(follower)
            bodies.append("\n".join(block))
        else:
            bodies.append(rest)
    return bodies


def test_there_are_two_jobs_and_only_the_second_has_the_environment_and_the_credential():
    assert set(JOBS) == {"plan", "open-pr"}
    assert not re.search(r"(?m)^\s*environment:", JOBS["plan"]), "the plan job must hold no environment"
    assert re.search(r"(?m)^ {4}environment:\s*admin-ops\s*$", JOBS["open-pr"])
    private_key = [line for line in CODE.split("\n") if "APP_PRIVATE_KEY" in line]
    assert len(private_key) == 1, "the private key must be named in exactly one place"
    assert "APP_PRIVATE_KEY" in _only(OPEN_STEPS, "actions/create-github-app-token")
    assert "APP_CLIENT_ID" in _only(OPEN_STEPS, "actions/create-github-app-token")


def test_second_job_runs_only_when_the_plan_found_something_to_move():
    assert re.search(r"(?m)^ {4}needs:\s*plan\s*$", JOBS["open-pr"])
    assert re.search(r"(?m)^ {4}if:\s*needs\.plan\.outputs\.changed == 'true'\s*$", JOBS["open-pr"])
    registry = next(s for s in PLAN_STEPS if "docker buildx imagetools inspect" in s)
    assert re.search(r"(?m)^\s*if:\s*steps\.plan\.outputs\.changed == 'true'\s*$", registry)
    assert "linux/amd64" in registry and "comm -13" in registry, "the registry check must test the platforms"


def test_pull_request_is_opened_with_the_app_token_never_github_token():
    app = _only(OPEN_STEPS, "actions/create-github-app-token")
    pr = _only(OPEN_STEPS, "peter-evans/create-pull-request")
    assert re.search(r"(?m)^\s*id:\s*app-token\s*$", app)
    assert OPEN_STEPS.index(app) < OPEN_STEPS.index(pr), "the App token step must come before the pull request step"
    assert re.search(rf"(?m)^\s*token:\s*{APP_STEP_OUTPUT}\s*$", pr)
    assert "GITHUB_TOKEN" not in pr and "github.token" not in pr, "create-pull-request must not be given GITHUB_TOKEN"
    apply_step = next(s for s in OPEN_STEPS if "follow_website_base.py" in s)
    assert OPEN_STEPS.index(apply_step) < OPEN_STEPS.index(app), "the files are edited before the credential is minted"


def test_app_token_is_for_this_repository_only_with_contents_and_pull_requests_write():
    app = _only(OPEN_STEPS, "actions/create-github-app-token")
    assert re.search(r"client-id:\s*\$\{\{\s*vars\.APP_CLIENT_ID\s*\}\}", app)
    assert re.search(r"private-key:\s*\$\{\{\s*secrets\.APP_PRIVATE_KEY\s*\}\}", app)
    granted = dict(re.findall(r"(?m)^\s*permission-([a-z-]+):\s*(\w+)\s*$", app))
    assert granted == {"contents": "write", "pull-requests": "write"}
    assert not re.search(r"(?m)^\s*(owner|repositories):", app), "owner or repositories would widen the token"


def test_the_pull_request_adds_exactly_the_two_files_the_script_writes_on_one_stable_branch():
    pr = _only(OPEN_STEPS, "peter-evans/create-pull-request")
    paths = re.search(r"(?ms)^\s*add-paths:\s*\|\n(.*?)(?=^\s*[a-z-]+:|\Z)", pr)
    assert paths is not None
    assert sorted(paths.group(1).split()) == sorted([script.VERSIONS_ENV.as_posix(), script.DOCKERFILE.as_posix()])
    assert re.search(r"(?m)^\s*branch:\s*base-update/website-base\s*$", pr), "one fixed branch, reused"
    for key in ("author", "committer"):
        assert re.search(rf"(?m)^\s*{key}:\s*\"\$\{{\{{ steps\.app-token\.outputs\.app-slug \}}\}}\[bot\] <", pr)
    assert not re.search(r"(?m)^\s*draft:\s*true", pr), "ready for review, never a draft"
    assert "auto-merge" not in CODE.lower() and "pr merge" not in CODE, "nothing is merged automatically"


def test_github_token_is_read_only_and_every_job_has_a_timeout():
    assert re.search(r"(?m)^permissions:\s*\{\}\s*$", TEXT)
    for name, body in JOBS.items():
        assert re.search(r"(?m)^ {4}permissions:\n {6}contents:\s*read\s*$", body), (
            f"{name}: GITHUB_TOKEN must be read-only"
        )
        assert re.search(r"(?m)^ {4}timeout-minutes:\s*\d+\s*$", body), f"{name}: needs a timeout"
    # The App token's inputs are `permission-*`, a different key; any other `<name>: write` would widen GITHUB_TOKEN.
    assert not re.search(r"(?m)^[ \t]+(?!permission-)[a-z-]+:[ \t]*write[ \t]*$", TEXT), (
        "a permissions: block grants write"
    )


def test_no_expression_is_pasted_into_a_shell_script_and_the_python_runs_isolated():
    bodies = _run_bodies(TEXT)
    assert len(bodies) >= 4, "expected the run scripts of both jobs"
    for body in bodies:
        assert "${{" not in body, "an expression is interpolated into a run script"
    python_calls = [b for b in bodies if "follow_website_base.py" in b]
    assert len(python_calls) == 2 and all("python3 -I scripts/follow_website_base.py" in b for b in python_calls)
    assert sum("--check" in b for b in python_calls) == 1, "only the plan job runs the script in check mode"


def test_the_website_file_is_fetched_over_https_only_at_a_commit_with_limits():
    curls = re.findall(r"(?s)curl .*?-o ", CODE)
    assert len(curls) == 2
    for command in curls:
        for flag in ("--proto '=https'", "--proto-redir '=https'", "--tlsv1.2", "--max-time", "--max-filesize"):
            assert flag in command, f"curl lacks {flag}"
        assert "lab-image/versions.env" in command
    assert "/main/lab-image" not in CODE, "the file is read at a recorded commit, not at a moving branch"
    assert re.search(r"\^\[0-9a-f\]\{40\}\$", CODE), "the commit is checked to be a full SHA"


def test_every_checkout_drops_its_credentials_and_every_action_is_pinned_to_a_full_commit_sha():
    uses = re.findall(r"(?m)^\s*(?:- )?uses:\s*(\S+)", CODE)
    assert len(uses) == 4, "two checkouts, the App token and the pull request action"
    for reference in uses:
        assert re.fullmatch(r"[\w./-]+@[0-9a-f]{40}", reference), f"{reference} is not pinned to a full SHA"
    checkouts = [s for s in PLAN_STEPS + OPEN_STEPS if "actions/checkout@" in s]
    assert len(checkouts) == 2 and all("persist-credentials: false" in s for s in checkouts)


def test_runs_daily_and_by_hand_and_never_in_parallel_with_itself():
    assert re.search(r"(?m)^on:\n {2}schedule: \[\{ cron: \"\d{1,2} \d{1,2} \* \* \*\" \}\]$", TEXT)
    assert re.search(r"(?m)^ {2}workflow_dispatch:\s*$", TEXT)
    assert "cancel-in-progress: false" in TEXT
