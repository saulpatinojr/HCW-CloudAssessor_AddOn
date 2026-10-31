# What is new upstream (HCW-CloudAssessor_App)

**How to use this file.** The Cloud Assessor engine is written and released in
[`HCW-CloudAssessor_App`](https://github.com/saulpatinojr/HCW-CloudAssessor_App), and this lab edition adopts it. Read
this file before you change behaviour here, so you know what upstream already did and what is still waiting to be adopted,
and add an entry (newest first) whenever you adopt an upstream change or find that one reaches this repository.

Last updated: 2026-10-31, from a clone of the App's tag `v0.2.1` (commit `55b7242`); the table and the entries dated
2026-10-24 were checked against GitHub and the App's `main` at `e22603c` on that date and are not re-checked here. Where
something was not checked, it says so.

## Current upstream state

| Question | Answer |
|---|---|
| Who owns the engine? | The App. It was seeded here (`ADR-0001`), the App adopted it unchanged, and since then engine and catalog changes are made upstream, released, and adopted here. Do not edit `packages/cloud-assessor-core` in this repository. |
| Latest App releases | [`v0.2.1`](https://github.com/saulpatinojr/HCW-CloudAssessor_App/releases/tag/v0.2.1) (2026-10-18, tag commit `55b7242`) and [`v0.2.0`](https://github.com/saulpatinojr/HCW-CloudAssessor_App/releases/tag/v0.2.0) (2026-10-12, tag commit `6821e30`). There is no `v0.1.0` tag in the App. |
| Engine wheel to pin | `cloud_assessor_core-0.2.1-py3-none-any.whl` from the `v0.2.1` release. sha256 `6c5564ba0bc82c79060704dd52871e56b51b709c9ee8bdd7b6b7cf0409ca26e7` (downloaded and hashed; it matches the digest GitHub shows). The `v0.2.0` wheel is `31fde826a3ff0dccfcaee084a00e86df83e28473567dfdb75ad74319425bc638` (digest as GitHub shows it; not downloaded). |
| What this repository has | The original seed, engine `0.1.0`, catalog `1.0.0`, under `packages/cloud-assessor-core` (a workspace member). Since 2026-10-31 its dependency line in `pyproject.toml` carries the marker `CORE_REF v0.1.0-seed`, so `core-update.yml` is armed: its next run sees `v0.2.1` and opens the adoption pull request itself (see "Adopting `v0.2.1`" below). |
| Drift | Behind by two releases until that pull request merges. |
| Does the App's version match its tags? | No, by design for now: the App's own `pyproject.toml` says `0.1.0`, the engine and the tags are `0.2.x`. The policy is an open owner decision (App [#33](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/33)). The wheel's version is what matters for pinning here. |
| Protection on the App | Rulesets on `main` (pull request required; checks `lint`, `test`, `boundary`, `catalog-check`, `secret-scan`, `image`, `terraform` required; no force-push or deletion) and on `v*` tags (cannot be moved or deleted), applied on 2026-10-24 with the App's `repository-admin` workflow and read back through the API. A pinned `v*` URL therefore keeps pointing at the same release. Protection on **this** repository was not checked. |

## What upstream changed in the engine (not yet adopted here)

**Reaches this repository: yes.** Two releases of `cloud-assessor-core` sit between the seed and today.

- **`v0.2.0` (2026-10-12): engine `0.2.0`, catalog `1.1.0`.** Adds the models `CostEvidence` and `BudgetEvidence`, a new
  evaluator kind `cost-evidence` (`budgets-present`, `anomaly-alerts-present`, `untagged-share`),
  `evaluate(resources, catalog, *, evidence=None)`, and optional `edition` and `scope` fields on `Assessment`. Without
  evidence, a `cost-evidence` check is skipped and the criterion is judged from the export exactly as before.
  `CA-FIN-002`, `CA-FIN-003` and `CA-FIN-007` gain a second check. `MODEL_VERSION` stays `1` because `Resource` did not
  change. `redaction.ALLOWED_WORDS` gains the appliance's event names. Evaluator kinds were only added, never renamed.
- **`v0.2.1` (2026-10-18): engine `0.2.1`.** `pydantic` is declared as a range (`>=2.14,<3`) instead of an exact pin
  (App #15 and #16). This repository's seed already declares the same range, so the resolved set does not change.

**Trial result (2026-10-24, nothing in this repository was changed).** In a throwaway copy of this repository, the seed
was replaced by the App's `0.2.1` package and the unit, security, contract, end-to-end and engine tests were run: 160
passed and 1 failed. The failure is `tests/unit/test_api.py::test_health_is_flat_and_complete` (line 32), which pins the
catalog version at `1.0.0` while the engine now reports `1.1.0`. That is a stale test value, not a behaviour change. Because one test fails, `core-update.yml`
would label the pull request `needs adaptation`, and the adaptation is the one-line pin change. `scripts/check-catalog.py`
passed; `make rules-doc` changes 6 lines of `docs/rules/catalog.md`; regenerating the App's `catalog/schema.json` produced no change.
**Not run in the trial:** the Playwright browser suite (`make e2e`) and the Docker image build.

### Adopting `v0.2.1`: the workflow does it

The adoption is now automatic. Pull request "Adopt engine v0.2.1 through core-update" (2026-10-31, branch
`chore/adopt-core-v0.2.1`) made this repository ready for the wheel and put the marker `CORE_REF v0.1.0-seed` on the
seed's dependency line. It did not switch the dependency itself, because the session that wrote it could not download
the release asset, and `uv lock` has to download the wheel to record its sha256 (`uv.lock` is never edited by hand).

What happens next, on GitHub:

1. The next run of `core-update.yml` (scheduled at minute 41 of hours 0, 6, 12 and 18 UTC, or started by hand with
   `gh workflow run core-update.yml -R saulpatinojr/HCW-CloudAssessor_AddOn --ref main`) compares `v0.1.0-seed` with the
   latest release, `v0.2.1`, and finds them different.
2. Because the old pin ends in `-seed`, its bump step runs `scripts/adopt_core_wheel.py --tag v0.2.1`: the dependency
   line becomes
   `"cloud-assessor-core @ https://github.com/saulpatinojr/HCW-CloudAssessor_App/releases/download/v0.2.1/cloud_assessor_core-0.2.1-py3-none-any.whl",  # CORE_REF v0.2.1`,
   the `[tool.uv]` workspace and `[tool.uv.sources]` entries go, the seed leaves `testpaths` and the coverage `source`,
   and the Dockerfile's two `COPY packages/cloud-assessor-core/...` lines and the `.dockerignore` line for the seed's
   tests go. Then `git rm -r packages/cloud-assessor-core` and `uv lock`, which downloads the wheel and records its sha256.
   The sha256 to expect is `6c5564ba0bc82c79060704dd52871e56b51b709c9ee8bdd7b6b7cf0409ca26e7` (see the table).
3. `docs/rules/catalog.md` is regenerated from catalog `1.1.0` (12 lines change: the version line, and the checks and
   texts of `CA-FIN-002`, `CA-FIN-003` and `CA-FIN-007`).
4. The compatibility check (lint, catalog, tests, Playwright) decides the label. It is expected to be `compatible`.
   With the repository variable `CORE_AUTOMERGE` set to `true` the run asks GitHub to auto-merge the pull request
   whatever the label says, and the merge happens only once the required checks of the `main` rules pass on the pull
   request; the label is a hint, never the gate.

Steps 1 to 4 run in two jobs, so the new engine's code never shares a runner with the App's key. The `bump` job does
the bump, the catalog page and the compatibility check with no secret (a read-only `GITHUB_TOKEN` reaches only the
step that asks for the latest release, which runs no project code), and uploads the changed files, the list of deleted
paths and the outcome as an artifact. The `pull-request` job starts on a fresh runner from a clean checkout and runs
none of the engine's code. It regenerates the bump itself with main's own `scripts/adopt_core_wheel.py` and
`uv lock --no-build` (which reads metadata only and builds nothing), and refuses the artifact unless its
`pyproject.toml`, `uv.lock`, Dockerfile, `.dockerignore` and deletions are byte-identical to what it produced. The one
file it takes from the artifact is `docs/rules/catalog.md`, because generating it needs the engine, and only as plain
Markdown (UTF-8 text, no control characters, no HTML, at most 256 KiB, starting with its heading); the bump pull
request's own `catalog-check` job, which holds no secret, then proves it matches the engine. Only then does the job
mint the App token and open the pull request. The outcome counts as untrusted: it picks the label, the title, the
body text and the not-compatible warning, and auto-merge never reads it (it needs `CORE_AUTOMERGE` and the
byte-for-byte check, then the required checks). The workflow runs from `main` only: a manual run started on another branch stops at the first step of each
job with an error naming the branch. Both tags are refused unless they are `v<major>.<minor>.<patch>`
(the pin may also be `v<version>-seed`), and later bumps move the pin with an exact replacement
(`adopt_core_wheel.py --bump`), not a `sed` script, so a hostile tag cannot run a command.

What was prepared in this repository so that pull request passes without touching a workflow (the App token cannot
change files under `.github/workflows`):

- `scripts/check-catalog.py` reads the catalog the installed engine loads, so it works with the seed's `catalog/` and
  with the wheel's `catalog_data`; it now prints the new `cost-evidence` checks properly, and `--write-schema` writes only
  the seed's catalog under `packages/` and refuses an installed release (in `site-packages`, even inside this
  repository's `.venv`).
- `tests/unit/test_api.py` compares the health route's catalog version with the installed catalog's (`1.0.0` now,
  `1.1.0` after), instead of a fixed `1.0.0`.
- `tests/security/test_edition_boundary.py` scans the installed engine's files wherever they are (it also reads the
  engine's declared requirements), and skips the seed's manifest once the seed is gone.
- `pyproject.toml` sets `[tool.hatch.metadata] allow-direct-references = true`, without which hatchling refuses to
  build this project once its dependency is a URL.
- `security.yml` exports the audit set with `--no-emit-package cloud-assessor-core`: `pip-audit --strict` fails on a
  package it cannot find on PyPI, and the engine wheel is not on PyPI (the seed was left out by `--no-emit-workspace`
  for the same reason).
- `ci.yml` and the `Makefile` pass `--cov=packages` only while `packages/cloud-assessor-core/pyproject.toml` exists (a
  tracked file, not the folder: ignored `__pycache__` folders keep `packages/` alive in a working copy after a pull).
- `tests/unit/test_adopt_core_wheel.py` runs the script and the workflow's own steps (the tag check, the bump, the
  artifact check of the `pull-request` job) against copies of the real files and against hostile tags and tampered
  artifacts, in every pull request, so a later edit that would break them fails here first.
- `tests/security/test_edition_boundary.py` forbids the engine, wherever it is installed, to import a network module
  (`urllib.request`, `http.client`, `socket`, `ssl`, `httpx`, `requests`, `aiohttp`), since it now comes from outside.

Left for after the adoption merges (documents only): `README.md`'s layout table and diagram, `.github/CODEOWNERS`,
`.github/pull_request_template.md`, `NOTICE` and `SECURITY.md` still name `packages/cloud-assessor-core`; the table
above and this section should then name the bump pull request and its merge commit.

**Observable differences after the adoption.** `/api/health` reports catalog `1.1.0`; `report.json` reports
`core_version` `0.2.1` and gains two keys, `edition` and `scope`, both `null` because the lab passes neither (passing
`edition="lab"` needs engine `0.2.0` or later, so it can only come after the adoption). Findings, scores and coverage for
both fictional samples are identical between the seed and `0.2.1` (compared on 2026-10-31, `VALIDATION.md`).

## Entries, newest first

### 2026-10-31: adoption of `v0.2.1` handed to `core-update.yml` (this repository's branch `chore/adopt-core-v0.2.1`)

Read upstream between the seed (`0.1.0`) and `v0.2.1` from a clone of the App at tag `v0.2.1` (`55b7242`): its
`CHANGELOG.md` and a `diff -r` of `packages/cloud-assessor-core` against the seed. **Reaches this repository: yes**, as
described in "Adopting `v0.2.1`" above. Nothing in the engine's API that this edition calls was renamed or removed:
`evaluate()` and `assess()` gained keyword arguments with defaults (`evidence`, `edition`, `scope`), `Assessment` gained
two optional fields, `CheckKind` gained `cost-evidence`, and `redaction.ALLOWED_WORDS` only grew. A wheel built from
the tag with `uv build` has the same sha256 as the release asset (`6c5564ba…26e7`), and that wheel, served locally, was
used to run the adoption end to end in a throwaway copy (results in `VALIDATION.md`).

### 2026-10-24: documents corrected, and this file started (App [#40](https://github.com/saulpatinojr/HCW-CloudAssessor_App/pull/40), merged as `e22603c`; this repository's [#27](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/27))

The App's README said no release existed and told readers to install `@v0.1.0` (a tag that was never created), and its
`REVIEW.md` said the repository had no license and was private. Both are corrected. This repository's `CLAUDE.md`,
`AGENTS.md`, `README.md`, `CONTRIBUTING.md`, the pull request template and `docs/README.md` said the engine was still "edited
here, moving upstream"; they now say the App owns it and the seed is awaiting adoption.
**Reaches this repository: documents only.** Action: none. **Left alone:** `ADR-0001` (a historical record; its
"edited here until the App adopts it" wording is superseded by this file) and `packages/cloud-assessor-core/README.md`, which the App
holds as an identical copy.

### 2026-10-24: the App's lockfile check now fails on a stale `uv.lock` (App [#38](https://github.com/saulpatinojr/HCW-CloudAssessor_App/pull/38), ticket [#27](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/27))

The App's `scripts/check-lockfiles.sh` used to re-lock silently, so it never noticed a stale `uv.lock`; it now runs
`uv lock --check` and exports with `--locked`. **Reaches this repository: no.** This repository has no committed export;
its `ci.yml` already runs `uv lock --check` (line 40), and `uv lock --check` passes here today. The one difference is that
CI installs with `uv sync --frozen`, which does not itself check freshness (the separate `uv lock --check` step does).

### 2026-10-24: release-workflow inputs hardened in the App (App [#37](https://github.com/saulpatinojr/HCW-CloudAssessor_App/pull/37), ticket [#34](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/34))

In the App's `release.yml` and `publish-images.yml`, the tag, image digest and image version now reach shell scripts as
quoted environment variables instead of being pasted into the script. **Reaches this repository: the same pattern exists
here, at low risk.** `.github/workflows/publish-images.yml`, step "Record the immutable digest for the website's group_vars",
pastes `${{ steps.build.outputs.digest }}` and `${{ steps.version.outputs.version }}` into a `run:` script (two `echo` lines).
Action (optional, workflow-only): pass both through `env:` and quote them. `core-update.yml` and the `with:` inputs are fine.

### 2026-10-24: lock refresh and `CLAUDE.md` in the App (App [#23](https://github.com/saulpatinojr/HCW-CloudAssessor_App/pull/23))

`certifi` moved to `2026.10.23` in the App's locks (advisory PYSEC-2026-4320, fixed in `2026.10.19`); `fastapi` and `ruff` were
brought in line with their pins; `CLAUDE.md` was added and allow-listed by the App's documentation check.
**Reaches this repository: no.** This repository's `uv.lock` already has `certifi` `2026.10.19` (the fixed version), `ruff` `0.17.1`
and `fastapi` `0.150.0`. Action: none. On 2026-10-24 the App's Python base image tag was `python:3.14.8-slim-trixie`, the same tag this repository used then (digests were not compared). This repository's base now follows the website's pin by itself (`base-update.yml`), so read `infrastructure/docker/versions.env` for the current one.

### 2026-10-24: access controls on the App (App [#36](https://github.com/saulpatinojr/HCW-CloudAssessor_App/pull/36), ticket [#25](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/25))

The App gained an owner-approved `repository-admin` workflow (dry run unless "apply" is ticked, approved per run) and used it
to create the two rulesets listed in the table above. **Reaches this repository: indirectly.** Because `v*` tags in the App cannot
be moved or deleted, a wheel URL pinned by tag stays valid. Action: none.

### 2026-10-18 and 2026-10-12: releases `v0.2.1` and `v0.2.0`

See "What upstream changed in the engine" above.

## Open upstream decisions that affect this repository

These belong to the owner; none is decided yet.

| Decision | Why it matters here | Where |
|---|---|---|
| Versioning policy: does the App follow the engine or version separately? | Decides the shape of the tag this repository pins (`CORE_REF v<version>`), and what `/api/health` should report upstream. | App [#33](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/33) |
| License and visibility confirmation (MIT file present, repository public) | This repository carries the same MIT license and `[REVIEW REQUIRED]` attribution wording. | App [#31](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/31), `REVIEW.md` R-003 |
| Caller authentication for the appliance | The appliance only; the lab edition has no sign-in and is unaffected, but its pane protocol is shared. | App [#26](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/26) |
| Dependabot in the App uses the `pip` ecosystem and cannot update `uv.lock` | This repository already moved to `uv` (see its `CHANGELOG.md`); the App has not decided to follow. | App [#29](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/29) |
| Secret-scan allow-list for prose in the App's plan document | App-only. | App [#30](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/30) |
| Contribution guide and issue forms in the App | This repository already has `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` and `SECURITY.md`. | App [#32](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/32) |
| When to adopt `v0.2.1` here | Needs the owner's go-ahead for the pull request above. The program's checklist (App issue [#9](https://github.com/saulpatinojr/HCW-CloudAssessor_App/issues/9)) still talks about tagging an App `v0.1.0`; that is out of date. | this file |
