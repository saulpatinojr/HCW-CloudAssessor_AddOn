# Website integration guide

How `hybridcloudworks.com` shows the Cloud Assessment lab edition, per the HCW AddOn Integration Standard (website
repository `docs/standards/addon-integration-standard.md`, ADR 0035). The site frames this AddOn in a sandboxed pane on
one page; nothing from this repository is installed into the site bundle.

## Identity

| Item | Value |
|---|---|
| AddOn id | `cloud-assessment` |
| Site route | `/tools/cloud-assessment` (`frontend/src/pages/tools/AddOnPanePage.jsx` with `addonId="cloud-assessment"`; `CloudAssessmentPage.jsx` wrapper) |
| Origin | `https://cloud-assessment.lab.hybridcloudworks.com` (exactly `'https://' + id + '.lab.hybridcloudworks.com'`) |
| Frame `src` | `https://cloud-assessment.lab.hybridcloudworks.com/` exactly (the site builds `origin + panePath` and adds no query string). The pane still honours `?theme=dark` or `?theme=light` if a caller passes one; the site does not, so without it the pane follows `prefers-color-scheme` (read 2026-10-24: `addonPaneUrl` in the catalogue, and `AddOnPanePage.jsx` has no theme handling) |
| Health path | `/api/health` |
| Function App setting (status proxy) | `ADDON_CLOUD_ASSESSMENT_URL` = the origin, plain app setting (public value) |
| Lab-host vault key | `vault_addon_cloud_assessment_turnstile_secret` |
| Lab-host loopback port | 18083 |
| Image | `docker.io/hybridcloudworks/hcw-addon-cloud-assessment`, pinned by digest in the website's `lab-host/ansible/group_vars/all.yml` `addons[]` |

## Catalogue row (`frontend/src/data/addons/catalogue.js`)

The website's row is the authority. This is a copy of it as of 2026-10-24 (website commit 5757bb71, the last change to that file). An earlier copy, written
before the row shipped, was kept here and drifted: the site's summary, pane path, technology, status and
capabilities all ended up different from it. When this block and the website disagree, the website is right.

```js
{
  id: 'cloud-assessment',
  title: 'Cloud assessment',
  summary: 'Upload an export of your Azure resources and get a scored assessment against a catalogue of reliability, security, cost and operations criteria. Nothing you upload is kept beyond two hours.',
  origin: 'https://cloud-assessment.lab.hybridcloudworks.com',
  panePath: '/',
  healthPath: '/api/health',
  providers: ['azure'],
  technology: ['well-architected', 'resource-graph'],
  status: 'available',
  capabilities: ['navigate', 'downloads'],
  docsUrl: 'https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn#readme',
  articleSlugs: []
}
```

