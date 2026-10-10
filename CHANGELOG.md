# Changelog

All notable changes to this repository are recorded here. The format follows Keep a Changelog; versions are semver tags.

## [Unreleased] — 0.1.0

### Changed
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
