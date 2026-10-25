# Changelog

All notable changes to this repository are recorded here. The format follows Keep a Changelog; versions are semver tags.

## [Unreleased] — 0.1.0

### Added
- `.github/workflows/codeql.yml` (CodeQL for the workflow files and the Python, on pull requests, on `main` and every Monday) and `.github/workflows/dependency-review.yml` (blocks a pull request that adds a dependency with a known high or critical vulnerability), both copied from `HCW-CloudCrawler_AddOn`, which had them while this repository did not. Both are read-only (`contents: read`, plus `security-events: write` for CodeQL's own upload), pin every action to a full commit, and are not required checks. The dependency-review job drops its pull request comment and write permission.

- The lab image repository on Docker Hub is renamed from `hybridcloudworks/hcw-addon-cloud-assessment` to `hybridcloudworks/img-ca-lab-addon` (owner naming convention `img-<short name>-<job>-<type>`, 2026-10-25), and its tag is now the full release tag (`v0.1.0`, not `0.1.0`). `publish-images.yml` (`IMAGE`, the tag, the image title label), the local `:dev` build tag, the README and the deployment and integration documents follow. The container name on the lab host (`hcw-addon-cloud-assessment`) is **not** changed: the website's host role owns it. Nothing is published by this change; the next `v*` tag pushes to the new name once the Docker OIDC connection allows it (`docs/deployment/lab-host.md`, step 4).
- Hardening: the last step of `publish-images.yml` printed the release version straight into a shell command (`echo "image_tag: ${{ steps.version.outputs.version }}"`). The version comes from the pushed tag's name, so a crafted tag name could inject a command. It now reaches the shell through the environment variable `IMAGE_TAG` and is printed as `"${IMAGE_TAG}"`. This was already present before the rename; only people with write access can push tags.

### Added
- `.github/dependabot.yml` groups `pydantic` and `pydantic-core` so they arrive in one pull request. pydantic requires one exact `pydantic-core`, so a `pydantic-core` bump on its own cannot resolve; the same failure closed the App repository's Dependabot pull requests.
- `docs/whats-new-upstream.md`: a running note of what the App released and changed that reaches this edition (current upstream state, the two releases not yet adopted, the compatibility trial, the adoption steps, and open upstream decisions). `CLAUDE.md` and `docs/README.md` point to it.

### Changed
- `docs/website-integration/integration-guide.md` follows the website after hybridcloudworks.com#1359 (issues #1353 and #1354, owner decisions of 2026-10-24): the row now holds `downloads` and `clipboard-write` (it held `navigate` and `downloads`), the frame address carries `?theme=dark|light` read once from the site's theme, the clipboard grant is write only, and the row copy is taken from website commit b0cf0055.
- `docs/website-integration/integration-guide.md` now follows the website's real catalogue row. The row pasted into it was
  written before the row shipped and had drifted: 5 of its 10 fields differed from the website's (summary, pane path,
  technology, status and capabilities, plus the `comingSince` and `comingReason` fields). The block is now a copy of the
  website's current row, with the website commit it came from, and says the website is the authority. The guide also
  says that the site frames `origin + panePath` with no `?theme=` parameter (the pane still honours one), and that the
  site grants `navigate` and `downloads` where this AddOn asked for `downloads` and `clipboard`; the owner confirms
  whether that is intended. Compared field by field with a script on 2026-10-24: 0 of 10 now differ.
