"""core-update.yml opens its bump pull request with the HCW Main Admin GitHub App token, never with GITHUB_TOKEN.

A pull request opened with GITHUB_TOKEN starts no workflow, so the required checks never run on it and it can never
merge. The App's client ID is the repository variable HCW_MAIN_ADMIN_CLIENT_ID and its private key is the repository
secret HCW_MAIN_ADMIN_PRIVATE_KEY; the job does not run in an environment. These are static checks of the workflow
text; they do not prove the credential works. A run with probe=true does (see the header of the workflow)."""

import re

from ..conftest import ROOT

TEXT = (ROOT / ".github" / "workflows" / "core-update.yml").read_text(encoding="utf-8")
JOBS = TEXT.split("\njobs:\n", 1)[1]
# The two jobs, by name: `bump` (runs project and upstream code, no secret) and `pull-request` (the App token).
JOB_TEXT = dict(
    zip(
        re.findall(r"(?m)^ {2}([A-Za-z0-9_-]+):\s*$", JOBS),
        re.split(r"(?m)^ {2}[A-Za-z0-9_-]+:\s*$", JOBS)[1:],
        strict=True,
    )
)
STEPS = re.split(r"(?m)^ {6}- ", JOBS)[1:]  # the steps of both jobs, in order
APP_STEP_OUTPUT = r"\$\{\{\s*steps\.app-token\.outputs\.token\s*\}\}"


def _only_in(job: str, header: str) -> str:
    found = [s for s in STEPS if s in job and re.search(rf"(?m)^\s*{re.escape(header)}\s*$", s)]
    assert len(found) == 1, f"expected exactly one step with {header}"
    return found[0]


def _only(action: str) -> str:
    found = [s for s in STEPS if re.search(rf"(?m)^\s*uses:\s*{re.escape(action)}@", s)]
    assert len(found) == 1, f"expected exactly one step using {action}"
    return found[0]


def test_pull_request_is_opened_with_the_app_token_never_github_token():
    app = _only("actions/create-github-app-token")
    pr = _only("peter-evans/create-pull-request")
    assert re.search(r"(?m)^\s*id:\s*app-token\s*$", app)
    assert STEPS.index(app) < STEPS.index(pr), "the App token step must come before the pull request step"
    assert re.search(rf"(?m)^\s*token:\s*{APP_STEP_OUTPUT}\s*$", pr)
    assert "GITHUB_TOKEN" not in pr, "create-pull-request must not be given GITHUB_TOKEN"


def test_every_step_that_runs_gh_pr_uses_the_app_token_after_it_was_minted():
    app = _only("actions/create-github-app-token")
    gh_pr = [s for s in STEPS if re.search(r"\bgh pr\b", s)]
    assert gh_pr, "the auto-merge step is missing"
    for step in gh_pr:
        assert re.search(rf"GH_TOKEN:\s*{APP_STEP_OUTPUT}", step)
        assert STEPS.index(app) < STEPS.index(step)


def test_token_is_minted_late_after_the_compatibility_check():
    app = _only("actions/create-github-app-token")
    compat = [s for s in STEPS if re.search(r"(?m)^\s*id:\s*compat\s*$", s)]
    assert len(compat) == 1, "expected exactly one compatibility step"
    assert STEPS.index(compat[0]) < STEPS.index(app), "the App token must be minted after the tests have run"


def test_token_action_is_pinned_to_a_full_commit_sha():
    app = _only("actions/create-github-app-token")
    assert re.search(r"(?m)^\s*uses:\s*actions/create-github-app-token@[0-9a-f]{40}(\s|$)", app)


def test_app_credential_is_the_hcw_main_admin_variable_and_secret():
    app = _only("actions/create-github-app-token")
    assert re.search(r"(?m)^\s*client-id:\s*\$\{\{\s*vars\.HCW_MAIN_ADMIN_CLIENT_ID\s*\}\}\s*$", app)
    assert re.search(r"(?m)^\s*private-key:\s*\$\{\{\s*secrets\.HCW_MAIN_ADMIN_PRIVATE_KEY\s*\}\}\s*$", app)
    # Only the token step is given the key.
    with_key = [s for s in STEPS if "secrets.HCW_MAIN_ADMIN_PRIVATE_KEY" in s]
    assert with_key == [app], "the private key must reach the token step and no other step"


