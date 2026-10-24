# Validation

What was executed for this edition and what was not, per run. "Here" is the authoring container (no Docker daemon, PyPI
and the Playwright CDN reachable through a proxy). Dates are the run date.

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