The row became `available` on 2026-10-12 (website #1089), when the digest was pinned. `title` and `summary` obey the site's public-copy rule (no vendor names; "human verification", "expires after two hours").

## Status proxy

`GET /api/public/addons/cloud-assessment/status` (anonymous, registered in `functions/src/lib/addons/registry.js` with
`setting: 'ADDON_CLOUD_ASSESSMENT_URL', healthPath: '/api/health'`) reads this AddOn's `/api/health` with a 5 s timeout
and projects exactly `configured, reachable, version, edition, capabilities, asOf`. Every other health field
(`catalog`, `limits`, `turnstile`, `siteOrigins`, `azureConnectivity`) is for the pane and is never forwarded. The pane
mounts only when the proxy answers `configured: true, reachable: true`; otherwise the page shows
"This tool isn't available right now."

## Pane protocol

The pane posts, to each origin in its own `/api/health.siteOrigins` (env `CA_SITE_ORIGINS`, never `*`):

```json
{ "type": "hcw-addon", "id": "cloud-assessment", "state": "ready" }
```

| State | When |
|---|---|
| `loading` | As soon as the health read answers (the pane needs `siteOrigins` before it can post anything) |
| `ready` | Health answered `ok: true` with `id: cloud-assessment`; after every upload completes or fails |
| `working` | While `POST /api/assessments` is in flight |
| `unavailable` | Health failed or answered another id (also shown in-pane with the one sentence) |

If the API is down before the first health read, the pane cannot know the site origins and posts nothing; the page's
30 s watchdog shows the unavailable sentence. The site accepts a message only when `event.origin === origin`,
`event.source === frame.contentWindow`, `data.type === 'hcw-addon'`, `data.id === 'cloud-assessment'` and `data.state`
is one of the four. This AddOn sends no `navigate` and requires no message from the site.

## Sandbox and capabilities

Base sandbox `allow-scripts allow-same-origin allow-forms`. This row asks for:

- `downloads` -> `allow-downloads`: the bundle zip and the sample files are saved from inside the pane.
  **[REVIEW REQUIRED]** Owner decision as a website security change (standard section 21, ADR 0035). The pane works
  without it: "Copy report" puts `report.md` on the clipboard and the report is rendered in a selectable block, and the
  pane says so when a download does not start.
- `clipboard` -> `allow="clipboard-write"` on the frame for "Copy report" (a `document.execCommand('copy')` fallback
  inside the user gesture exists for browsers that refuse the API).

Never `allow-top-navigation`; `allow-popups` is not requested.

**What the site grants today (read 2026-10-24):** `navigate`, `downloads`. That differs from what this AddOn asked for above: `clipboard` (`clipboard-write`) is not granted, and `navigate` is granted although this AddOn never sends one. Whether that is intended is the owner's to confirm against ADR 0035; until then "Copy report" depends on its in-gesture fallback.

## Content security policy, both sides

- Site: `frame-src` gains `https://cloud-assessment.lab.hybridcloudworks.com` (derived from `addonOrigins()`).
- AddOn: `frame-ancestors` from `CA_FRAME_ANCESTORS`, set by the role to the two site origins, equal to the host's
  `caddy_frame_ancestors` (both policies are enforced by the browser; they must agree). `X-Frame-Options: DENY` is sent
  only when the value is `'none'` (the default, which is what a direct visit outside the lab host sees).

## Environment table (rendered by the website's `addons` role)

| Variable | Store | Value on the lab host |
|---|---|---|
| `PORT` | `addons[].env` | `8080` |
| `CA_FRAME_ANCESTORS` | `addons[].env` | `https://hybridcloudworks.com https://www.hybridcloudworks.com` |
| `CA_SITE_ORIGINS` | `addons[].env` | `https://hybridcloudworks.com https://www.hybridcloudworks.com` |
| `CA_ALLOWED_ORIGINS` | `addons[].env` | empty (the pane is same-origin with its API) |
| `CA_TRUST_PROXY` | `addons[].env` | `1` (the host's reverse proxy sets `X-Forwarded-For`) |
| `CA_TURNSTILE_SITE_KEY` | `addons[].env` | the widget's public site key |
| `TURNSTILE_SECRET` | vault | `vault_addon_cloud_assessment_turnstile_secret` (`secret_env`) |
| `CA_ALLOW_NO_TURNSTILE` | never set on the host | absent (fail closed) |
| `CA_TTL_MINUTES`, `CA_MAX_ITEMS`, `CA_RATE_LIMIT_POSTS`, `CA_RATE_LIMIT_WINDOW_MINUTES`, `CA_MAX_CONCURRENT` | `addons[].env` | defaults `120`, `200`, `10`, `10`, `2` |
| `CA_TELEMETRY` | image default | `0` (this edition emits nothing) |

## Copy rules for anything a visitor reads

No vendor or tool names on either side of the frame: not the host, the edge, the human-verification provider, the
workspace platform. Say "human verification" and "expires after two hours". The in-pane unavailable sentence is
exactly `This tool isn't available right now.` Status is shown in words (`Checking…`, `Ready`, `Assessing…`,
`Unavailable`), never by colour alone. `tests/e2e/lab.spec.ts` scans the pane's text for the forbidden words.

## Acceptance tests on the website side

Catalogue row validity and registry parity, `AddOnPanePage.test.jsx` (status gate, exact sandbox for
`['downloads', 'clipboard']`, `allow`, watchdog, message acceptance), `csp.test.js` parity, route completeness, public
copy with `data/addons` in its roots, the status proxy with a fake fetch answering this AddOn's health shape.