- **Documents say who owns the engine.** `CLAUDE.md`, `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, the pull request template and `.github/copilot-instructions.md` still said the engine is "seeded here and moves upstream" and "edited here until the App adopts it". The App adopted it (its "Engine adopted" entry) and has released it as `v0.2.0` and `v0.2.1`, so they now say the App owns it and the seed here is not edited until it is replaced by the release wheel. `ADR-0001` is left as written (a historical record). Documents only; no code, test or dependency changed.
- Dependency updates pass CI as Dependabot opens them. Its `pip` updater rewrote `pyproject.toml` and the committed
  `requirements.lock.txt` but never `uv.lock`, so every one of its pull requests failed the export check (#12 to #15).
  `.github/dependabot.yml` now uses the `uv` ecosystem, which moves `pyproject.toml` and `uv.lock` together. The
  committed export is gone: the image's build stage runs `uv export --frozen` from `uv.lock` with the uv CI uses, by
  digest, and still installs with `pip --require-hashes --no-deps`; uv never reaches the lab stage. CI checks
  `uv lock --check` and that the Dockerfile's uv is `UV_VERSION`; `pip-audit` audits the same export. The engine
  declares `pydantic>=2.14,<3` (the app keeps the exact pin), so the two cannot be bumped apart while the engine is
  the seed; the App's engine must carry the same range before its wheel is adopted (HCW-CloudAssessor_App#15).
  CI builds the image on every pull request, resolves the uv digest for `UV_VERSION` rather than trusting any
  digest, and a weekly job flags the base drifting from the website's pin.
- Base image `python:3.14.8-slim-trixie` by digest, the website's current pin (CONTRACT-DECISIONS item 20). There is
  no docker Dependabot entry: the base follows the website, and the uv image follows `UV_VERSION`.
- Repository hygiene: `.github/dependabot.yml` groups GitHub Actions updates under `all-actions` and removes the unused `/tests/e2e` npm entry; `tests/unit/test_config.py` and `tests/unit/test_edition.py` use `as_posix()`, `os.pathsep`, and `SYSTEMROOT` forwarding for cross-platform Windows/Linux test parity.
- `core-update.yml`'s checkout no longer persists credentials: two Authorization headers made GitHub answer `400` to `create-pull-request`'s push (reproduced twice in the Migrate App's `rules-refresh`, fixed there in saulpatinojr/HCW-AzMigrateOrchestrator_App#24).
- README: a "where to try it" paragraph for new visitors; the relationship diagram and text say the App now holds the engine and the seed here is deleted at its first release.
- `core-update.yml` pins the upstream engine as the GitHub Release wheel asset by URL, so `uv lock` records its sha256 and the image's `pip install --require-hashes` keeps verifying it; the `git+https` form it described before cannot be hash-checked by pip and would have broken the image build on the first adoption. No PyPI step is needed (ADR-0001 amended).
- Code scanning: the e2e host page accepts only a loopback `?addon=` origin for the frame and the message filter, and the unit test asserts the exact `script-src` and `frame-src` source lists instead of a substring (closes the three CodeQL alerts raised on #5; test and harness code only, no runtime change).
- Cross-AddOn standardization (program Phase 5D): the concurrency-cap answer is `503 overloaded` (was `busy`), the code
  the Azure Migrate AddOn already uses; log event renamed to match.
- Numeric settings are bounded to 1,000,000,000 (`MAX_SETTING`), so an absurd value cannot push a TTL, window or
  bucket into arithmetic the clocks cannot represent; mirrors the Azure Migrate AddOn's safe-integer rule.

### Added
- Engine seed `packages/cloud-assessor-core` 0.1.0 (pydantic only): `Resource` model (`MODEL_VERSION = 1`), JSON-path-lite,
  `arg-json` / `arg-csv` ingestion (array or `az graph query` envelope with the paged warning; Resource Graph Explorer
  CSV with JSON cells; portal "All resources" CSV accepted with the "no properties column" warning; BOM strip, delimiter
  sniff, formula neutralisation, row caps), catalog loader with a generated JSON Schema (draft 2020-12) drift check and a
  `learnUrl` host allow-list, six evaluator kinds (`tag-present`, `property-equals` with `anyOf`, `property-exists`,
  `sku-in`, `count-threshold` resource/estate, `cross-resource` has-child/estate-has/has-sibling) with `when`
  applicability, `missingIs` and `anyPass`, severity- and pillar-weighted scorecards where unknown lowers coverage and
  never score, `report.md`, `report.json`, `findings.csv` (neutralised), `NOT-AN-AUDIT.md`, `bundle.zip` (STORE), and
  the log-path redaction guard.
- Catalog 1.0.0: 25 paraphrased, attributed criteria (`CA-FIN-001..007`, `CA-WAF-001..007`, `CA-ZT-001..011`) with
  `verify: true` and `retrievedOn: 2026-10-10` on every reference link; `scoring.json`.
- Lab application `src/cloud_assessment_lab` 0.1.0 (FastAPI 0.143.0, uvicorn 0.54.0, pydantic 2.14.0): `CA_*` settings,
  import-time edition guard (no cloud SDK importable, refusal under identity endpoints, a `sys.meta_path` finder that
  refuses `azure`, `msal`, `boto3`), in-memory store (UUID4, hashed owner tokens, TTL sweep, eviction), human
  verification with `action` echo and fail-closed posture (`CA_ALLOW_NO_TURNSTILE=1` for local use only), security
  headers with configurable `frame-ancestors`, exact-origin CORS, 5 MB streamed cap, 5,000 rows, per-client token bucket
  (`CA_TRUST_PROXY` for `X-Forwarded-For`), concurrency bound, content-free JSON logs, the flat `/api/health` envelope
  and the documented route set with the error envelope.
- Vanilla pane (`web/`) with the HCW theme tokens copied with provenance, `?theme=` selection, the `hcw-addon` message
  bridge (`loading | ready | working | unavailable`), upload preview, scorecards with coverage sentences, filterable
  findings, detail panel, "Unknown by design" panel, bundle download, "Copy report" fallback and immediate delete.
- Samples (40 fictional rows in three export shapes) with pinned expected results; unit, contract (OpenAPI two-way),
  security (edition boundary, no secrets, content-free logs), manifest and Playwright suites (standalone and framed).
- Docs (website integration, routes, API, lab host, appliance pointer, runbook, threat model, user guide, bundle,
  generated criteria catalog, ADR-0001..0003 and copies of upstream ADR-0008/0011/0028), hardened two-stage Dockerfile
  on the website's base-image digest, local compose, SHA-pinned `ci`, `security`, `publish-images` (Docker Hub by OIDC,
  Trivy before push, image-level boundary check) and inert `core-update` workflows, Dependabot, CODEOWNERS, PR template.
