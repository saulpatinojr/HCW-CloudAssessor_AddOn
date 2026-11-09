# AGENTS.md — guidance for coding agents (Copilot coding agent, Codex, Claude)

This is `saulpatinojr/HCW-CloudAssessor_AddOn`: the lab edition of the Cloud Assessor (upload-only, in-memory, no cloud
connectivity by design). The engine is owned and released by `saulpatinojr/HCW-CloudAssessor_App` (ADR-0001) and
installed here as its release wheel, pinned by URL in `pyproject.toml` and by sha256 in `uv.lock`; `core-update.yml`
opens the pull request for each new release. The seed that used to live under `packages/` was deleted when the first
wheel was adopted; do not re-create it. Read `docs/whats-new-upstream.md` before changing behaviour.

Build/test: `uv sync --all-packages`, then `uv run ruff check . && uv run ruff format --check .`,
`uv run python scripts/check-catalog.py`, `uv run pytest -q --cov=src`; browser suite `make e2e`.
Conventions and invariants: `CLAUDE.md`. Review expectations: `.github/copilot-instructions.md`. AI-created changes go
through the review -> fix -> current-head verification cycle before merge.
