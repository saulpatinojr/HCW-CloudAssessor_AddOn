# ADR-0001: The lab edition is upload-only; the Python engine is seeded here and handed upstream

Status: accepted, 2026-10-10. Scope: `HCW-CloudAssessor_AddOn`; affects `HCW-CloudAssessor_App` (its `REFACTOR_APP.md` section 7.1).

## Context

The Cloud Assessor App had no code when this AddOn was created, only governance files and a backlog (T-001..T-031,
R-001..R-008) that signal a Python product. The program needs a lab edition on the website now, framed as a pane at
`/tools/cloud-assessment`, that assesses an Azure estate without ever holding a credential. ADR-0028 (copied here)
prescribes the model for the sibling pair: the App is upstream and publishes the engine; the AddOn is a strict,
downstream, web-front subset. With no upstream engine to consume, the seed has to be written somewhere.

## Decision

1. **The lab edition is upload-only.** Its input is a Resource Graph export (`arg-json`: array or `az graph query`
   envelope; `arg-csv`: Resource Graph Explorer CSV; the portal "All resources" CSV accepted with a warning). It has
   no sign-in, no cloud SDK, no live reads, no persistence, no execution. It refuses to start where a managed identity
   is offered (`edition.py`), and reports `azureConnectivity: disabled-by-design`.
2. **The engine is Python and is seeded in this repository** as the installable package
   `packages/cloud-assessor-core` (pydantic only; no HTTP import), with its catalog (`criteria.json`, generated
   `schema.json`, `scoring.json`) and its tests beside it. The App adopts the package verbatim from this repository's
   tag `v0.1.0`; after the App's first release, this repository pins
   the wheel `publish-core.yml` attaches to that release, by URL and sha256
   (`cloud-assessor-core @ https://github.com/saulpatinojr/HCW-CloudAssessor_App/releases/download/<tag>/cloud_assessor_core-<version>-py3-none-any.whl`;
   amended 2026-10-10: the `git+https` form first written here cannot be verified by the image's `pip install --require-hashes`),
   deletes the seed, and `core-update.yml` adopts later releases (compatible / needs-adaptation pull requests).
3. **Honesty is in the data.** Findings carry `state: observed | unknown | not-applicable`; scorecards carry `coverage`;
   unknown lowers coverage, never score; the things an export cannot show are criteria that answer `unknown` with a
   reason, surfaced in an "Unknown by design" panel and in `report.md`; `NOT-AN-AUDIT.md` ships in every bundle.
4. **Criteria are paraphrased and attributed**, with `text` as the single replaceable field, a `learnUrl` on an allowed
   host and a `retrievedOn` date; every link is `verify: true` until the owner confirms it (`[VERIFY]`); attribution
   wording is `[REVIEW REQUIRED]` (R-005).
5. **Downloads and the sandbox.** The site's pane sandbox has no `allow-downloads` today; the pane always offers
   "Copy report" and a selectable report, and the integration guide requests the `downloads` capability
   (`[REVIEW REQUIRED]`, website security decision).

## Consequences

- The lab can ship before the App exists; the App's day one is an adoption, not a rewrite (Python matched the App's
  intent; a TypeScript seed would have handed it one).
- Engine changes are made here only until the hand-over; the package is written as if it already lived upstream
  (`MODEL_VERSION`, evaluator kinds only added, never renamed, catalog versioned).
- The appliance's live collectors emit the same `Resource` rows the lab parses, so one engine serves both editions;
  the appliance adds `CostEvidence` (core 0.2.0) without touching the lab.
- `tests/security/test_edition_boundary.py` and the image-level check in `publish-images.yml` make the boundary
  enforceable rather than documented.
