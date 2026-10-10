# Operations runbook (lab edition)

The container is run by the website repository's `addons` role on the lab host (`docs/deployment/lab-host.md`). The
commands below are bash on the host unless stated. Nothing here touches a cloud.

| Task | How | What success looks like |
|---|---|---|
| Health | `curl -s http://127.0.0.1:18083/api/health` | `{"ok":true,"id":"cloud-assessment","version":"0.1.0","edition":"lab",…,"azureConnectivity":"disabled-by-design",…}` within a second |
| Which version is live | `curl -sI http://127.0.0.1:18083/api/health \| grep -i x-addon-version` | `x-addon-version: 0.1.0` |
| Logs | `docker logs --since 1h hcw-addon-cloud-assessment` | JSON lines on stderr: `startup`, `assessment_created` (counts and durations), `assessment_read`, `assessment_deleted`, `rate_limited`, `busy`, `turnstile_rejected` (a count of codes), `sweep`, `shutdown`. Never ids, names, tokens, file names or cell content. |
| Restart | `docker restart hcw-addon-cloud-assessment` | Health answers again within the `HEALTHCHECK` start period (10 s). Every in-memory assessment is gone by design. |
| Upgrade / rollback | Move `image_tag` and `image_digest` in the website's `group_vars/all.yml`; run `bootstrap.sh` | The role pulls by digest, recreates the container and waits for health. Rollback is the previous digest. |
| Stop serving (kill switch) | Website: unset `ADDON_CLOUD_ASSESSMENT_URL` (the proxy answers `configured:false`, the page shows the one sentence). Host: `enabled: false` on the row and run `bootstrap.sh` (the container is removed; Caddy answers 503 with the same sentence). | Visitors see `This tool isn't available right now.` and nothing else |
| Abuse | Per client address: `CA_RATE_LIMIT_POSTS` per `CA_RATE_LIMIT_WINDOW_MINUTES` (defaults 10 / 10) and `CA_MAX_CONCURRENT` (2). Tighten in `addons[].env`; human verification is already required on every upload. A burst shows as `rate_limited` and `busy` log lines. | 429 / 503 answers with `Retry-After`; health stays 200 |
| Verification outage | Uploads answer `403 turnstile_failed` with code `verification-unavailable` (the siteverify call failed within 5 s). Nothing to do on the host; the pane tells the visitor to retry. | Health unaffected |
| Data request | There is nothing to retrieve or erase: assessments live in process memory for at most `CA_TTL_MINUTES` (120), are returned only to the holder of the owner token, and a restart purges everything. State this in the reply. | — |
| Memory or pids pressure | The role caps the container at 512m and 256 pids; the store holds at most `CA_MAX_ITEMS` (200) assessments (oldest evicted) of at most 5 MB input each. | `docker stats hcw-addon-cloud-assessment` stays under the caps |

Troubleshooting a container that will not start: `docker logs hcw-addon-cloud-assessment` prints one line
`{"event":"startup_refused","reason":"…"}` (exit code 3) when the edition guard refused (an identity endpoint or a
credential variable in the environment) or the catalog failed to load. Neither is fixed on the host: remove the
offending environment, or rebuild the image.
