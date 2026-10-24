# AGENTS.md — guidance for coding agents (Copilot coding agent, Codex, Claude)

This is `saulpatinojr/HCW-CloudAssessor_AddOn`: the lab edition of the Cloud Assessor (upload-only, in-memory, no cloud
connectivity by design) plus the original engine seed `packages/cloud-assessor-core` (`0.1.0`). The engine is owned by
`saulpatinojr/HCW-CloudAssessor_App` (ADR-0001), which has released it as `v0.2.0` and `v0.2.1`; the seed is awaiting
adoption of that wheel and is not edited here. Read `docs/whats-new-upstream.md` before changing behaviour.

Build/test: `uv sync --all-packages`, then `uv run ruff check . && uv run ruff format --check .`,
`uv run python scripts/check-catalog.py`, `uv run pytest -q --cov=packages --cov=src`; browser suite `make e2e`.
Conventions and invariants: `CLAUDE.md`. Review expectations: `.github/copilot-instructions.md`. AI-created changes go
through the review -> fix -> current-head verification cycle before merge.
