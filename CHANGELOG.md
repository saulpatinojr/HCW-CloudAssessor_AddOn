# Changelog

All notable changes to this repository are recorded here. The format follows Keep a Changelog; versions are semver tags.

## [Unreleased]

### Security
- `core-update.yml` now runs from `main` only, and auto-merge no longer listens to the `bump` job's report. These are
  two High findings from a review of the same two-job workflow in the MigrateOrchestrator add-on
  ([its pull request 57](https://github.com/saulpatinojr/HCW-MigrateOrchestrator_AddOn/pull/57#discussion_r4430793870)),
  and they apply here as merged in pull request 67.
  - Main only. A person with write access could start the workflow by hand on another branch
    (`gh workflow run core-update.yml --ref` with any branch name other than `main`), and the `pull-request` job would
    then run that branch's
    `scripts/adopt_core_wheel.py` before minting the App token. Now the first step of each job stops the run with an
    error that names the branch unless it was started on `refs/heads/main`, the `pull-request` job's `if:` also
    requires `main`, and both checkouts take the exact commit the run was started for (`github.sha`).
    `create-pull-request` is told `base: main`, which it needs when the checkout is a commit. The `bump` job has no
    job-level `if:` on purpose, so a refused run shows as failed rather than skipped.
  - Auto-merge. The outcome file comes from the job that ran upstream code, so a compromised release could rewrite it
    to `success`. Auto-merge now needs the repository variable `CORE_AUTOMERGE` to be `true`, a run that is not a
    probe, and the `pull-request` job's own byte-for-byte check; it never reads the outcome. GitHub merges only after
    the "Protect main" ruleset's required checks (`lint`, `test`, `image`, `package`, `e2e`, `catalog-check`,
    `pip-audit`, `secret-scan`, `dependency-review`) pass on the bump pull request itself. The outcome still picks the
    label, the title and the body text, so when `CORE_AUTOMERGE` is `true` a `needs-adaptation` bump also has
    auto-merge turned on and merges once its checks pass (normally after someone fixes it on its branch); select
    **Disable auto-merge** on the pull request to hold one.
  - `tests/security/test_core_update_app_token.py` checks both guards. `docs/whats-new-upstream.md`, `VALIDATION.md`, a
    dated note on the ADR-0028 copy and the workflow's own comments now say the same: only a bump whose required checks
    pass merges, and the outcome picks only the label, the title, the body text and the not-compatible warning. Not run
    on GitHub yet; see `VALIDATION.md`.

### Changed

- The engine update to `v0.2.1` is now set up to happen by itself. The engine (`cloud-assessor-core`) is written in
  `HCW-CloudAssessor_App` and released there as a wheel (a ready-to-install package file); this repository still ran
  the old local copy, the seed under `packages/cloud-assessor-core`. The dependency line in `pyproject.toml` now carries
  the marker `CORE_REF v0.1.0-seed`, and `core-update.yml` (every six hours, or by hand) treats a pin that ends in
  `-seed` as the first adoption: `scripts/adopt_core_wheel.py` rewrites the line to the `v0.2.1` wheel's URL and removes
  the workspace entries and the Dockerfile and `.dockerignore` lines for the seed, `git rm -r` deletes the seed, and
  `uv lock` downloads the wheel and records its sha256 in `uv.lock`. The App's GitHub App token then opens the pull
  request, so the required checks run on it, and with `CORE_AUTOMERGE=true` it is queued for auto-merge, which waits
  for those checks (since the Security entry above, for every bump, `compatible` or not).
  This is done by the workflow because the wheel's sha256 can only enter `uv.lock` through `uv lock`, which needs to
  download the release asset. Each bump now also regenerates `docs/rules/catalog.md`, so the drift check in `ci.yml`
  passes when a release changes the catalog. Refs saulpatinojr/HCW-MigrateOrchestrator_AddOn#50.
- Made ready for the wheel without changing behaviour today (the bump pull request cannot change workflows, so these
  had to come first): `scripts/check-catalog.py` reads the catalog the installed engine loads and prints `cost-evidence`
  checks; `tests/unit/test_api.py` compares the catalog version with the installed catalog; the edition-boundary tests
  scan the engine wherever it is installed and check its declared requirements; `pyproject.toml` allows a direct
  (URL) reference, which hatchling otherwise refuses; `security.yml` leaves the engine out of `pip-audit`, which cannot
  find it on PyPI (`--strict` would fail, checked locally), as the seed already was; `ci.yml` and the `Makefile`
  measure `packages/` only while the seed's tracked `pyproject.toml` exists. `tests/unit/test_adopt_core_wheel.py` runs
  the script and the workflow's own steps against copies of the real files. `repository.manifest.json` no longer lists
  seed files, and the `ruff.toml` ignore for the seed's tests is gone (it ignored a rule that is not selected).
- `core-update.yml` is split into two jobs after an independent review. `bump` runs this repository's scripts and the
  new engine's code with no secret and uploads the result as an artifact; `pull-request` runs no project code, accepts
  only the five bump paths and deletions under the seed, applies them, and only then mints the GitHub App token. Before,
  upstream code ran in the same job that later received the App's key, and a step can reach later steps of its job.
  The compatibility outcome now only picks the label and title; auto-merge needs `CORE_AUTOMERGE` (and, since the
  Security entry above, no longer reads the outcome). Both tags must
  be `v<major>.<minor>.<patch>` before anything is written to the step outputs, and later bumps move the pin with an
  exact replacement (`scripts/adopt_core_wheel.py --bump`) instead of a `sed` script, which a crafted tag could have
  turned into a shell command through GNU sed's `e` flag. `scripts/check-catalog.py --write-schema` writes only the
  seed's catalog (the in-project `.venv` is inside the repository, so it had written into an installed release). The
  edition-boundary tests forbid the engine to import a network module, and the health test reads the catalog version
  from `criteria.json` directly instead of through the loader the route itself uses.
- The `pull-request` job of `core-update.yml` no longer trusts the artifact's contents (Copilot review of pull request
  67). Code in the `bump` job could have rewritten any of the five allowed files before they were collected. The job now
  regenerates the bump itself with main's `scripts/adopt_core_wheel.py` and `uv lock --no-build` (uv installed by
  version and sha256), and refuses the artifact unless `pyproject.toml`, `uv.lock`, the Dockerfile, `.dockerignore` and
  the deletions are byte-identical. `docs/rules/catalog.md` is the only file taken from the artifact, and only as plain
  Markdown; the bump pull request's `catalog-check` proves it matches the engine. Both jobs lock with `--no-build`.
