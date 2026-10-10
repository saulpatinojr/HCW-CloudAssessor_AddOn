> Copied from HCW-AzMigrateOrchestrator_App/docs/adr/ADR-0011-uploads-are-never-persisted-and-every-demo-conclusion-carries-an-evidence-state.md on 2026-10-10; applies by analogy to the Cloud Assessor pair
> (HCW-CloudAssessor_App upstream, HCW-CloudAssessor_AddOn downstream). The canonical text lives upstream; this copy is not edited here.

# ADR-0011: Uploads are never persisted and every demo conclusion carries an evidence state

**Status:** Accepted · **Date:** 2026-10-03

## Context

§16 security and labelling requirements.

## Decision

In-memory processing, size/row limits, formula neutralisation on ingest and on CSV output, provenance per field, evidence states on every decision, confidence capped at 0.74 when unauthenticated.

## Consequences

Users can trust that 'observed' means the CSV said so and 'inferred' means we guessed from type.