def test_workflow_reads_no_other_secrets():
    names = set(re.findall(r"secrets\.([A-Za-z0-9_]+)", TEXT))
    assert names == {"GITHUB_TOKEN", "HCW_MAIN_ADMIN_PRIVATE_KEY"}
    for leak in ("toJSON(secrets", "secrets[", "secrets: inherit"):
        assert leak not in TEXT, f"{leak} would hand more than the one key to a step"


def test_app_token_is_limited_to_this_repository():
    app = _only("actions/create-github-app-token")
    # With `owner` set and `repositories` empty the action mints a token for every repository of the installation.
    # With no `owner`, an empty `repositories` falls back to the current repository, so this shape fails closed.
    assert not re.search(r"(?m)^\s*owner:", app), "owner must not be set: an empty repositories would widen the token"
    # One value, this repository's full name: not a list, not a wildcard, not another repository.
    assert re.search(r"(?m)^\s*repositories:\s*\$\{\{\s*github\.repository\s*\}\}\s*$", app)


def test_app_token_permissions_are_exactly_contents_and_pull_requests_write():
    app = _only("actions/create-github-app-token")
    granted = dict(re.findall(r"(?m)^\s*permission-([a-z-]+):\s*([a-z]+)\b", app))
    assert granted == {"contents": "write", "pull-requests": "write"}


def test_old_app_credential_is_gone():
    for old in ("admin-ops", "APP_CLIENT_ID", "APP_PRIVATE_KEY"):
        assert old not in TEXT, f"{old} must not appear in core-update.yml"
    assert "portfolio" not in TEXT.lower(), "the Portfolio App must not appear in core-update.yml"


def test_job_does_not_run_in_an_environment():
    # The credential is a repository variable and secret, so no environment is needed (or wanted) on the job.
    assert not re.search(r"(?m)^\s*environment:", TEXT)


def test_two_jobs_and_an_empty_top_level_permissions_block():
    assert re.search(r"(?m)^permissions: \{\}\s*$", TEXT), "top-level permissions must stay empty"
    assert list(JOB_TEXT) == ["bump", "pull-request"], "expected the jobs bump and pull-request, in that order"
    assert len(re.findall(r"(?m)^\s*permissions:\s*\{", TEXT)) == 1, "only the top level may use the inline form"
    for name, job in JOB_TEXT.items():
        assert re.search(r"(?m)^ {4}permissions:\n {6}contents:\s*read\s*\n(?! {6}\S)", job), (
            f"{name}: contents: read only"
        )


def test_the_job_that_runs_project_code_holds_no_secret_but_a_read_only_token_for_one_step():
    bump = JOB_TEXT["bump"]
    assert "HCW_MAIN_ADMIN" not in bump and "create-github-app-token" not in bump and "create-pull-request" not in bump
    # GITHUB_TOKEN reaches the refs step only (the upstream releases API), never a step that runs project code.
    steps = re.split(r"(?m)^ {6}- ", bump)[1:]
    with_token = [s for s in steps if "secrets." in s or "GH_TOKEN" in s]
    assert len(with_token) == 1 and re.search(r"(?m)^\s*id:\s*refs\s*$", with_token[0])
    assert not re.search(r"\b(uv|python|npx|npm|pytest)\b", with_token[0].split("run: |", 1)[1])


def _commands(job: str) -> str:
    """Every shell script of a job (the `run:` values), without comments and quoted messages."""
    blocks = re.findall(r"(?ms)^ {8}run: (?:\|\n(.*?)(?=^ {6}- |\Z)|(.*?)$)", job)
    lines = [ln for block, line in blocks for ln in (block or line).splitlines() if not ln.strip().startswith("#")]
    return re.sub(r"'[^'\n]*'|\"[^\"\n]*\"", '""', "\n".join(lines))


