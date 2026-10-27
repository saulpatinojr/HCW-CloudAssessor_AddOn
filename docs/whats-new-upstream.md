# What is new upstream (HCW-CloudAssessor_App)

**How to use this file.** The Cloud Assessor engine is written and released in
[`HCW-CloudAssessor_App`](https://github.com/saulpatinojr/HCW-CloudAssessor_App), and this lab edition adopts it. Read
this file before you change behaviour here, so you know what upstream already did and what is still waiting to be adopted,
and add an entry (newest first) whenever you adopt an upstream change or find that one reaches this repository.

Last updated: 2026-10-24, from the App's `main` at commit `e22603c` (its pull request #40, documents only; the last change
that touched the engine, workflows or locks is #38 at `5a7ed0b`). Everything below was checked against GitHub and the two
repositories on that date; where something was not checked, it says so.

## Current upstream state

| Question | Answer |
|---|---|
| Who owns the engine? | The App. It was seeded here (`ADR-0001`), the App adopted it unchanged, and since then engine and catalog changes are made upstream, released, and adopted here. Do not edit `packages/cloud-assessor-core` in this repository. |
| Latest App releases | [`v0.2.1`](https://github.com/saulpatinojr/HCW-CloudAssessor_App/releases/tag/v0.2.1) (2026-10-18, tag commit `55b7242`) and [`v0.2.0`](https://github.com/saulpatinojr/HCW-CloudAssessor_App/releases/tag/v0.2.0) (2026-10-12, tag commit `6821e30`). There is no `v0.1.0` tag in the App. |
| Engine wheel to pin | `cloud_assessor_core-0.2.1-py3-none-any.whl` from the `v0.2.1` release. sha256 `6c5564ba0bc82c79060704dd52871e56b51b709c9ee8bdd7b6b7cf0409ca26e7` (downloaded and hashed; it matches the digest GitHub shows). The `v0.2.0` wheel is `31fde826a3ff0dccfcaee084a00e86df83e28473567dfdb75ad74319425bc638` (digest as GitHub shows it; not downloaded). |
| What this repository has | The original seed, engine `0.1.0`, catalog `1.0.0`, under `packages/cloud-assessor-core` (a workspace member). `pyproject.toml` has **no** `CORE_REF` line, so `core-update.yml` is inert ("the engine seed is still local"). |
| Drift | This repository is behind by two releases. Neither has been adopted. |
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

### Action for this repository: adopt `v0.2.1`

This is a code and dependency change, so it needs its own pull request, reviewed by the owner (it is not part of the
documentation pass that created this file). Steps, in order:

1. `pyproject.toml`: replace the dependency `"cloud-assessor-core"` with
   `"cloud-assessor-core @ https://github.com/saulpatinojr/HCW-CloudAssessor_App/releases/download/v0.2.1/cloud_assessor_core-0.2.1-py3-none-any.whl",  # CORE_REF v0.2.1`
   on one line; remove the `[tool.uv] workspace` and `[tool.uv.sources]` entries; remove the seed from `testpaths` and from `[tool.coverage.run] source`.
2. `uv lock` (it records the wheel's sha256; the image's `pip install --require-hashes` keeps verifying it). Never edit `uv.lock` by hand.
3. Delete `packages/cloud-assessor-core/`.
4. `infrastructure/docker/Dockerfile`: delete the two `COPY packages/cloud-assessor-core/...` lines (28 and 29); the wheel carries the catalog as `cloud_assessor_core/catalog_data`.
5. Things that still point at the seed folder and will break: `scripts/check-catalog.py` (`CATALOG_DIR`), `tests/security/test_edition_boundary.py` (line 24 reads the seed's `pyproject.toml`), `ruff.toml` (the seed-tests ignore), `repository.manifest.json` (seed file list). Point the first at the installed package's `catalog_data`, and drop the rest.
6. `make rules-doc`, then change the catalog version pin in `tests/unit/test_api.py` from `1.0.0` to `1.1.0`.
7. Update `VALIDATION.md` and `CHANGELOG.md`, and the README relationship text (it already says the seed is deleted at adoption).
8. Run `uv sync --frozen --all-packages`, `uv run ruff check . && uv run ruff format --check .`, `uv run python scripts/check-catalog.py`, `uv run pytest -q --cov=packages --cov=src` and `make e2e`; CI also builds the image and proves `import azure` fails inside it.

After that, `core-update.yml` has a `CORE_REF` to compare and will open the pull request for every later release.

## Entries, newest first

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
