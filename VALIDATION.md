# Validation

What was executed for this edition and what was not, per run. "Here" is the authoring container (no Docker daemon, PyPI
and the Playwright CDN reachable through a proxy). Dates are the run date.

## Run 2026-10-27 (release 0.1.1 prepared)

Toolchain: Python 3.14.6 (`.python-version`), uv 0.12.0 locally (CI uses uv 0.11.32, which was not run here), environment from
`uv sync --frozen --all-packages`, on a Windows 11 workstation. This run prepares the version bump only: nothing in `src/`,
`web/`, `samples/` or `docs/api/` changed since `v0.1.0` (`git diff v0.1.0 origin/main` over them is empty). No image was built
and no workflow was run for it.

| Check | Executed here | Result |
| --- | --- | --- |
| The lab application's version in every place that states it: `pyproject.toml`, `uv.lock` (the `cloud-assessment-lab` entry only), `__version__`, `repository.manifest.json` and the two sample lines in `docs/operations/runbook.md` | yes | all `0.1.1`. `uv lock` also rewrote the `revision = 5` line of `uv.lock` to `3`; that line was put back by hand so the lock file differs in one line. The engine seed (`packages/cloud-assessor-core`, its `__version__`, its tests, and the `cloud-assessor-core` entry in `uv.lock`) stays `0.1.0` on purpose |
| `docs/api/openapi.yaml`, `info.version` | decided, not changed | stays `0.1.0`. The OpenAPI Specification defines that field as the version of the API document, "distinct from the OpenAPI Specification version or the API implementation version" ([Info Object](https://spec.openapis.org/oas/v3.1.0#info-object)); the document is unchanged since `v0.1.0`; no test ties it to `__version__`; the Migrate AddOn keeps API document `0.3.0` beside release `0.3.2` |
| `uv lock --check` | yes | exit 0 |
| `uv run ruff check .` and `uv run ruff format --check .` | yes | clean (88 files) |
| `uv run pytest -q --cov=packages --cov=src --cov-fail-under=85` | yes | 336 passed, coverage 98.12% (gate 85) |
| `/api/health` and `X-Addon-Version` read `__version__` | yes | `tests/unit/test_api.py` asserts both equal `__version__`; `tests/end_to_end/test_repository_manifest.py` holds `__version__` to `pyproject.toml` and `repository.manifest.json`; a request to the app in the same process printed health `0.1.1` and header `0.1.1` |
| `uv run python scripts/check-catalog.py`, and its `--doc` output against `docs/rules/catalog.md` | yes | catalog 1.0.0, 25 criteria, 25 links marked `[VERIFY]`; no drift |
| The website's `scripts/addons/check-guide-drift.mjs` (the script `guide-drift.yml` runs), on this branch's guide and the website's `main` data | yes, locally | "in step: 13 fields compared". The guide is not touched by this change |
| Docker image build, the in-image boundary checks, Trivy, and the licence label on a built image | **no**, CI only | no image was built here; the `image` job of `ci.yml` builds one and checks the label on the pull request |
| `publish-images.yml` dry run on `main` | **no** | not part of this change. This repository's gate step does not check for a `v*` tag (the Cloud Crawler's does, since its [pull request 18](https://github.com/saulpatinojr/HCW-CloudCrawler_AddOn/pull/18), which says a manual run there reached the Docker login and failed because the connection trusts tags only). What a manual run does here has not been observed |
| Push, provenance, SBOM, attestation and digest of `v0.1.1`; the label on the Docker Hub tag | **no** | only the tag `v0.1.1` publishes, and it is the owner's call ([issue 47](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/issues/47)) |
| The live lab host | **no** | the status route still reported version `0.1.0` on 2026-10-27, as expected until the website pins a new digest |

## Upstream adoption trial 2026-10-24 (nothing in this repository changed)

Question: would the App's engine `0.2.1` (release `v0.2.1`) work in this edition? Method: a throwaway copy of this repository with `packages/cloud-assessor-core` replaced by the App's `packages/cloud-assessor-core` at `5a7ed0b` (engine `0.2.1`, catalog `1.1.0`), `uv sync --all-packages`, then `pytest` over `tests/unit`, `tests/security`, `tests/contract`, `tests/end_to_end` and the engine's own tests. Python 3.14.6, uv 0.11.32.

| Check | Executed here | Result |
|---|---|---|
| Tests with the App's engine swapped in | yes | 160 passed, 1 failed: `tests/unit/test_api.py::test_health_is_flat_and_complete` pins the catalog version at `1.0.0`; the engine reports `1.1.0` (stale test value) |
| `uv run python scripts/check-catalog.py` with the App's engine | yes | catalog 1.1.0, 25 criteria, 25 reference links marked `[VERIFY]` |
| `make rules-doc` with the App's engine | yes | `docs/rules/catalog.md` changes by 6 lines |
| `uv lock --check` on this repository as it is | yes | exit 0 |
| Playwright e2e (`make e2e`) with the App's engine | **no** | not run in the trial |
| Docker image build with the App's engine | **no**, CI only | no daemon here |
| Install of the `v0.2.1` wheel by URL with `pip` on Python 3.14 | yes | installs; `cloud_assessor_core.__version__` is `0.2.1`; the downloaded wheel's sha256 is `6c5564ba0bc82c79060704dd52871e56b51b709c9ee8bdd7b6b7cf0409ca26e7`, matching GitHub's digest |

Limitation: `uv pip install` of the same URL failed with a 401 on the download redirect inside the authoring sandbox (its proxy); `pip` and `curl` worked. The adoption steps are in `docs/whats-new-upstream.md`.

## Run 2026-10-10 (0.1.0, initial)

Toolchain: Python 3.14.6 (`uv python pin 3.14.6`), uv 0.11.32, Node 26.11.1 (for Playwright only), chromium 1243
(`playwright@1.63.0`). Resolved pins: fastapi 0.143.0, uvicorn 0.54.0, pydantic 2.14.0 (pydantic-core 2.50.0,
starlette 1.7.0, anyio 4.15.1, h11 0.16.0, click 8.5.0, idna 3.20, annotated-types 0.8.0, annotated-doc 0.0.5,
opentelemetry-api 1.45.1, typing-extensions 4.16.0, typing-inspection 0.4.4); dev pytest 9.1.1, pytest-cov 7.1.0,
ruff 0.17.0, httpx 0.28.1, pip-audit 2.10.1; build hatchling 1.32.4. `uv.lock` and `requirements.lock.txt`
(`uv export --format requirements-txt --no-dev --no-emit-project --no-emit-workspace --no-header`; hashes are on by
default) are committed; 14 third-party runtime packages, none Azure. Since 2026-10-16 the export is not committed:
the image build runs it from `uv.lock` (see `infrastructure/README.md`), and CI checks `uv lock --check`.

| Check | Executed here | Result |
|---|---|---|
| `uv sync --all-packages` | yes | 52 packages resolved and installed |
| `uv run ruff check . && uv run ruff format --check .` | yes | clean (82 files) |
| `uv run python scripts/check-catalog.py` | yes | catalog 1.0.0, 25 criteria, 25 reference links marked `[VERIFY]`; `schema.json` in sync; `docs/rules/catalog.md` in sync |
| `uv run pytest -q --cov=packages --cov=src --cov-report=term-missing` | yes | 151 tests passed; coverage 98% (2,224 statements, 36 missed; gate 85). `__main__.py` is covered only by its subprocess tests, which coverage does not trace |
| `uv run pytest tests/security tests/contract -q` | yes | 16 passed (edition boundary incl. fresh-process refusal, no secrets, content-free logs, OpenAPI two-way) |
| Live server: `CA_ALLOW_NO_TURNSTILE=1 PORT=8080 uv run python -m cloud_assessment_lab`, `GET /api/health`, `POST /api/assessments` with `samples/sample-resource-graph.json`, `GET …/report.md`, `GET …/bundle.zip`, wrong token, `DELETE`, after-delete, `GET /` | yes | health `ok:true id:cloud-assessment version:0.1.0 edition:lab`, headers `X-Addon-Id`, `X-Addon-Version`, CSP with `frame-ancestors 'none'`, `X-Frame-Options: DENY`, `Cache-Control: no-store`; 201 with 40 resources / 95 findings; report.md 200 (10,480 B); bundle.zip 200 (151,756 B); wrong token 404; `{"deleted":true}`; 404 after delete; index 200. Log lines carried only counts, flags and event names |
| `IDENTITY_ENDPOINT=http://169.254.169.254 uv run python -c "import cloud_assessment_lab.app"` | yes | exit 1 with `EditionBoundaryError: refusing to start: identity environment present (IDENTITY_ENDPOINT)`; `python -m cloud_assessment_lab` under `MSI_ENDPOINT` exits 3 with one scrubbed `startup_refused` line |
| `uv run pip-audit -r requirements.lock.txt --strict` | yes | no known vulnerabilities |
| Playwright e2e (`npx playwright test -c tests/e2e/playwright.config.ts`, chromium) | yes | 4 passed: standalone journey (sample, scorecard, filters, detail, copy report, download, delete); vendor-name scan; framed pane under the site's sandbox posting `loading, ready, working, ready` to the host origin, dark theme by `?theme=dark`; headers and health |
| `bash scripts/package-repository.sh` | yes | `hcw-cloudassessor-addon.zip` (220 KB); archive file set equals `git ls-files`; no excluded path leaked |
| `git status --short \| wc -l` | yes | 29 top-level entries (137 files, all untracked: initial commit pending; the parent commits) |
| Docker image build (`infrastructure/docker/Dockerfile`) | **no**, CI only | no daemon here; `publish-images.yml` builds, proves `import azure` fails and the container exits under `IDENTITY_ENDPOINT`, runs the hardened health check, scans with Trivy, and pushes only when `DOCKERHUB_ENABLED` is `true` |
| Trivy scan, SBOM, provenance, attestation | **no**, CI only | as above |
| `versions.env` vs every `FROM` | locally by the same shell snippet as `ci.yml`; CI | both `FROM` lines equal `BASE_IMAGE@BASE_DIGEST` |
| Human verification against the real siteverify endpoint | **no** | mocked in `tests/unit/test_api.py` and `test_security_modules.py`; the real call needs the owner's widget and secret (`docs/deployment/lab-host.md`) |
| Lab-host deployment, Caddy route, website pane | **no** | owner steps and the website PR (Phase 6); the catalogue row stays `coming` until the digest exists |
| CodeQL, gitleaks, dependency-review | **no**, CI only | `security.yml` |

## Limitations recorded

- An export shows configuration only: spend, budgets, role assignments, diagnostic settings, policy state, Defender
  plans and traffic are `unknown` by design (the panel and `report.md` say so; coverage, never score, reflects it).
- `CA-FIN-003`, `CA-FIN-007`, `CA-ZT-011` and `CA-FIN-002` are estate-level criteria: one finding each, so the sample
  cannot show both a pass and a fail for them (pinned as such in `test_samples_expected.py`).
- The portal "All resources" CSV maps the display names of the 19 types in the sample to ARM types; other display
  names stay as written and match no criterion (they are counted, not assessed).
- Every `learnUrl` is the most plausible page on `learn.microsoft.com` or `www.finops.org` as of 2026-10-10 and is
  marked `[VERIFY]` (`verify: true`) until the owner confirms it; the attribution wording is `[REVIEW REQUIRED]` (R-005);
  the MIT license is `[REVIEW REQUIRED]` (R-003 upstream undecided); the `downloads` sandbox capability is
  `[REVIEW REQUIRED]` on the website side; the base-image digest is `[VERIFY]` at the first image build.
- The 5 MB cap stops reading at the limit and answers 413; the socket close past the limit is uvicorn's behaviour on an
  unread body and was observed only through the test client, not with a raw socket.
- First-party packages are copied into the image as source trees rather than built as wheels (no build backend in
  the image); `importlib.metadata` therefore does not know them, and the version comes from `__version__` (asserted
  equal to `pyproject.toml` and `repository.manifest.json` by a test).
- starlette 1.7 prefers `httpx2` for its test client; this edition pins `httpx` (the brief) and mutes that one
  deprecation notice in `pyproject.toml`.
- `core-update.yml` is inert until `HCW-CloudAssessor_App` publishes a release and this repository pins
  `cloud-assessor-core` by git tag (ADR-0001).
- When it is not inert, `core-update.yml` opens the pull request with a GitHub App token (the HCW Main Admin App: its client ID is the repository variable
  `HCW_MAIN_ADMIN_CLIENT_ID`, its private key the repository secret `HCW_MAIN_ADMIN_PRIVATE_KEY`), not `GITHUB_TOKEN`, so the required checks run on the pull request itself. That path is covered by
  `tests/security/test_core_update_app_token.py` (static) and was linted with actionlint and zizmor; it has not yet opened
  a real bump pull request here. To prove the credential while the workflow is inert:
  `gh workflow run core-update.yml -R saulpatinojr/HCW-CloudAssessor_AddOn --ref main -f probe=true`.
  The App key lives only as the repository secret `HCW_MAIN_ADMIN_PRIVATE_KEY` and is never printed. To rotate it,
  generate a new private key on the settings page of the App (https://github.com/settings/apps), replace the secret in every repository that holds the key (this one:
  https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/settings/secrets/actions; the App is installed on the four
  add-on repositories, so check the other three), then delete the old key on the settings page of the App.
  The settings page can hold several keys, so a separate key per repository lets you revoke one without
  touching the others.
- Auto-merge of a compatible bump needs the repository setting "Allow auto-merge", which was off on 2026-10-26 (UTC) and has since been turned on.
  With it off, `core-update` warns and leaves the pull request for a person to merge.
- `base-update.yml` moves the base image pin to the website's pin by opening a pull request, with the same HCW Main Admin App credential as
  `core-update.yml` (so `core-update.yml`'s probe run also proves the credential here). It is covered by
  `tests/security/test_base_update_workflow.py` (static checks of the workflow text, and its two decision scripts run against stand-ins for
  `docker` and `gh`), `tests/unit/test_follow_website_base.py` (the script, including hostile website content) and
  `tests/unit/test_base_image_pin.py` (fails when `versions.env` and a `FROM` line disagree), and it was linted with actionlint.
  **Proved on GitHub on 2026-10-27** with the proof in `docs/operations/runbook.md`, "Keeping the base image on the website's pin": a throwaway
  branch (`proof/base-update`, deleted afterwards) with the pin set one release back, so nothing on `main` was touched.
  - Run [40488729010](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/actions/runs/40488729010): `plan` and `open-pr` both green. The plan
    printed `changed=true`, old `sha256:a2b82f3c…`, new `sha256:fbecd461…`, and the new digest's platforms included `linux/386` and `linux/s390x`
    (so the registry check works with the runner's own `docker buildx`). The App token was minted and pull request
    [#55](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/55) was opened by `app/hcw-main-admin`, ready for review, with the
    "platforms compared" box ticked. Its commit is credited to `hcw-main-admin[bot]`. The repository's checks (`lint`, `test`, `image`,
    `catalog-check`, `package`, `e2e`, CodeQL, `pip-audit`, `secret-scan`, `dependency-review`) ran on that pull request and all passed, which is
    what the App token is for.
  - Run [40490178354](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/actions/runs/40490178354): with a commit a person had pushed to
    `base-update/website-base`, the run logged that the pull request was left alone, `open-pr` was skipped, and the person's commit stayed the last
    commit on the branch.
  - Run [40493622020](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/actions/runs/40493622020): after the throwaway branch went back to the
    website's pin, the run logged that the pull request was obsolete, `open-pr` succeeded, and pull request
    [#58](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/58) ended closed (not merged) with `base-update/website-base` deleted
    (`create-pull-request` with `delete-branch: true`).
  - The workflow's pull request asks the repository owner for a review (`CODEOWNERS` names the owner for every path), so a proof pull request looks like any other. Two of them (#55 and #57)
    were merged into the throwaway branch by the owner's account, about ten minutes after they opened, before the next step could use them; nothing
    on `main` was affected. The runbook now says to run steps 7 to 11 straight after step 5.
  Still unverified: whether the ruleset "Protect main" option "require extra approval for unattributed changes" asks for an approval on a pull
  request into `main` (the proof's pull requests went into the throwaway branch, which that ruleset does not govern; it is read from the first real
  pull request); the first scheduled run (the daily trigger, 07:37 UTC); what happens when the website moves again while a pull request holds a
  person's commit (only the "left alone" half was seen live); and the runner's own Python version (the script ran, so it is compatible, but the version
  was not read). Scheduled workflows in a public repository are switched off by GitHub after 60 days without repository activity. That switches off
  `base-update` and the weekly `base-follows-website` job together, so after a quiet spell the weekly job is not an independent second
  check. How to see whether either has been switched off, and how to switch them back on, is in `docs/operations/runbook.md`, "If the
  daily run goes quiet".
