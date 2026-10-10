# Contributing

1. Fork/branch, `uv sync --all-packages`, make the change, then `uv run ruff check . && uv run ruff format --check .`, `uv run python scripts/check-catalog.py`, `uv run pytest -q --cov=packages --cov=src`, and `make e2e` for pane or API changes.
2. Engine changes (`packages/cloud-assessor-core`) are written to move upstream unchanged (ADR-0001): pydantic only, no HTTP, no cloud SDK; evaluator kinds are added, never renamed; `MODEL_VERSION` moves only when `Resource` changes.
3. Catalog changes keep criteria paraphrased and attributed, carry a `learnUrl` on an allowed host and a `retrievedOn` date, and regenerate `docs/rules/catalog.md` (`make rules-doc`) and, if the model changed, `catalog/schema.json`.
4. Fill the PR template honestly: what you ran, what you did not, and why. Pull requests open ready for review.
5. Keep `VALIDATION.md` and `CHANGELOG.md` current; edition-relevant upstream ADRs are copied into `docs/adr/`.
6. Be kind; see `CODE_OF_CONDUCT.md`.
