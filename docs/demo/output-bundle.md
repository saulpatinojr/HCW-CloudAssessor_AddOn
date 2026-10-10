# The output bundle

`GET /api/assessments/{id}/bundle.zip` (owner token required) is a STORE zip (no compression, fixed timestamps) with
exactly four files, each also available at `…/files/{name}`:

| File | Content |
|---|---|
| `report.md` | Executive summary (resources, criteria, findings by state), the scorecard table with the coverage sentence per framework, failed checks by severity with evidence path / observed / expected / remediation, the unknown list with reasons, "What this export cannot show", attribution |
| `report.json` | The full assessment document: `id`, `created_at`, `model_version` (1), `catalog_version`, `core_version`, `source_format`, `file_name`, `summary`, `scorecards[]`, `findings[]` (`criterionId, framework, pillar, severity, resourceId, resourceName, resourceType, state, result, evidence{path, observed, expected}, reason, remediation, learnUrl`), `unknown_by_design[]`, `ingestion_warnings[]` |
| `findings.csv` | One row per finding, every cell formula-neutralised (a leading `= + - @` is prefixed with `'`) |
| `NOT-AN-AUDIT.md` | What the assessment is and is not |

Versions in `report.json` let results be compared across releases: `model_version` moves only when the `Resource`
model changes; `catalog_version` when criteria change; `core_version` is the engine package version.

The bundle carries your own data (resource ids, subscription ids, tags, properties) back to you. It is returned only to
the holder of the owner token and is never written to disk on the server.
