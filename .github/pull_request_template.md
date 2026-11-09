## Summary

<!-- What changes and why. Name the AddOn Integration Standard section or the ADR this affects. -->

## Verification

- [ ] `uv run ruff check . && uv run ruff format --check .` — result:
- [ ] `uv run python scripts/check-catalog.py` — result:
- [ ] `uv run pytest -q --cov=src` — result (tests, coverage):
- [ ] `npx playwright test -c tests/e2e/playwright.config.ts` — result, or CI run link:
- [ ] Checks not run and why:

## Engine and catalog (if the `cloud-assessor-core` wheel pin in `pyproject.toml` or `uv.lock` changed)

- [ ] The engine and its catalog are owned upstream (ADR-0001): this change adopts an `HCW-CloudAssessor_App` release wheel unchanged, by URL and sha256, and `docs/whats-new-upstream.md` records it
- [ ] `docs/rules/catalog.md` regenerated (`make rules-doc`) from the new wheel's catalog

## Infrastructure (if `infrastructure/**` or `docker-compose.yml` changed)

- [ ] `versions.env` and every `FROM` agree; `uv lock --check` passes
- [ ] No privileged containers, Docker socket exposure or secrets introduced

## Security and data review

- [ ] No real tenant, subscription or resource identifiers anywhere (samples use `00000000-0000-0000-0000-000000000001`)
- [ ] Nothing weakens the edition boundary, the fail-closed human verification, owner-token isolation, the limits, exact-origin CORS or the "not production" labels

## AI provenance

- [ ] Code created or changed by an AI coding partner (GitHub Copilot / Claude / Codex); reviewer applies the review -> fix -> current-head verification cycle