def test_the_job_that_holds_the_key_runs_no_engine_code_and_only_mains_bump_script():
    pr = JOB_TEXT["pull-request"]
    assert re.search(r"(?m)^ {4}needs:\s*bump\s*$", pr)
    scripts = _commands(pr)
    assert "git rm" in scripts and "gh pr merge" in scripts, "the run blocks were not found"
    # uv only to lock, never to build, sync or run; python only for main's bump script and the hashed uv install.
    assert set(re.findall(r"\buv\s+(\S+)", scripts)) == {"lock"}
    for line in scripts.splitlines():
        if re.search(r"\buv\s+lock\b", line):
            assert "--no-build" in line, line
    assert set(re.findall(r"\bpython3?\s+(\S+)", scripts)) == {"scripts/adopt_core_wheel.py", "-m"}
    assert re.findall(r"\bpython3?\s+-m\s+(\S+\s+\S+\s+\S+)", scripts) == ["pip install --require-hashes"]
    assert set(re.findall(r"scripts/\S+", scripts)) == {"scripts/adopt_core_wheel.py"}
    for word in (r"\bpytest\b", r"\bnpx\s", r"\bnpm\s", r"\bmake\s", r"\bpip\s+install\s+(?!--require-hashes)"):
        assert not re.search(word, scripts), f"the pull-request job must not run project or engine code ({word})"
    apply = _only_in(pr, "id: apply")
    app = _only("actions/create-github-app-token")
    assert STEPS.index(apply) < STEPS.index(app), "the artifact must be checked and applied before the token is minted"


def test_the_pull_request_job_installs_the_same_uv_as_the_bump_job_by_hash():
    version = re.findall(r'"uv==([0-9.]+)"', JOB_TEXT["bump"])
    hashed = re.findall(r"uv==([0-9.]+) --hash=sha256:[0-9a-f]{64}\b", JOB_TEXT["pull-request"])
    assert len(version) == 1 and hashed == version, "move the uv hash in the pull-request job with UV_VERSION"


def _steps_of(job: str) -> list[str]:
    return re.split(r"(?m)^ {6}- ", JOB_TEXT[job])[1:]


def test_auto_merge_never_reads_the_untrusted_outcome():
    merge = [s for s in STEPS if re.search(r"\bgh pr merge\b", s)]
    assert len(merge) == 1
    condition = merge[0].split("\n", 1)[0]
    assert condition.startswith("if: ")
    # The outcome comes from the job that ran upstream code, so it must not decide the merge. What does: the repository
    # variable, this job's own byte-for-byte check, and GitHub's required checks on the pull request.
    for part in (
        "vars.CORE_AUTOMERGE == 'true'",
        "steps.apply.outcome == 'success'",
        "steps.pr.outputs.pull-request-number != ''",
        "!inputs.probe",
    ):
        assert part in condition, part
    assert not re.search(r"outputs\.outcome|outcome\.txt", merge[0]), "the auto-merge step must not read the outcome"
    assert 'gh pr merge --squash --auto "$PR_NUMBER"' in merge[0], "auto-merge waits for the required checks"
    assert "--admin" not in merge[0]
    # The outcome reaches only the pull request's text (title, labels, body) and a warning that holds no token.
    readers = [s for s in _steps_of("pull-request") if "steps.apply.outputs.outcome" in s]
    pr = _only("peter-evans/create-pull-request")
    assert len(readers) == 2 and pr in readers
    warning = next(s for s in readers if s != pr)
    assert not re.search(r"GH_TOKEN|secrets\.|app-token|\bgh\b", warning), "the warning step must hold no token"


REFUSE_NAME = "name: Refuse a run that is not on main"


