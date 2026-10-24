# GitHub Copilot repository instructions

Treat GitHub Copilot as one teammate with separate review and remediation hats: `copilot-pull-request-reviewer[bot]`
reviews; `copilot-swe-agent` fixes only when explicitly requested. A fix that demonstrably closes the original finding
closes that finding: acknowledge and resolve the thread, then evaluate the current head. Handle disagreement on-thread
with evidence and a counter-proposal. Never treat a stale-head check as current evidence.

## This repository

`saulpatinojr/HCW-CloudAssessor_AddOn` is the **lab edition** of the Cloud Assessor: a Python 3.14 FastAPI application
(`src/cloud_assessment_lab`) that assesses an uploaded Azure Resource Graph export against a declarative criteria
catalog, plus the original engine seed (`packages/cloud-assessor-core`; the engine is now owned and released by `HCW-CloudAssessor_App`, see `docs/whats-new-upstream.md`), a vanilla pane
(`web/`), fictional samples, docs, a hardened Dockerfile and SHA-pinned workflows.

Review against `CLAUDE.md`'s invariants. In particular: the lab must stay technically unable to reach Azure (no cloud
SDK, import-time refusal under identity endpoints, `tests/security/test_edition_boundary.py`); uploads stay gated by
human verification unless `CA_ALLOW_NO_TURNSTILE=1` (local only); owner tokens are hashed and compared in constant
time; 5 MB / 5,000 rows / 200 items / 120 minutes; logs carry no visitor data; no vendor names in visitor copy; every
`learnUrl` is `[VERIFY]` until the owner confirms it; samples use only subscription `00000000-0000-0000-0000-000000000001`.
