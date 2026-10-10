# AGENTS.md — guidance for coding agents (Copilot coding agent, Codex, Claude)

This is `saulpatinojr/HCW-CloudAssessor_AddOn`: the lab edition of the Cloud Assessor (upload-only, in-memory, no cloud
connectivity by design) plus the engine seed `packages/cloud-assessor-core` that moves upstream to
`saulpatinojr/HCW-CloudAssessor_App` (ADR-0001).

Build/test: `uv sync --all-packages`, then `uv run ruff check . && uv run ruff format --check .`,
`uv run python scripts/check-catalog.py`, `uv run pytest -q --cov=packages --cov=src`; browser suite `make e2e`.
Conventions and invariants: `CLAUDE.md`. Review expectations: `.github/copilot-instructions.md`. AI-created changes go
through the review -> fix -> current-head verification cycle before merge.