def test_both_jobs_refuse_a_run_that_is_not_on_main_first_and_visibly():
    for name in JOB_TEXT:
        first = _steps_of(name)[0]
        assert first.startswith(REFUSE_NAME), f"{name}: the first step must be the main-only refusal"
        assert not re.search(r"(?m)^\s*if:", first), f"{name}: the refusal must always run"
        assert re.search(r'(?m)^ {8}env: \{ RUN_REF: "\$\{\{ github\.ref \}\}" \}$', first), name
        block = first.split("run: |\n", 1)[1]
        assert 'if [ "$RUN_REF" != "refs/heads/main" ]; then' in block
        assert re.search(r'echo "::error::[^"]*\$\{RUN_REF\}[^"]*"', block), f"{name}: the error must name the ref"
        assert re.search(r"(?m)^\s*exit 1$", block)
        assert "${{" not in block, f"{name}: no expression inside the shell"
    # A job-level `if:` would skip the bump job in silence; the pull-request job is also gated by one.
    assert not re.search(r"(?m)^    if:", JOB_TEXT["bump"]), "the bump job must refuse, not be skipped silently"
    job_if = "if: github.ref == 'refs/heads/main' && (needs.bump.outputs.changed == 'true' || inputs.probe)"
    assert re.search(rf"(?m)^    {re.escape(job_if)}$", JOB_TEXT["pull-request"])


def test_both_checkouts_take_the_commit_the_run_was_started_for_after_the_refusal():
    with_line = 'with: { persist-credentials: false, ref: "${{ github.sha }}" }'
    for name in JOB_TEXT:
        steps = _steps_of(name)
        checkouts = [s for s in steps if re.search(r"(?m)^uses:\s*actions/checkout@", s)]
        assert len(checkouts) == 1, name
        assert re.search(rf"(?m)^ {{8}}{re.escape(with_line)}$", checkouts[0]), name
        assert steps.index(checkouts[0]) > 0 and steps[0].startswith(REFUSE_NAME), name
    # A checkout of a commit is a detached HEAD, where create-pull-request needs the base named.
    assert re.search(r"(?m)^ {10}base: main$", _only("peter-evans/create-pull-request"))


def test_github_token_is_read_only():
    assert re.search(r"(?m)^ {4}permissions:\n {6}contents:\s*read\s*$", TEXT)
    # The App token's inputs are `permission-*`, a different key; any other `<name>: write` would widen GITHUB_TOKEN.
    write_grant = re.search(r"(?m)^[ \t]+(?!permission-)[a-z-]+:[ \t]*write[ \t]*$", TEXT)
    assert not write_grant, "a permissions: block grants write"


def test_every_action_is_pinned_to_a_full_commit_sha():
    uses = [u for u in re.findall(r"(?m)^[ \t]*(?:- )?uses:[ \t]*(\S+)", TEXT) if not u.startswith("./")]
    assert len(uses) >= 4
    for use in uses:
        assert re.search(r"@[0-9a-f]{40}$", use), f"{use} is not pinned to a commit SHA"


def test_a_probe_run_never_reaches_a_step_that_writes():
    # A manual run with probe=true must stay read-only even when a newer release exists (changed == 'true').
    writers = [s for s in STEPS if "peter-evans/create-pull-request@" in s or re.search(r"\bgh pr\b", s)]
    assert len(writers) == 2, "expected the pull request step and the auto-merge step"
    for step in writers:
        assert re.search(r"(?m)^\s*(?:- )?if:.*!inputs\.probe", step), "a step that writes must be skipped on a probe"


def test_probe_step_only_reads_and_checks_the_token_covers_this_repository_only():
    probe = [s for s in STEPS if re.search(r"(?m)^\s*if:\s*inputs\.probe\s*$", s)]
    assert len(probe) == 1, "expected exactly one probe step"
    assert re.search(r'gh api "repos/\$\{REPO\}"', probe[0])
    assert re.search(r"gh api installation/repositories", probe[0])
    assert re.search(r'test "\$\{covered\}" = "\$\{REPO\}"', probe[0]), "the probe must fail if the token covers more"
    # `gh api` turns into a POST as soon as it is given a field, so fields and bodies are as forbidden as -X, with
    # the value attached (-XPOST, -fname=value) or separate.
    writes = r"\bgh pr\b|\bgit\b|--method|\s-[XfF]|--field|--raw-field|--input"
    assert not re.search(writes, probe[0]), "the probe must not write"