- The `image` job in `ci.yml` checks that the built image runs the Python that `infrastructure/docker/versions.env`
  names as `BASE_PYTHON_VERSION`, so a base digest that is not that Python fails the pull request
  ([saulpatinojr/HCW-HybridCloudWorks#1386](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1386)).

## [0.1.1] - 2026-10-27

This release exists so that the image on Docker Hub states its licence. The image
`docker.io/hybridcloudworks/img-ca-lab-addon` now carries the label `org.opencontainers.image.licenses=MIT`. (A label is a
small note stored inside an image. Registries and scanners read this one to learn which licence the software is under,
and the ticket for this release notes that Docker's free open-source programme checks it.) The label has been in the
Dockerfile since [pull request 44](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/44), but a label reaches
Docker Hub only when a tag is pushed, and the newest tag so far, `v0.1.1-rc.1`, was built before the label was added
([ticket 47](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/issues/47)). `v0.1.1` is the first tag that includes
it.

The application's own code did not change since `v0.1.0`: `src/`, the pane (`web/`), the API description
(`docs/api/openapi.yaml`) and the samples are identical, and the engine seed (`packages/cloud-assessor-core`) differs only
in one dependency range in its `pyproject.toml`. What changed is what the image is built from (a newer base image and
four newer libraries) and the automation around it. Because the libraries are part of what runs, it is the test suite
(`VALIDATION.md`, run 2026-10-27) and the in-image checks that CI and the publish run make that show behaviour is the same.

The version moves from `0.1.0` to `0.1.1` in `pyproject.toml`, in `uv.lock` (the `cloud-assessment-lab` entry only), in
`__version__` (`src/cloud_assessment_lab/__init__.py`) and in `repository.manifest.json`, so `/api/health` and the
`X-Addon-Version` header say `0.1.1`. The engine seed keeps its own version, `0.1.0`, and `docs/api/openapi.yaml` keeps
`info.version: 0.1.0`, because that field is the version of the API document and the API has not changed. The image was
published on 2026-10-27 by the tag `v0.1.1` (digest `sha256:95082857e3b866743ffa5c827c7b897d085e945d80aa4b710f58926b03170456`;
[release](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/releases/tag/v0.1.1)).

In short, since `v0.1.0`:

- The image states its licence, as above ([pull request 44](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/44)).
- The image is built on Python 3.14.8 (it was 3.14.7) and four of its libraries are newer: FastAPI 0.143.0 to 0.162.0,
  Starlette 1.7.0 to 1.9.0, pydantic 2.14.0 to 2.14.1 and pydantic-core 2.50.0 to 2.50.1 (pull requests
  [17](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/17) and
  [43](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/43), and the Dependabot updates in `git log v0.1.0..main`).
- The Docker Hub repository is named `img-ca-lab-addon` (it was `hcw-addon-cloud-assessment`), and a crafted tag name can
  no longer inject a command into the last step of the publish workflow ([pull request 38](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/38)).
- The base image now follows the website's pin by itself: a daily workflow opens a pull request when the website moves,
  and a person still reviews and merges it ([pull request 49](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/49)).
- A manual run of the publish workflow (`publish-images.yml`) is now a true dry run: it builds, checks and scans the image
  but never pushes, because only a `v*` tag does. Before, a manual run on `main` went on to the Docker login
  ([pull request 60](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/60)).
- The engine-update workflow (`core-update.yml`) opens its pull request through the HCW Main Admin GitHub App, so this
  repository's required checks run on that pull request ([pull request 42](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/42)
  and [pull request 45](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/45)). It does nothing yet: the
  repository has not pinned an upstream engine release (`pyproject.toml` has no `CORE_REF` line).
- A weekly check compares this repository's integration guide with the website's catalogue row ([pull request 41](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/41)).
- Dependabot uses the `uv` ecosystem, so one dependency pull request updates `pyproject.toml` and `uv.lock` together
  ([pull request 17](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/17)).

The entries below are the detail.

### Added
- `.github/workflows/guide-drift.yml` switches on the website's check that this repository's integration guide still says what the website says (website issue saulpatinojr/HCW-HybridCloudWorks#1356). It calls a reusable workflow (a workflow that another repository can call, like a function) from the website repository, pinned to a full commit, and compares the catalogue row pasted into `docs/website-integration/integration-guide.md` with the website's row for `cloud-assessment`, field by field. It runs on pull requests that touch the guide or this workflow, every Monday at 06:35 UTC and on demand. It holds no secret and has `contents: read` only. To switch it off, delete the file. How to read a failure: https://github.com/saulpatinojr/HCW-HybridCloudWorks/blob/main/docs/runbooks/addon-guide-drift.md
- `.github/dependabot.yml` groups `pydantic` and `pydantic-core` so they arrive in one pull request. pydantic requires one exact `pydantic-core`, so a `pydantic-core` bump on its own cannot resolve; the same failure closed the App repository's Dependabot pull requests.
- The base image now follows the website's pin by itself, so nobody has to remember to move it. `.github/workflows/base-update.yml` runs once a day (and on demand), compares `infrastructure/docker/versions.env` with the website's `lab-image/versions.env` and, when they differ, opens one pull request that moves `versions.env` and every external `FROM` line together. A person still reviews and merges that pull request; nothing is merged automatically. How it works: the run reads the website's file at one recorded commit; `scripts/follow_website_base.py` (tests: `tests/unit/test_follow_website_base.py`) checks each value against a strict pattern, refuses a key that appears twice, and edits only those two files; before the pull request is opened, the run asks the registry whether the new digest is an index (one entry that lists every platform) with every platform the old digest had, and the pull request says whether that comparison could be made (it cannot when the registry no longer shows the old digest; then only `linux/amd64` is checked). While a pull request from the run is open and its branch already holds the website's pin, the daily run leaves it alone, so a fix a person pushed to it is not overwritten; when the website moves again the branch is rebuilt, and when the pin is no longer needed the run closes the pull request by deleting its branch. The script stops, and the run goes red with nothing opened, for a different image repository, a different Python minor line (3.14 to 3.15) or a Dockerfile it cannot move completely, because those need a person's decision; `docs/operations/runbook.md` says what to do for each. The pull request is opened by the HCW Main Admin GitHub App exactly as `core-update.yml` does it (repository variable `HCW_MAIN_ADMIN_CLIENT_ID`, repository secret `HCW_MAIN_ADMIN_PRIVATE_KEY`, no environment), so this repository's required checks run on it, and its commit is credited to the App's bot user. `tests/security/test_base_update_workflow.py` pins that credential handling down and runs the two decision scripts against stand-ins for `docker` and `gh`; these are checks made before the first real run, which is the live proof (runbook, "Keeping the base image on the website's pin", and `VALIDATION.md`). `tests/unit/test_base_image_pin.py` fails if `versions.env` and a `FROM` line ever disagree, in the regular `pytest` run as well as in the `lint` job of `ci.yml`. `versions.env` no longer names a Python version in its header comment, because an automatic move would leave that sentence out of date. Background: the website bumped its pin on 2026-10-21 and this repository's `base-follows-website` check then sat red on `main` until a person fixed it by hand ([saulpatinojr/HCW-HybridCloudWorks#1386](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1386)); that job stays as the second line of defence.
- `docs/whats-new-upstream.md`: a running note of what the App released and changed that reaches this edition (current upstream state, the two releases not yet adopted, the compatibility trial, the adoption steps, and open upstream decisions). `CLAUDE.md` and `docs/README.md` point to it.

### Changed
- The lab image repository on Docker Hub is renamed from `hybridcloudworks/hcw-addon-cloud-assessment` to `hybridcloudworks/img-ca-lab-addon` (owner naming convention `img-<short name>-<job>-<type>`, 2026-10-25), and its tag is now the full release tag (`v0.1.0`, not `0.1.0`). `publish-images.yml` (`IMAGE`, the tag, the image title label), the local `:dev` build tag, the README and the deployment and integration documents follow. The container name on the lab host (`hcw-addon-cloud-assessment`) is **not** changed: the website's host role owns it. Nothing is published by this change; the next `v*` tag pushes to the new name once the Docker OIDC connection allows it (`docs/deployment/lab-host.md`, step 4).
- Hardening: the last step of `publish-images.yml` printed the release version straight into a shell command (`echo "image_tag: ${{ steps.version.outputs.version }}"`). The version comes from the pushed tag's name, so a crafted tag name could inject a command. It now reaches the shell through the environment variable `IMAGE_TAG` and is printed as `"${IMAGE_TAG}"`. This was already present before the rename; only people with write access can push tags.
- `core-update.yml` opens its bump pull request with a short-lived GitHub App token (`actions/create-github-app-token`, pinned to v3.3.0; the HCW Main Admin App, installed on this repository: its client ID is the repository variable `HCW_MAIN_ADMIN_CLIENT_ID`, which is not a secret, and its private key is the repository secret `HCW_MAIN_ADMIN_PRIVATE_KEY`, which is never printed; the job no longer runs in an environment) instead of `GITHUB_TOKEN`. The token step names this repository (`repositories: ${{ github.repository }}`) and sets no `owner`, so even an empty value could only fall back to this repository, never to every repository the App is installed on. Why: a pull request opened with `GITHUB_TOKEN` starts no workflow, so the required checks of the `Protect main` ruleset would never run on it and it could not merge. The token is minted for this repository only, with Contents and Pull requests write, after the compatibility check and just before the pull request is opened; `GITHUB_TOKEN` is now `contents: read` only. Because the App's pull request starts this edition's own CI, the "do not trigger other workflows" comment is gone; the compatibility check in the run still decides the label and whether auto-merge is requested. Turning on auto-merge no longer fails the run when the repository setting "Allow auto-merge" is off; it warns and leaves the pull request to merge by hand. A manual run with `probe=true` mints the token, makes a read-only call and lists the repositories the token covers (the run fails unless that is this repository only), and opens no pull request and asks for no auto-merge even when a newer release exists, to prove the credential while the workflow is still inert (no `CORE_REF` line yet). `tests/security/test_core_update_app_token.py` pins all of it (no `GITHUB_TOKEN` passed to `create-pull-request`, the token step first, the HCW Main Admin variable and secret, the token limited to this repository, exactly the two permissions, SHA pins, and none of the old credential names left). To rotate the key, generate a new private key on the settings page of the App (https://github.com/settings/apps), replace the repository secret `HCW_MAIN_ADMIN_PRIVATE_KEY` in every repository that holds the key (this one: https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/settings/secrets/actions; the App is installed on the four add-on repositories, so check the other three), then delete the old key on the settings page of the App. The settings page can hold several keys, so a separate key per repository lets you revoke one without touching the others.
- `docs/website-integration/integration-guide.md` follows the website after hybridcloudworks.com#1359 (issues #1353 and #1354, owner decisions of 2026-10-24): the row now holds `downloads` and `clipboard-write` (it held `navigate` and `downloads`), the frame address carries `?theme=dark|light` read once from the site's theme, the clipboard grant is write only, and the row copy is taken from website commit b0cf0055.
- `docs/website-integration/integration-guide.md` now follows the website's real catalogue row. The row pasted into it was
  written before the row shipped and had drifted: 5 of its 10 fields differed from the website's (summary, pane path,
  technology, status and capabilities, plus the `comingSince` and `comingReason` fields). The block is now a copy of the
  website's current row, with the website commit it came from, and says the website is the authority. The guide also
  says that the site frames `origin + panePath` with no `?theme=` parameter (the pane still honours one), and that the
  site grants `navigate` and `downloads` where this AddOn asked for `downloads` and `clipboard`; the owner confirms
  whether that is intended. Compared field by field with a script on 2026-10-24: 0 of 10 now differ.
- **Documents say who owns the engine.** `CLAUDE.md`, `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, the pull request template and `.github/copilot-instructions.md` still said the engine is "seeded here and moves upstream" and "edited here until the App adopts it". The App adopted it (its "Engine adopted" entry) and has released it as `v0.2.0` and `v0.2.1`, so they now say the App owns it and the seed here is not edited until it is replaced by the release wheel. `ADR-0001` is left as written (a historical record). Documents only; no code, test or dependency changed.
- Dependency updates pass CI as Dependabot opens them. Its `pip` updater rewrote `pyproject.toml` and the committed
  `requirements.lock.txt` but never `uv.lock`, so every one of its pull requests failed the export check (#12 to #15).
  `.github/dependabot.yml` now uses the `uv` ecosystem, which moves `pyproject.toml` and `uv.lock` together. The
  committed export is gone: the image's build stage runs `uv export --frozen` from `uv.lock` with the uv CI uses, by
  digest, and still installs with `pip --require-hashes --no-deps`; uv never reaches the lab stage. CI checks
  `uv lock --check` and that the Dockerfile's uv is `UV_VERSION`; `pip-audit` audits the same export. The engine
  declares `pydantic>=2.14,<3` (the app keeps the exact pin), so the two cannot be bumped apart while the engine is
  the seed; the App's engine must carry the same range before its wheel is adopted (HCW-CloudAssessor_App#15).
  CI builds the image on every pull request, resolves the uv digest for `UV_VERSION` rather than trusting any
  digest, and a weekly job flags the base drifting from the website's pin.
- Base image `python:3.14.8-slim-trixie` by digest, the website's current pin (CONTRACT-DECISIONS item 20). There is
  no docker Dependabot entry: the base follows the website, and the uv image follows `UV_VERSION`.
- The base image digest follows the website's current pin again (`python:3.14.8-slim-trixie@sha256:fbecd461...`, same
  tag, newer build; `versions.env` and both `FROM` lines). The website rebuilt on it on 2026-10-21; `security.yml`'s
  `base-follows-website` job, which runs on `main` and weekly only, had been red on `main` since its first run after
  that (2026-10-23). An image built from the next tag uses the current base; a tag already published keeps the base
  it was built on.
- The lab image states its open-source licence in the form registries and scanners read.
  `infrastructure/docker/Dockerfile` sets `org.opencontainers.image.licenses="MIT"` on the final stage (the SPDX id
  of `LICENSE`, the MIT License). The `image` job in `ci.yml` fails when the built image lacks the label or `LICENSE`
  stops being MIT, and the pre-publish check in `publish-images.yml` fails when the image about to be pushed lacks it.
  The `labels:` input of `publish-images.yml` must not set this label: it would override the Dockerfile's. The image
  tags on Docker Hub on 2026-10-26 (`0.1.0`, `v0.1.0` and `v0.1.1-rc.1`) were built without the
  label and are not changed; the label reaches Docker Hub with the next tagged release, which is `v0.1.1`.
- Libraries in the image, by Dependabot pull requests (checked by comparing the committed `requirements.lock.txt` at
  `v0.1.0` with what `uv export --no-dev` prints now): four of the fourteen third-party packages the image installs
  moved, FastAPI 0.143.0 to 0.162.0, Starlette 1.7.0 to 1.9.0, pydantic 2.14.0 to 2.14.1 and pydantic-core 2.50.0 to
  2.50.1. The other ten did not move. Other locked packages that are not in the image (for example ruff 0.17.0 to 0.17.2,
  coverage and certifi) also moved. The engine seed's `pyproject.toml` now allows `pydantic>=2.14,<3` where it said
  `pydantic==2.14.0` (see the Dependabot entry below for why); the seed's version stays `0.1.0`.

## [0.1.0] - 2026-10-11

The first tagged release (tag `v0.1.0`, commit `6cd7ab6`, 2026-10-11). The entries below are the ones that file held at that
tag, word for word; everything added to this file after the tag is under 0.1.1.

### Changed
- Repository hygiene: `.github/dependabot.yml` groups GitHub Actions updates under `all-actions` and removes the unused `/tests/e2e` npm entry; `tests/unit/test_config.py` and `tests/unit/test_edition.py` use `as_posix()`, `os.pathsep`, and `SYSTEMROOT` forwarding for cross-platform Windows/Linux test parity.
- `core-update.yml`'s checkout no longer persists credentials: two Authorization headers made GitHub answer `400` to `create-pull-request`'s push (reproduced twice in the Migrate App's `rules-refresh`, fixed there in saulpatinojr/HCW-AzMigrateOrchestrator_App#24).
- README: a "where to try it" paragraph for new visitors; the relationship diagram and text say the App now holds the engine and the seed here is deleted at its first release.
- `core-update.yml` pins the upstream engine as the GitHub Release wheel asset by URL, so `uv lock` records its sha256 and the image's `pip install --require-hashes` keeps verifying it; the `git+https` form it described before cannot be hash-checked by pip and would have broken the image build on the first adoption. No PyPI step is needed (ADR-0001 amended).
- Code scanning: the e2e host page accepts only a loopback `?addon=` origin for the frame and the message filter, and the unit test asserts the exact `script-src` and `frame-src` source lists instead of a substring (closes the three CodeQL alerts raised on #5; test and harness code only, no runtime change).
- Cross-AddOn standardization (program Phase 5D): the concurrency-cap answer is `503 overloaded` (was `busy`), the code
  the Azure Migrate AddOn already uses; log event renamed to match.
- Numeric settings are bounded to 1,000,000,000 (`MAX_SETTING`), so an absurd value cannot push a TTL, window or
  bucket into arithmetic the clocks cannot represent; mirrors the Azure Migrate AddOn's safe-integer rule.

### Added
- Engine seed `packages/cloud-assessor-core` 0.1.0 (pydantic only): `Resource` model (`MODEL_VERSION = 1`), JSON-path-lite,
  `arg-json` / `arg-csv` ingestion (array or `az graph query` envelope with the paged warning; Resource Graph Explorer
  CSV with JSON cells; portal "All resources" CSV accepted with the "no properties column" warning; BOM strip, delimiter
  sniff, formula neutralisation, row caps), catalog loader with a generated JSON Schema (draft 2020-12) drift check and a
  `learnUrl` host allow-list, six evaluator kinds (`tag-present`, `property-equals` with `anyOf`, `property-exists`,
  `sku-in`, `count-threshold` resource/estate, `cross-resource` has-child/estate-has/has-sibling) with `when`
  applicability, `missingIs` and `anyPass`, severity- and pillar-weighted scorecards where unknown lowers coverage and
  never score, `report.md`, `report.json`, `findings.csv` (neutralised), `NOT-AN-AUDIT.md`, `bundle.zip` (STORE), and
  the log-path redaction guard.
- Catalog 1.0.0: 25 paraphrased, attributed criteria (`CA-FIN-001..007`, `CA-WAF-001..007`, `CA-ZT-001..011`) with
  `verify: true` and `retrievedOn: 2026-10-10` on every reference link; `scoring.json`.
- Lab application `src/cloud_assessment_lab` 0.1.0 (FastAPI 0.143.0, uvicorn 0.54.0, pydantic 2.14.0): `CA_*` settings,
  import-time edition guard (no cloud SDK importable, refusal under identity endpoints, a `sys.meta_path` finder that
  refuses `azure`, `msal`, `boto3`), in-memory store (UUID4, hashed owner tokens, TTL sweep, eviction), human
  verification with `action` echo and fail-closed posture (`CA_ALLOW_NO_TURNSTILE=1` for local use only), security
  headers with configurable `frame-ancestors`, exact-origin CORS, 5 MB streamed cap, 5,000 rows, per-client token bucket
  (`CA_TRUST_PROXY` for `X-Forwarded-For`), concurrency bound, content-free JSON logs, the flat `/api/health` envelope
  and the documented route set with the error envelope.
- Vanilla pane (`web/`) with the HCW theme tokens copied with provenance, `?theme=` selection, the `hcw-addon` message
  bridge (`loading | ready | working | unavailable`), upload preview, scorecards with coverage sentences, filterable
  findings, detail panel, "Unknown by design" panel, bundle download, "Copy report" fallback and immediate delete.
- Samples (40 fictional rows in three export shapes) with pinned expected results; unit, contract (OpenAPI two-way),
  security (edition boundary, no secrets, content-free logs), manifest and Playwright suites (standalone and framed).
- Docs (website integration, routes, API, lab host, appliance pointer, runbook, threat model, user guide, bundle,
  generated criteria catalog, ADR-0001..0003 and copies of upstream ADR-0008/0011/0028), hardened two-stage Dockerfile
  on the website's base-image digest, local compose, SHA-pinned `ci`, `security`, `publish-images` (Docker Hub by OIDC,
  Trivy before push, image-level boundary check) and inert `core-update` workflows, Dependabot, CODEOWNERS, PR template.
