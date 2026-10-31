# CLAUDE.md — working agreement for Claude Code in this repository

This is `saulpatinojr/HCW-CloudAssessor_AddOn`, the **lab edition** of the Cloud Assessor (AddOn id `cloud-assessment`,
site route `/tools/cloud-assessment`, origin `https://cloud-assessment.lab.hybridcloudworks.com`): a Python 3.14 FastAPI
application that assesses an uploaded Azure Resource Graph export against a declarative criteria catalog, a vanilla pane
the website frames, fictional samples, docs, a hardened Dockerfile and SHA-pinned workflows. The engine
is **owned upstream** by `saulpatinojr/HCW-CloudAssessor_App`: it was seeded here (ADR-0001), the App adopted it unchanged
and has released it as `v0.2.0` and `v0.2.1` (wheel assets). The copy under `packages/cloud-assessor-core` is the
original `0.1.0` seed, now two releases behind and **not to be edited**; engine and catalog changes go upstream first and
arrive here as a release wheel through `core-update.yml`. The dependency line carries `CORE_REF v0.1.0-seed`, so the
workflow's next run opens the adoption pull request itself (`scripts/adopt_core_wheel.py` rewrites the line to the wheel
URL, the seed is deleted, `uv lock` records the sha256); once that merges, `packages/` is gone and `--cov=packages` drops.
**Read `docs/whats-new-upstream.md` before changing behaviour here, and update it when you adopt an upstream change.**

- Run `uv sync --all-packages`, then `uv run ruff check . && uv run ruff format --check .`,
  `uv run python scripts/check-catalog.py` and `uv run pytest -q --cov=packages --cov=src` before claiming anything
  works; `make e2e` for anything touching the pane or the API. Never claim a check passed that you did not run.
- Never weaken: the lab's inability to construct an Azure credential (no cloud SDK; `edition.py` refuses to start under
  `IDENTITY_ENDPOINT`/`MSI_ENDPOINT`/`AZURE_CLIENT_SECRET`/`AZURE_FEDERATED_TOKEN_FILE`/`AZURE_CLIENT_ID`/`AZURE_TENANT_ID`;
  `tests/security/test_edition_boundary.py`); fail-closed human verification (uploads answer 503 without a secret unless
  `CA_ALLOW_NO_TURNSTILE=1`, local only); owner-token isolation (hashed, constant-time, 404 for foreign ids); the
  5 MB / 5,000-row / 200-item / 120-minute limits; exact-origin CORS; the content-free log writer; the "not production"
  and "no cloud connectivity by design" labels; the `NOT-AN-AUDIT.md` in every bundle.
- Scoring: severity weights critical 4 / high 3 / medium 2 / low 1; pillar weights in `catalog/scoring.json`; request
  overrides clamp to [0, 10]; **unknown lowers coverage, never score**. Evaluator kinds are only added, never renamed.
- Criteria are paraphrased and attributed (`text` is the single replaceable field, R-005); every `learnUrl` stays
  `verify: true` until the owner confirms it; cite with a `retrievedOn` date. `docs/rules/catalog.md` is generated
  (`make rules-doc`); `catalog/schema.json` is generated (`scripts/check-catalog.py --write-schema`).
- No secrets, tokens, customer inventories or real tenant/subscription ids anywhere, fixtures and tests included.
  Samples use subscription `00000000-0000-0000-0000-000000000001` and `hcw-sample-*` names only.
- No vendor names in anything a visitor can read (not the host, edge, verification provider or workspace platform):
  say "human verification" and "expires after two hours".
- Owner-pasteable commands: no placeholders; bash and PowerShell both acceptable.
- `/api/health` is flat (`id`, `version` at the top level); the pane posts `{type:'hcw-addon', id, state}` with states
  `loading | ready | working | unavailable` to each origin in `siteOrigins` only.
- ADRs: this edition's own in `docs/adr/` (next number: 0004); upstream ones copied with a header. Record limitations in
  `VALIDATION.md`. Keep `CHANGELOG.md` current. Pull requests open ready for review and follow the template.
