## Summary

<!-- What changes and why. Name the AddOn Integration Standard section or the ADR this affects. -->

## Verification

- [ ] `uv run ruff check . && uv run ruff format --check .` — result:
- [ ] `uv run python scripts/check-catalog.py` — result:
- [ ] `uv run pytest -q --cov=packages --cov=src` — result (tests, coverage):
- [ ] `npx playwright test -c tests/e2e/playwright.config.ts` — result, or CI run link:
- [ ] Checks not run and why:

## Catalog (if `packages/cloud-assessor-core/catalog/**` changed)

- [ ] `learnUrl` and `retrievedOn` updated for every touched criterion; `verify` left `true` until the owner confirms
- [ ] Criteria stay paraphrased and attributed (R-005); only `text`, `title`, `remediation` carry prose
- [ ] `docs/rules/catalog.md` regenerated (`make rules-doc`) and `schema.json` regenerated if the model changed

## Engine (if `packages/cloud-assessor-core/src/**` changed)

- [ ] The change is meant to move upstream to `HCW-CloudAssessor_App` unchanged (ADR-0001); `MODEL_VERSION` bumped only if `Resource` changed
- [ ] No FastAPI, HTTP or cloud SDK import entered the package

## Infrastructure (if `infrastructure/**` or `docker-compose.yml` changed)

- [ ] `versions.env` and every `FROM` agree; `requirements.lock.txt` re-exported
- [ ] No privileged containers, Docker socket exposure or secrets introduced

## Security and data review

- [ ] No real tenant, subscription or resource identifiers anywhere (samples use `00000000-0000-0000-0000-000000000001`)
- [ ] Nothing weakens the edition boundary, the fail-closed human verification, owner-token isolation, the limits, exact-origin CORS or the "not production" labels

## AI provenance

- [ ] Code created or changed by an AI coding partner (GitHub Copilot / Claude / Codex); reviewer applies the review -> fix -> current-head verification cycle
