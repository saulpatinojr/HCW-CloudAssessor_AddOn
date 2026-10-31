# Validation

What was executed for this edition and what was not, per run. "Here" is the authoring container (no Docker daemon, PyPI
and the Playwright CDN reachable through a proxy). Dates are the run date.

## Run 2026-10-31, second round (review fixes: two-job split, tag check, exact bump)

Same toolchain as the run below. After an independent review of pull request 67 (head `36251c8`). The wheel was again
built from the App's tag `v0.2.1` and served on `127.0.0.1` for the simulation.

| Check | Executed here | Result |
| --- | --- | --- |
| `uv sync --all-packages`, `uv run ruff check . && uv run ruff format --check .` | yes | clean (90 files) |
| `uv run python scripts/check-catalog.py`, `--doc` drift, `uv lock --check` | yes | catalog 1.0.0, 25 criteria; no drift; exit 0 |
| `uv run pytest -q --cov=packages --cov=src` | yes | 396 passed, coverage 98.12% (gate 85) |
| The refs step's script as written, fed hostile tags through `inputs.ref` and through a stand-in `gh` (`v9\|;etouch${IFS}PWNED;#`, a tag with a newline, `v1.0`, `v1.0.0-rc.1`, and others) | yes (in the tests) | each refused with exit 1, nothing written to `GITHUB_OUTPUT`, no `PWNED` file; a plain `v99.0.0` passes |
| `adopt_core_wheel.py --bump` with the same hostile tags | yes (in the tests) | refused, `pyproject.toml` unchanged; a plain bump moves the URL and the marker |
| The `pull-request` job's apply step as written, against a stand-in checkout and artifact | yes (in the tests) | takes the expected bump; refuses an extra file, a deletion outside the seed, a `..` path, a deletion of an untracked path, a symbolic link, an extra artifact entry, a malformed or missing outcome and a malformed tag, each with the checkout left unchanged |
| A step that runs project code added to the `pull-request` job | yes (a temporary edit, reverted) | `test_the_job_that_holds_the_key_runs_no_project_code` fails |
| `import socket` appended to the installed engine (the `0.2.1` wheel in the simulation's `.venv`, reverted after) | yes | `test_the_engine_opens_no_network_connection` fails with `paths.py: socket`; passes again once removed |
| `check-catalog.py --write-schema` with the wheel installed in the in-project `.venv` | yes | exit 1, "belongs to the installed engine release"; the installed `schema.json` is untouched. With the seed it rewrites the seed's file with no change |
| Simulation, both jobs: the bump by hand, then the `bump` job's collect step, then the `pull-request` job's apply step in a fresh clone | yes | the artifact holds the five files, 39 deletions and `success`; the applied clone is identical to the `bump` job's tree (outside ignored folders) |
| Simulation: the applied clone with an ignored `__pycache__` left under `packages/cloud-assessor-core` | yes | coverage flags pick `--cov=src` only (`ci.yml` and `make -n test`); ruff, catalog 1.1.0, drift, `uv lock --check` clean; pytest 311 passed, 9 skipped, 1 failed (the bump test, only because the simulated URL is `127.0.0.1`; with the release URL form, 120 of 120 run tests pass in the touched files); Playwright 4 passed; `pip-audit --strict` on the `security.yml` export: no known vulnerabilities |
| Third round (Copilot's review of `2a2d3ed`): the `pull-request` job's regenerate-and-compare step as written, with real uv, in a clean clone, against the artifact from the simulation (wheel URL pointed at the local server in that clone's copy of the script) | yes | exit 0; the regenerated `pyproject.toml`, `uv.lock`, Dockerfile, `.dockerignore` and 39 deletions are byte-identical to the artifact's; `outcome=success` |
| The same with one changed line in the artifact's `pyproject.toml` | yes | exit 1, `pyproject.toml in the artifact differs from the one regenerated here`; the checkout is left clean |
| `uv lock --no-build -v` for the first adoption | yes | `Found static pyproject.toml for: cloud-assessment-lab`; nothing built; the wheel's metadata read from the wheel; the lock is identical to the one plain `uv lock` wrote |
| uv by hash: `pip download --require-hashes` of `uv==0.11.32 --hash=sha256:3da76cd4…a6c4` | yes | the manylinux x86_64 wheel downloads and matches (hash from PyPI's JSON for 0.11.32) |
| The apply step against tampered artifacts in the tests (stand-in uv, real script and real collect step): an extra line in `pyproject.toml`, a changed `uv.lock`, an edited Dockerfile, a non-seed deletion, a dropped seed deletion, HTML, a control character, a wrong heading or 300 KB in `catalog.md`, plus the earlier cases | yes | each refused with exit 1, nothing written to `GITHUB_OUTPUT`, checkout unchanged; the untampered artifact is taken |
| `uv run pytest -q --cov=packages --cov=src` at the third round | yes | 404 passed, coverage 98.12% |
| actionlint | **no** | not re-run (running a downloaded linter was not allowed in this session) |
| The two jobs on GitHub, the artifact hand-over, the bump pull request and auto-merge | **no** | GitHub only, after merge |

## Run 2026-10-31 (adoption of engine `v0.2.1` handed to `core-update.yml`)

Toolchain: Python 3.14.6 (`.python-version`), uv 0.11.32 (the version CI uses), Docker 29.9.2 with a daemon, Playwright
1.63.0 with its preinstalled chromium, on the authoring container. The release asset itself could not be downloaded
here, so the wheel was built from a clone of the App at tag `v0.2.1` (`55b7242`) with `uv build`; its sha256,
`6c5564ba0bc82c79060704dd52871e56b51b709c9ee8bdd7b6b7cf0409ca26e7`, is the release asset's (recorded on 2026-10-24 in
`docs/whats-new-upstream.md`). "Simulation" below is a throwaway copy of the branch in which the workflow's bump step
was run by hand, with the wheel served on `127.0.0.1` and passed with `--wheel-url` (the only difference from the run on
GitHub, which uses the release URL).

| Check | Executed here | Result |
| --- | --- | --- |
| `uv sync --all-packages` (branch, seed) | yes | resolved, 51 packages checked |
| `uv run ruff check . && uv run ruff format --check .` | yes | clean (90 files) |
| `uv run python scripts/check-catalog.py`, and `--doc` against `docs/rules/catalog.md` | yes | catalog 1.0.0, 25 criteria, 25 `[VERIFY]`; no drift |
| `uv lock --check` | yes | exit 0 (the `allow-direct-references` setting does not change the lock) |
| `uv run pytest -q --cov=packages --cov=src` | yes | 348 passed, coverage 98.12% (gate 85) |
| `make e2e` | **no, as written**: here `npx --yes playwright@1.63.0` resolves a global Playwright that cannot load `@playwright/test` | the CI way instead (`npm install --no-save @playwright/test@1.63.0`, `CI=1 npx playwright test -c tests/e2e/playwright.config.ts`): 4 passed |
| Image build (branch, seed), then the `image` job's steps from `ci.yml` | yes, with one local-only change: the proxy's CA certificate copied into the build stage for `pip` | built; `import azure` fails; fastapi, pydantic and uvicorn import; `Python 3.14.8` equals `BASE_PYTHON_VERSION=3.14.8`; licence label `MIT` |
| The new Python check with `BASE_PYTHON_VERSION=3.14.7` in a copy of `versions.env` | yes | fails as intended: `the image runs 'Python 3.14.8', versions.env says BASE_PYTHON_VERSION=3.14.7` |
| Simulation: the bump step (`adopt_core_wheel.py`, `git rm -r`, `uv lock`, `uv sync --frozen`, `--doc`) | yes | three files rewritten; `uv.lock` gains `cloud-assessor-core 0.2.1` with hash `sha256:6c5564ba…26e7`; 12 lines of `docs/rules/catalog.md` change |
| Simulation: what `create-pull-request` commits (`git add --` the five add-paths, then `git commit`) | yes | one commit with the five files and the seed's deletion (44 files); the untracked `package.json` from the e2e install is left out |
| Simulation: ruff, `check-catalog.py`, `--doc` drift, `uv lock --check` | yes | clean; catalog 1.1.0, 25 criteria; no drift |
| Simulation: `pytest` with the coverage line `ci.yml` now runs | yes | 263 passed, 9 skipped (the seed-only tests), 1 failed: the sed test, only because the simulated URL is `127.0.0.1` rather than `github.com/.../releases/download/`; with the URL put in the release form it passes. Coverage 96.01% |
| Simulation: Playwright e2e | yes | 4 passed |
| Simulation: image build with the wheel, then the `image` job's steps | yes (build network `host` to reach the local server) | pip installs `cloud-assessor-core-0.2.1` from the lock with `--require-hashes`; no cloud SDK in `/install`; all checks pass; the container answers `/api/health` with catalog `1.1.0` |
| Simulation: `pip-audit --strict` on the export with and without `--no-emit-package cloud-assessor-core` | yes | without it: exit 1, `Dependency not found on PyPI and could not be audited: cloud-assessor-core (0.2.1)`; with it: `No known vulnerabilities found` |
| Findings and scores for both fictional samples, seed against `0.2.1` (`report.json` through the API) | yes | identical; only `catalog_version`, `core_version`, `created_at` and the two new `null` keys `edition` and `scope` differ |
| actionlint on `ci.yml`, `core-update.yml`, `security.yml` | partly | one run printed only the known `ubuntu-26.04` runner-label notice in the part shown; a filtered re-run was not allowed in this session, so a clean result is not claimed |
| The real `core-update.yml` run, the bump pull request, its required checks and auto-merge | **no** | GitHub only, after this pull request merges: the next scheduled run (minute 41 of hours 0, 6, 12, 18 UTC) or `gh workflow run core-update.yml -R saulpatinojr/HCW-CloudAssessor_AddOn --ref main` |

## Run 2026-10-27 (release 0.1.1 published)

Run on GitHub after the owner said yes to the tag ([issue 47](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/issues/47)).
Nothing in the application changed; this records the dry run, the tag and what the registry shows.

| Check | Result |
| --- | --- |
| The gate step of `publish-images.yml` for a manual run, its own shell run with the repository variables set as they are | **Before** [pull request 60](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/60): `push=true` for a manual run on `main`, so a "dry run" could have reached the Docker login. **After**: `push=false` with a notice for anything that is not a `v*` tag; a tag gives `push=true`; a tag with publishing switched off gives `push=false` |
| Publish dry run on `main` at `8079f7ac` (the guard and the release both merged), [run 40501552352](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/actions/runs/40501552352) | success. The build, the in-image boundary check (which asserts the licence label) and the Trivy scan passed; the gate step passed; the Docker login, the push, the attestation and the digest record were skipped |
| Tag `v0.1.1` on that same commit, [publish run 40502008575](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/actions/runs/40502008575) | success: login, push with provenance and SBOM, attestation, digest record |
| Digest in the registry | `sha256:95082857e3b866743ffa5c827c7b897d085e945d80aa4b710f58926b03170456` for `docker.io/hybridcloudworks/img-ca-lab-addon:v0.1.1` |
| Labels on the published image (`docker buildx imagetools inspect <image> --format '{{json .Image.Config.Labels}}'`) | `org.opencontainers.image.licenses=MIT`, `org.opencontainers.image.version=0.1.1`, `org.opencontainers.image.revision=8079f7ac9b92769bf65ec81d9848154dbc74bce2` |
| `gh attestation verify oci://docker.io/hybridcloudworks/img-ca-lab-addon:v0.1.1 --repo saulpatinojr/HCW-CloudAssessor_AddOn` | passes (exit 0). With `--format json`: the attested subject digest equals the registry digest above, the predicate is SLSA provenance v1, the signer is `.github/workflows/publish-images.yml@refs/tags/v0.1.1` of this repository, and the source commit is the tagged commit. Without a terminal the command prints nothing, so read its exit code or use `--format json` |
| GitHub Release | [v0.1.1](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/releases/tag/v0.1.1) |
| The live lab host | **not changed**: it keeps running the `v0.1.0` image until a website change pins the new digest (the owner said nothing changes on the website for this release) |

CodeRabbit's note on the release pull request ([61](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/61)) asked for a tag guard
before any manual publish run; that is pull request 60, merged before the dry run. The section below records the state when the release was
prepared, before the guard, the dry run and the tag.

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
- `core-update.yml` is armed since 2026-10-31: the seed's dependency line carries `CORE_REF v0.1.0-seed`, and the
  first run after that opens the adoption pull request for the newest release (the wheel by URL, its sha256 in
  `uv.lock`; ADR-0001). Until that pull request merges, the engine is still the seed.
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
  **Accepted risk, so nobody has to rediscover it.** A repository secret can be read by any workflow that runs from a branch
  someone with write access can push, so `base-update.yml` is a second reader of the key beside `core-update.yml` (both can
  be started by hand with `workflow_dispatch`), and the base-update proof depends on that: it runs the workflow from a
  throwaway branch (it did, on 2026-10-27, and minted the token from that branch). As of 2026-10-27, only the owner can push here. The App
  is installed on the four add-on repositories, and both workflows ask the token action for this repository only
  (`repositories: ${{ github.repository }}`) with Contents and Pull requests write; a token lasts one hour. A modified workflow
  on another branch could ask for more: the limit is then whatever the App was granted when it was installed (that list is on
  the App's settings page, https://github.com/settings/apps, and is not repeated here because a session cannot read it), which
  is why the key is a risk. The owner decided on 2026-10-26 to leave the key as a repository secret
  ([HCW-HybridCloudWorks#1410](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1410)); the stronger options (an
  environment limited to `main`, or a separate App installation for each repository) can be reopened if the key is ever
  suspected leaked. A separate key for each repository on the same App is not one of them: it helps rotation (one key can be
  revoked without touching the others) but it does not shrink what a stolen key can reach, because every key authenticates the
  same App, and that App is installed on all four add-on repositories. An environment limited to `main` would also stop the
  base-update proof, which needs a run from a branch.
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
  check. It is also not a full second check at any time: it compares only the image and its digest, so if the website changes only
  `BASE_PYTHON_VERSION` to another minor line, `base-update` refuses and goes red while the weekly job stays green. How to see whether
  either has been switched off, and how to switch them back on, is in `docs/operations/runbook.md`, "If the daily run goes quiet";
  failed `base-update` runs should be watched on their own ("When the run is red").
