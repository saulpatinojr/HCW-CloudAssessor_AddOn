# Validation

What was executed for this edition and what was not, per run. "Here" is the authoring container (no Docker daemon, PyPI
and the Playwright CDN reachable through a proxy). Dates are the run date.

## Run 2026-11-14, second part (round four of the workflow runtime check; HCW-HybridCloudWorks#1707)

`tests/security/test_workflow_runtime_setup.py` takes round four of the check from the canonical Python copy in HCW-NetworkEyes_App (`0b28c39` on its branch `claude/runtime-round4-1707`, [HCW-NetworkEyes_App#403](https://github.com/saulpatinojr/HCW-NetworkEyes_App/pull/403)), which is kept the same as the website's copy (merged as `95b2aac5`, [HCW-HybridCloudWorks#1725](https://github.com/saulpatinojr/HCW-HybridCloudWorks/pull/1725); issue [HCW-HybridCloudWorks#1707](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1707)). Only this repository's own lists differ, and the wrapping of the lines that ran past this repository's 120 columns: the new made-up workflows are written as adjacent strings, which Python joins into the same value, and one docstring line is wrapped one word earlier. Run from `main` at `28850d5`. Toolchain: Linux cloud session, CPython 3.15.2, uv 0.13.8.

| Check | Executed here | Result |
| --- | --- | --- |
| The port's code against HCW-NetworkEyes_App's copy at `0b28c39` | yes | identical syntax trees once the docstrings and the four lists (`RUNNER_DEFAULT_ALLOWED`, `INDIRECT_RUNTIME`, `PIPX_ALLOWED`, `BELOW_FLOOR_ALLOWED`) are set aside, as on `main` against the canonical copy before round four; the same 109 test functions in the same order; the module docstring has the same words, except the paragraph saying this file is a copy |
| `uv sync --all-packages`, `ruff check .`, `ruff format --check .`, `python scripts/check-catalog.py` | yes | `Checked 51 packages`; `All checks passed!`; 58 files already formatted; catalog 1.1.0, 25 criteria |
| `pytest -q --cov=src` | yes | 1520 passed; coverage 96.01%. `tests/security/test_workflow_runtime_setup.py` alone: 1129 passed (1049 before) |
| The same answers as the canonical copy | yes | the 60,632 generated cases of round four and its review rounds (command reading, `sudo` reading, `pipx`, the floor, `shell:` words, and made-up workflows read for unset steps, `pipx` problems and floor problems): 0 disagreements with HCW-NetworkEyes_App's copy at `0b28c39`, and none between the three add-ons' copies |
| The check over the workflows of every HCW clone in this session (23 folders, these round-four copies included) | yes | the same findings as the canonical copy's, folder by folder, and the same as the canonical copy before round four; here, no step reported, no `pipx` problem, no set-up step below the floor |
| gitleaks (the secret scan `security.yml` runs) | **no** | not installed here; `tests/security/test_no_secrets.py` ran in the suite above |
| actionlint, zizmor, and CI on GitHub | **no** | no workflow changed; CI runs when the pull request is opened |
| `make e2e` | **no** | this change touches neither the pane nor the API |

## Run 2026-11-14 (round three of the workflow runtime check; HCW-HybridCloudWorks#1707)

`tests/security/test_workflow_runtime_setup.py` is replaced by round three of the check, from the canonical Python copy in HCW-NetworkEyes_App (merged as `9b96396`, [HCW-NetworkEyes_App#399](https://github.com/saulpatinojr/HCW-NetworkEyes_App/pull/399)), which is kept the same as the website's `scripts/workflow-runtime-setup.test.mjs` (merged as `4be949f`, [HCW-HybridCloudWorks#1722](https://github.com/saulpatinojr/HCW-HybridCloudWorks/pull/1722); issue [HCW-HybridCloudWorks#1707](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1707)). Only this repository's own lists differ, and the wrapping of the docstring and comment lines that ran past this repository's 120 columns; the 17 one-line YAML texts the new tests feed the reader, which ran past 120 columns too, are written as adjacent strings, which Python joins into the same value. Run from `main` at `7e4750b`. Toolchain: Linux cloud session, CPython 3.15.2, the session's uv 0.11.32.

| Check | Executed here | Result |
| --- | --- | --- |
| The port's code against HCW-NetworkEyes_App's copy at `9b96396` | yes | the two files' syntax trees are identical once the docstrings and the four lists (`RUNNER_DEFAULT_ALLOWED`, `INDIRECT_RUNTIME`, `PIPX_ALLOWED`, `BELOW_FLOOR_ALLOWED`) are set aside; the four lists are the same as on `main`; the docstrings have the same words, except the module docstring's paragraph saying this file is a copy |
| `uv sync --all-packages`, `ruff check .`, `ruff format --check .`, `python scripts/check-catalog.py` | yes | `Checked 51 packages`; `All checks passed!`; 58 files already formatted; catalog 1.1.0, 25 criteria |
| `pytest -q --cov=src` | yes | 1291 passed, none skipped; coverage 96.01%. `tests/security/test_workflow_runtime_setup.py` alone: 901 passed (699 before), at this pull request's first push; after the fixes below, 1439 passed and 1049 in that file |
| The check over this repository's workflows, old copy (`main`) against new | yes | the same findings as the copy on `main`, file by file (6 workflows, no composite action): no step reported, no `pipx` problem, no set-up step below 3.15 or 26. Its lists stay empty |
| The same answers as the canonical copy | yes | the 12,975 cases of the round-three harness, the 348 inputs of the round-three review, the 66,583 cases of round two and the 199 cases of the round-three case files (command reading with its two shell texts and the `sudo` reading, the `pipx` check, the condition rules, and made-up workflows read for unset steps, `pipx` problems and floor problems): 0 disagreements with HCW-NetworkEyes_App's copy at `9b96396`, and none between the three add-ons' copies |
| The name `UNSET`, which round three gives to a marker for an unset variable and which the end of the file reuses for the list of reported steps | yes | the same as the canonical copy, kept as it is there. Every use of the marker compares by identity, and on the 49,652 `pipx` and workflow cases above the canonical copy gives the same answers with the marker as a fresh object, as an empty list and as the list it ends up as |
| The website's JavaScript copy driven over the same cases | **no** | the canonical copy's own run reports the two agree on these case sets |
| After Copilot's review of the round-3 pull requests, a review of those fixes and Copilot's second round: the fixes from HCW-NetworkEyes_App `ef14b90` (a `sudo` inside a script `sudo` runs), `82b9258` (five more), `2de76af` (`env -u PATH`, `command -p`, free-threaded names), `55e94dd` and `85fe01c` (the second round), against the canonical copy at `85fe01c` | yes | identical syntax trees once the docstrings and the four lists are set aside, as before; the new made-up workflows and refused texts are written as adjacent strings |
| After the reviews: `ruff check .`, `ruff format --check .`, `pytest` as above | yes | `All checks passed!`; 58 files already formatted; 1439 passed, none skipped; coverage 96.01%. The file alone: 1049 passed (901 before these fixes). The new tests and changed cases, each added to the file as it was before them: 49 of 86 fail for the first six fixes, 25 of 41 for the review's (its longer timing test among them), 19 of 1049 for Copilot's second round |
| After the reviews: the same answers as the canonical copy | yes | the 49,200 generated cases of these changes, the 4,844 nested-sudo cases and the 348 inputs of the round-three review: 0 disagreements with HCW-NetworkEyes_App's copy at `85fe01c`, and none between the three add-ons' copies; of the 348, one answer moved with the pre-PR review's fix and moved back with Copilot's second round (`pipx run --python python3.15t x` is reported again) |
| After the review: the check over the workflows of all nine HCW repositories | yes | the same findings before and after the change, and the same as the canonical copy's, repository by repository |
| gitleaks (the secret scan `security.yml` runs) | **no** | not installed here; `tests/security/test_no_secrets.py` ran in the suite above |
| actionlint, zizmor, and CI on GitHub | **no** | no workflow changed; CI runs when a pull request is opened |
| `make e2e` | **no** | this change touches neither the pane nor the API |

## Run 2026-11-13, sixth part (uv 0.13.8; HCW-HybridCloudWorks#1707)

uv (the tool that installs the Python packages and keeps `uv.lock`) moves from 0.13.7 to 0.13.8 in `ci.yml`, `security.yml`, `core-update.yml` and the Dockerfile's uv image ([HCW-HybridCloudWorks#1707](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1707)). 0.13.8 is a patch release with no change to the lock format ([release notes](https://github.com/astral-sh/uv/blob/0.13.8/CHANGELOG.md)). Run from `main` at `e41a06d`. Toolchain: Linux cloud session, CPython 3.15.2, uv 0.13.8 installed with `pip` into a throwaway virtual environment outside the repository, and uv 0.13.7 from another for the comparisons.

| Check | Executed here | Result |
| --- | --- | --- |
| The uv image digest: an anonymous `HEAD` of `https://ghcr.io/v2/astral-sh/uv/manifests/0.13.8` asking for an image index | yes | `Docker-Content-Digest: sha256:5cc1805e2426484abca4ad46ea783bab281fdb225fd82d8ce6d66a81254bac85`, content type `application/vnd.oci.image.index.v1+json` (the multi-platform index, which is what `docker buildx imagetools inspect` prints in `ci.yml`) |
| `ci.yml`'s uv check replayed (the `grep -Fq` lines, with the digest above in place of `docker buildx`) | yes | the Dockerfile line and the `"uv==0.13.8"` lines in `security.yml` and `core-update.yml` all match |
| The uv wheel hash in `core-update.yml`'s pull-request job | yes | `pip download --no-deps --only-binary=:all: --platform manylinux_2_17_x86_64 uv==0.13.8` gives `uv-0.13.8-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` with sha256 `e18a57b8b352eb7c8feb317b9f6f533c8f0ad9673fd6cf34bbe3cf1a9f6a8984` |
| `uv lock --check` with uv 0.13.8, with the session's cache and again with an empty cache | yes | exit 0 both times. The `401` on the engine wheel's address recorded in the 0.13.7 run did not come back: the `[[tool.uv.dependency-metadata]]` entry means uv has nothing to ask that address |
| `uv lock` with uv 0.13.8 on a scratch copy | yes | `Resolved 52 packages`; `uv.lock` byte-identical to the committed one |
| The image's `uv export` (the Dockerfile's flags) and `security.yml`'s export, under uv 0.13.7 and 0.13.8 | yes | byte-identical in both cases (98 and 95 lines) |
| `uv sync --all-packages`, `ruff check .`, `ruff format --check .` | yes | `Checked 51 packages`; `All checks passed!`; 58 files already formatted |
| `python scripts/check-catalog.py` | yes | exit 0, catalog 1.1.0, 25 criteria |
| `pytest -q --cov=src` | yes | 1089 passed, none skipped; coverage 96.01% (includes `tests/security/test_core_update_app_token.py`, which checks that the hashed uv in the pull-request job is the same version as the bump job's) |
| actionlint 1.7.12 and zizmor 1.31.1 `--offline` on the three changed workflows, hadolint 2.14.0 on the Dockerfile (the hadolint binary checked against the sha256 in `ci.yml`) | yes, actionlint without shellcheck | no findings from any of them (zizmor: 2 ignored, the lines `.github/zizmor.yml` names). shellcheck is not installed here; the shell lines changed only in a version number and a hash |
| The upstream engine wheel built with uv 0.13.7 and 0.13.8 (in the App, from its `main` at `bbf4e2e`, two scratch copies) | yes | wheel and source archive byte-identical under both versions (wheel sha256 `2e763e7a…12be`); recorded in the App's `CHANGELOG.md` too |
| Docker image build, and CI itself on uv 0.13.8 | **no** | no Docker daemon here; the pull request's CI run is the first real test |
| `make e2e` | **no** | this change touches neither the pane nor the API |

## Run 2026-11-13, fifth part (the engine seed's switch code removed; HCW-HybridCloudWorks#1707)

`core-update.yml`, `scripts/adopt_core_wheel.py` and `scripts/check-catalog.py` lose the code for the one-time switch from the local engine seed to the release wheel, which happened in [pull request 69](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/69) and could never run again; `ci.yml` reads `UV_VERSION` as a shell variable in its uv install steps ([HCW-HybridCloudWorks#1707](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1707)). Run from `main` at `9290d7c`. Toolchain: Linux cloud session, CPython 3.15.2, uv 0.13.7 from a throwaway folder outside the repository.

| Check | Executed here | Result |
| --- | --- | --- |
| `uv sync --all-packages`, `ruff check .`, `ruff format --check .` | yes | `Checked 51 packages`; `All checks passed!`; 58 files already formatted |
| `python scripts/check-catalog.py` | yes | exit 0, catalog 1.1.0, 25 criteria |
| `pytest -q --cov=src` | yes | 1088 passed, none skipped (the 10 seed-adoption tests that `main` skips are removed); coverage 96.01% |
| actionlint, and zizmor `--offline` with `.github/zizmor.yml` | yes | actionlint exit 0. zizmor: no findings, 2 ignored (the two Playwright install lines `.github/zizmor.yml` names by line number) |
| A real wheel-to-wheel bump replayed: the pin moved from `v0.3.0` to `v0.3.2`, the bump that [pull request 72](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/72) made on GitHub | yes | the bump job's bump and collect steps, run as written, produced only `pyproject.toml`, `uv.lock` and an empty `deleted.txt`; the pull-request job's apply step then exited 0 with outcome `success`, and the files it left were byte-identical to the real `v0.3.2` ones |
| Review follow-ups: a new test that both jobs refuse a pin written `v0.3.2-seed`, then `ruff check .`, `ruff format --check .`, `check-catalog.py` and `pytest -q --cov=src` again | yes | all clean; 1089 passed, coverage 96.01%. With `(-seed)?` put back into the refs step's pin check, the new test failed (the step accepted `v0.3.2-seed -> v99.0.0`); with it put back into the apply step's check only, it failed too (the script still refused the pin, but not with the step's own `the pinned CORE_REF is malformed`); with both, it failed. On the real file it passed. The workflow file was restored and compared byte for byte with a copy taken first |
| A real `core-update.yml` run on GitHub with the App token, and CI on GitHub | **no** | nothing was pushed; the next upstream release, or a probe run, is the first run of the changed workflow |
| `make e2e` | **no** | this change touches neither the pane nor the API |

## Run 2026-11-13, fourth part (round two of the workflow runtime check; HCW-HybridCloudWorks#1707)

`tests/security/test_workflow_runtime_setup.py` is replaced by round two of the check, from the canonical Python copy in HCW-NetworkEyes_App (commit `8ac3118`, with the fourth review round's fixes, [HCW-NetworkEyes_App#395](https://github.com/saulpatinojr/HCW-NetworkEyes_App/pull/395)), which is kept the same as the website's `scripts/workflow-runtime-setup.test.mjs` (merged as `9e2e0dd`, [HCW-HybridCloudWorks#1719](https://github.com/saulpatinojr/HCW-HybridCloudWorks/pull/1719); issue [HCW-HybridCloudWorks#1707](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1707)). Only this repository's own lists differ, and the wrapping of the docstring and comment lines that ran past this repository's 120 columns (the one long pattern, `ASSIGNMENT`, is written as two adjacent strings, which Python joins into the same value). Run from `main` at `ccfcd92`. Toolchain: Linux cloud session, CPython 3.15.2, uv 0.13.7 from a throwaway virtual environment outside the repository.

| Check | Executed here | Result |
| --- | --- | --- |
| The port's code against HCW-NetworkEyes_App's copy at `8ac3118` | yes | the two files' syntax trees are identical once the docstrings and the four lists (`RUNNER_DEFAULT_ALLOWED`, `INDIRECT_RUNTIME`, `PIPX_ALLOWED`, `BELOW_FLOOR_ALLOWED`) are set aside; the earlier canonical copy, as a control, differs |
| `uv sync --all-packages`, `ruff check .`, `ruff format --check .`, `python scripts/check-catalog.py` | yes | `Checked 51 packages`; `All checks passed!`; 58 files already formatted; catalog check clean |
| `pytest -q --cov=src` | yes | 1085 passed, 10 skipped (the seed-adoption tests, as on `main`); coverage 96.01%. `tests/security/test_workflow_runtime_setup.py` alone: 699 passed (354 before) |
| The check over this repository's workflows | yes | the same findings as the copy on `main`: no step reported that its lists do not name, no `pipx` step, no set-up step below 3.15 or 26, and no composite action to read. Its lists stay empty |
| The same answers as the canonical copy, and the JavaScript copies | yes | 66,627 cases (23,958 command readings, each with its two shell texts; 42,498 `pipx` cases; 171 condition cases), and the 104 files (100 workflows, 4 composite actions) of the nine HCW repositories cloned here plus two folders of made-up workflows for the new rules (jobs read, unset steps, `pipx` problems, floor problems): 0 disagreements with the canonical Python copy at `8ac3118` and between the five Python ports. The website's JavaScript copy (`9e2e0dd`) and the MigrateOrchestrator App's (`78feda5`) do not have the fourth round's fixes yet: they agree with the canonical copy as it was before them (`62ee0cc`) on every case, and differ from it now exactly on the 3,085 cases those fixes change (28 answers; the rest are how a GitHub expression is written in the shell text) and on the made-up workflow for them; the fixes reach them in their own pull requests |
| The new checks catch a real step | yes | in a scratch copy of the CloudCrawler add-on's `.github` (not this working tree), a job added to `ci.yml` with `PIPX_DEFAULT_PYTHON=/usr/bin/python3 pipx run zizmor .` and a literal `run: |` script running `node x.js`: 2 failed, naming both steps; the same `node` in a folded `run: >-` script is one line of text, as GitHub runs it, and is not reported |
| actionlint, zizmor, and CI on GitHub | **no** | no workflow changed, and nothing was pushed; the pull request's CI runs the test on GitHub |
| `make e2e` | **no** | this change touches neither the pane nor the API |

## Run 2026-11-13, third part (the finished workflow runtime check; HCW-HybridCloudWorks#1707)

`tests/security/test_workflow_runtime_setup.py` is replaced by the finished Python copy from HCW-NetworkEyes_App (commit `3810402`, [HCW-NetworkEyes_App#394](https://github.com/saulpatinojr/HCW-NetworkEyes_App/pull/394)), which is kept the same as the website's `scripts/workflow-runtime-setup.test.mjs` ([HCW-HybridCloudWorks#1707](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1707)). Only this repository's own lists differ, and the wording of three comment lines that ran past this repository's 120 columns. Toolchain: Linux cloud session, CPython 3.15.2, uv 0.13.7 installed with `pip` into a throwaway virtual environment outside the repository.

| Check | Executed here | Result |
| --- | --- | --- |
| The port's code against HCW-NetworkEyes_App's copy at `3810402` | yes | the two files' syntax trees are identical once the docstrings and the four lists (`RUNNER_DEFAULT_ALLOWED`, `INDIRECT_RUNTIME`, `PIPX_ALLOWED`, `BELOW_FLOOR_ALLOWED`) are set aside |
| `ruff check .`, `ruff format --check .`, `python scripts/check-catalog.py` | yes | clean, 58 files; catalog 1.1.0, 25 criteria |
| `pytest -q --cov=src` | yes | 740 passed, 10 skipped (the seed-adoption tests, as on `main`); coverage 96.01%. `tests/security/test_workflow_runtime_setup.py` alone: 354 passed (121 before) |
| The check over this repository's workflows | yes | no step reported: every step that runs Python or Node.js (now counting `pytest`, `bash -c` scripts and the rest) comes after a set-up step that covers it, every set-up step asks for 3.15 or 26, and no workflow runs `pipx` |
| The scripts the workflows call, read one level deep | yes | every Python script a step calls (`scripts/follow_website_base.py`, `check-catalog.py`, `adopt_core_wheel.py`) is run with `python` or `python3`, which the check reads, and starts no other program that is a runtime; `scripts/package-repository.sh` (the `package` job, which sets nothing up) runs only `zip` and `unzip`. So `INDIRECT_RUNTIME` stays empty |
| The same answers as HCW-NetworkEyes_App's copy | yes | 21,840 shared cases (command reading with its shell text, the `pipx` check and the condition rules) and the 97 workflow files of the nine HCW repositories cloned here (unset steps, `pipx` problems, floor problems): no disagreement, and none between the three add-ons' copies |
| The new checks catch a real step | yes | a job with `bash -c 'pytest -q'` and `pipx run zizmor .` steps added to the end of `ci.yml` on the working tree: 2 failed, naming both steps; the file was then restored |
| actionlint, zizmor, and CI on GitHub | **no** | no workflow changed, and nothing was pushed; the pull request's CI runs the test on GitHub |
| `make e2e` | **no** | this change touches neither the pane nor the API |

## Run 2026-11-13, second part (the engine's static metadata; HCW-HybridCloudWorks#1707)

The first part of this run (below) found that uv 0.13.7 could not lock this repository from here: its first request for the engine wheel is a HEAD, which GitHub's signed download link answered with `401`. This part ports the Cloud Crawler add-on's fix ([HCW-HybridCloudWorks#1707](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1707)): `pyproject.toml` gives uv the engine's metadata in a `[[tool.uv.dependency-metadata]]` entry, whose version line carries the marker `CORE_METADATA` and moves with the pin. `scripts/adopt_core_wheel.py --bump`, which `core-update.yml` runs in both jobs, now moves both lines or neither. The pull-request job needs no new check: it regenerates the bump with that script and compares the bump job's files with its own byte for byte. Toolchain as in the first part, with uv 0.13.7 for every uv command below.

| Check | Executed here | Result |
| --- | --- | --- |
| The entry's contents, from the pinned wheel itself | yes | `curl -L` (a GET) of `https://github.com/saulpatinojr/HCW-CloudAssessor_App/releases/download/v0.3.2/cloud_assessor_core-0.3.2-py3-none-any.whl` gave a file with sha256 `878d0d45a971ad567cc80f862ada6594aba3fcc4ba1e79383e6da7bdb1a66ca2`, the value in `uv.lock`; its `cloud_assessor_core-0.3.2.dist-info/METADATA` says `Name: cloud-assessor-core`, `Version: 0.3.2`, `Requires-Python: <3.16,>=3.14.6` and one `Requires-Dist: pydantic<3,>=2.14`, no `Provides-Extra`. The entry copies those `Requires-Dist` lines in the wheel's own spelling, leaves `Requires-Python` out on purpose (Dependabot rewrites every `requires-python` in the lock) |
| `uv lock -v` with an empty cache (`--cache-dir` a new folder) | yes | exit 0, `Resolved 52 packages`; the log shows 100 requests, 50 to `pypi.org` and 50 to `files.pythonhosted.org`, **none to `github.com` or `githubusercontent.com`** (the only line naming the engine's address is uv's `Searching for a compatible version`, which sends nothing) |
| `uv lock --check -v`, another empty cache | yes | exit 0, `Resolved 52 packages`, no request at all |
| What `uv lock` changed in `uv.lock` | yes | the header `revision = 3` became `5` (uv 0.13.7's lock format) and the `[manifest]` block with the entry was added; no package entry changed, the engine's URL and sha256 included |
| `uv sync` and `uv sync --frozen` (0.13.7) | yes | `Checked 51 packages`, nothing to change |
| The image's `uv export` (the Dockerfile's flags) and `security.yml`'s export, 0.13.7, against the first part | yes | byte-identical to the exports measured in the first part, under both uv versions |
| `uv lock --check` with uv 0.11.32 (the version `main` still uses) | yes | exit 0: a lock written by 0.13.7 also passes under 0.11.32 |
| `ruff check .`, `ruff format --check .`, `python scripts/check-catalog.py` | yes | clean, 58 files; catalog 1.1.0, 25 criteria |
| `pytest -q --cov=src` | yes | 507 passed, 10 skipped (the seed-adoption tests, as on `main`); coverage 96.01%. The new `tests/security/test_engine_static_metadata.py` (32 tests, ported from the Cloud Crawler add-on's, without its `test_engine_requires_only_pydantic`: that is the Cloud Crawler add-on's own rule about which dependencies its engine may have, not part of the metadata mechanism; here `tests/security/test_edition_boundary.py` still refuses any cloud SDK the engine declares) and the 4 new bump tests and 1 extended one in `tests/unit/test_adopt_core_wheel.py` are among them, and so is `tests/security/test_workflow_runtime_setup.py` |
| The new tests fail when the change is undone (each on the working tree, restored afterwards) | yes | `scripts/adopt_core_wheel.py` from before this part: 4 failed in `test_adopt_core_wheel.py`. `pyproject.toml` without the entry: 6 failed in `test_engine_static_metadata.py`. The apply step's bump moved after its `uv lock`: 1 failed |
| actionlint 1.7.12 (without shellcheck, not installed here) and zizmor 1.31.1 `--offline` with `.github/zizmor.yml` | yes | actionlint no findings. zizmor first reported one `adhoc-packages` finding: the Playwright install in `core-update.yml` moved down when lines were added above it, and `.github/zizmor.yml` ignores it by line number, as its comment says. The line is the same pinned `npm install "@playwright/test@1.63.0"`; its number in `.github/zizmor.yml` was moved to match, and zizmor then reported `No findings to report` |
| The PowerShell commands added to the runbook | **no** | no PowerShell here. The METADATA reader is the Cloud Crawler add-on's, run there in Windows PowerShell 5.1; the download line was adapted for this repository and was not run. The App's latest release (`v0.3.2`, read here with `gh api repos/saulpatinojr/HCW-CloudAssessor_App/releases/latest`) carries one file matching `cloud_assessor_core-*.whl` (and a `.tar.gz` the pattern skips) |
| A real engine bump through `core-update.yml`, a Dependabot run, and CI on GitHub | **no** | no new engine release exists, nothing was pushed, and Dependabot runs only from `main`. Whether GitHub Actions also gets the `401` was not tested; with the entry it no longer matters for `uv lock --check` |

## Run 2026-11-13 (uv 0.13.7 and ruff 0.17.4; HCW-HybridCloudWorks#1707)

uv (the tool that installs the Python packages and keeps `uv.lock`) moves from 0.11.32 to 0.13.7 in `ci.yml`, `security.yml`, `core-update.yml` and the Dockerfile's uv image ([HCW-HybridCloudWorks#1707](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1707)). Toolchain: Linux cloud session, CPython 3.15.2, uv 0.13.7 installed with `pip` into a throwaway virtual environment outside the repository, and the session's own uv 0.11.32. ruff moves from 0.17.3 to 0.17.4 and its `target-version` to `py315`, as in the Cloud Crawler add-on.

| Check | Executed here | Result |
| --- | --- | --- |
| The uv image digest: an anonymous `HEAD` of `https://ghcr.io/v2/astral-sh/uv/manifests/0.13.7` asking for an image index | yes | `Docker-Content-Digest: sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490`, content type `application/vnd.oci.image.index.v1+json` (the multi-platform index, which is what `docker buildx imagetools inspect` prints in `ci.yml`); the same digest `HCW-NetworkEyes_App` pins for 0.13.7. The old pin `df4cae8f…504c` is still what the registry gives for 0.11.32 |
| `ci.yml`'s uv check replayed (the `grep -Fq` lines, with the digest above in place of `docker buildx`) | yes | the Dockerfile line and the `"uv==0.13.7"` lines in `security.yml` and `core-update.yml` all match |
| The uv wheel hash in `core-update.yml`'s pull-request job | yes | `pip download --no-deps --only-binary=:all: --platform manylinux_2_17_x86_64 uv==0.13.7` gives `uv-0.13.7-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` with sha256 `2c9bdc4a872b60a93c5f26c0791089ea11585a4f9d3b3c017d78eb8487505e25`, the value PyPI's JSON lists |
| `uv lock --check` with uv 0.13.7 on this repository | **no, blocked** | uv 0.13.7 first sends a `HEAD` (a request for the file's headers only) to the engine wheel's address `https://github.com/saulpatinojr/HCW-CloudAssessor_App/releases/download/v0.3.2/cloud_assessor_core-0.3.2-py3-none-any.whl`; GitHub redirects it to a signed link on `objects.githubusercontent.com`, which answered `401`, so the command stopped with an error. A plain `GET` of the same address redirects to `release-assets.githubusercontent.com` and downloads. uv 0.11.32 sends no `HEAD`, which is why it never showed. This is the failure the Cloud Crawler add-on met in Dependabot's runs and fixed with a `[[tool.uv.dependency-metadata]]` entry (the engine's dependency list written in `pyproject.toml`, so uv need not ask the address). Whether GitHub Actions gets the same `401` was not tested: if it does, the `uv lock --check` step in `ci.yml` and the `uv lock` in `core-update.yml` fail until this repository gets the same entry |
| The same lock resolved by uv 0.13.7 with the engine's metadata supplied from a config file outside the repository (a scratch copy) | yes | 52 packages, every one identical to the committed lock; the only differences are the header `revision = 5` (uv 0.13.7's format; 0.13.7's `--check` accepts the committed `revision = 3`, tried on a scratch copy) and the `[manifest]` block the scratch config adds. So uv 0.13.7 itself changes nothing in `uv.lock` |
| `uv sync --frozen --all-packages` and `uv export --frozen` with uv 0.13.7 | yes | both work: installing from the lock downloads the wheel with a `GET` and never sends the `HEAD` |
| The image's `uv export` (the Dockerfile's flags) and `security.yml`'s export, under uv 0.11.32 and 0.13.7 | yes | byte-identical in both cases |
| ruff 0.17.3 → 0.17.4 in `pyproject.toml`, `target-version = "py315"` in `ruff.toml`; `uv lock --upgrade-package ruff` with uv 0.11.32 (the uv that can resolve this lock here; see above) | yes | `Updated ruff v0.17.3 -> v0.17.4`, only ruff's entry moved, and it is identical to the Cloud Crawler add-on's; `uv lock --check` (0.11.32) passes |
| `uv sync --all-packages`, `ruff check .`, `ruff format --check .` | yes | ruff 0.17.4; `All checks passed!`; 57 files already formatted, so the new target found nothing to change |
| `python scripts/check-catalog.py` | yes | catalog 1.1.0, 25 criteria, exit 0 |
| `pytest -q --cov=src` | yes | 471 passed, 10 skipped (the seed-adoption tests, as on `main`); coverage 96.01%. `tests/security/test_workflow_runtime_setup.py`, `test_core_update_app_token.py` and `tests/unit/test_follow_website_base.py` together: 268 passed |
| actionlint 1.7.12, hadolint 2.14.0 and zizmor 1.31.1 `--offline`, the versions `ci.yml` pins (binaries checked against its sha256 values) | yes, actionlint without shellcheck | no findings from any of them. shellcheck is not installed here, so actionlint ran with `-shellcheck=`; the shell lines changed only in a version number and a hash |
| Docker image build, and CI itself on uv 0.13.7 | **no** | no Docker daemon here, and nothing was pushed. The first pull request run is the real test of the `uv lock --check` step (see the row about the `401` above) |
| `make e2e` | **no** | no Playwright browser is installed here, and this change touches neither the pane nor the API |

## Run 2026-11-12 (workflow jobs choose their Python and Node.js; HCW-HybridCloudWorks#1707)

Toolchain: Linux cloud session, uv-managed CPython 3.15.2 (`uv sync --frozen --all-packages` ran). Three jobs ran Python
or Node.js on the runner's own versions (Python 3.14 and Node.js 24 on the `ubuntu-26.04` image), below the program's
floors of 3.15 and 26 ([HCW-HybridCloudWorks#1707](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1707)):
`base-update.yml` `plan` and `open-pr` (`python3 -I scripts/follow_website_base.py`) and `core-update.yml` `bump`
(`npm` and `npx` in the compatibility step). Each now installs its version with the pinned `actions/setup-python` (from
`.python-version`) or `actions/setup-node` (26), with no cache. A new test, `tests/security/test_workflow_runtime_setup.py`,
fails any workflow step that runs `node`, `npm`, `npx`, `python`, `python3` or `pip` before its job has set the version
up; it lists no exception in this repository.

| Check | Executed here | Result |
| --- | --- | --- |
| `tests/security/test_workflow_runtime_setup.py`, the new check over every workflow | yes | 30 passed. Its workflow reader was compared with PyYAML (CPython 3.13, outside the test) on all 367 steps of the four add-ons' workflows: the same jobs, containers and step `name`, `uses` and `run` values |
| The new check fails when a fix is undone | yes, on a scratch worktree | with the `bump` job's setup-node step removed from `core-update.yml`, 1 failed and 29 passed, naming `core-update.yml > bump > Compatibility check (lint, tests, catalog, browser e2e) > node`; the branch itself passes |
| `ruff check .`, `ruff format --check .`, `uv lock --check` | yes | `All checks passed!`, 57 files already formatted, lock current |
| `python scripts/check-catalog.py` | yes | `catalog 1.1.0: 25 criteria, 25 with learnUrl marked [VERIFY]` |
| `pytest -q --cov=src` (all of `tests/`) | yes | 380 passed, 10 skipped (the same pre-adoption cases as before); coverage 96% |
| actionlint 1.7.12 (with shellcheck 0.11.0) and zizmor 1.31.1 `--offline` with `.github/zizmor.yml`, the versions `ci.yml` pins | yes | actionlint no findings; zizmor `No findings to report` (2 ignored: the two `npm install @playwright/test` lines) |
| A real `base-update` run, and a real `core-update` bump, on the chosen versions | **no**, after the merge | `base-update` runs daily at 07:37 UTC; `core-update` only does this work when the App publishes a new release |
| Browser suite, image build | **no** | nothing in `web/`, `src/` or the Dockerfile changed |

## Run 2026-11-09 (release 0.1.3 prepared)

Toolchain: the authoring container (Linux, no Docker daemon). Its only Python 3.15 is `3.15.0b4`, which the project's
`requires-python = ">=3.15.1,<3.16"` refuses, so `uv sync` and `uv lock` could not run here. The checks ran in a scratch
virtual environment on `3.15.0b4` instead: the third-party set from `uv export --frozen --no-hashes --all-groups
--all-packages --no-emit-project` (uv 0.11.32, CI's `UV_VERSION`), with the engine wheel `cloud_assessor_core-0.3.2`
downloaded from the App's `v0.3.2` release and installed from a local file (its sha256 `878d0d45…6ca2` matches the one
`uv.lock` records), and the lab application on `PYTHONPATH=src`. This run prepares the version bump only: the reason
for the release is a rebuild of the image so it carries Debian's fixed zlib (CVE-2026-76844 and CVE-2026-85091, website
issue 1600). Nothing in `src/` (apart from `__version__`), `web/`, `samples/` or `docs/api/` changed since `v0.1.2`. No
image was built here.

| Check | Executed here | Result |
| --- | --- | --- |
| The lab application's version in every place that states it: `pyproject.toml`, `uv.lock` (the `cloud-assessment-lab` entry only), `__version__`, `repository.manifest.json` and the two sample lines in `docs/operations/runbook.md` | yes | all `0.1.3`. The `uv.lock` line was edited by hand (the one `version` line of the `[[package]]` whose `source = { editable = "." }`, the same one line `uv lock` changed for `0.1.2`), because `uv lock` refuses the container's Python. The engine pin stays `cloud-assessor-core 0.3.2` |
| `docs/api/openapi.yaml`, `info.version` | decided, not changed | stays `0.1.0`, for the reason recorded in the run of 2026-10-27 |
| `uv lock --check` | **no** | refused here for the Python version above; the `lint` job of `ci.yml` runs it on the pull request |
| `ruff check .` and `ruff format --check .` | yes | clean (`All checks passed!`, 56 files already formatted) |
| `python scripts/check-catalog.py`, and its `--doc` output against `docs/rules/catalog.md` | yes | `catalog 1.1.0: 25 criteria, 25 with learnUrl marked [VERIFY]`, exit 0; the generated document is identical to the committed one |
| `pytest -q --cov=src` (all of `tests/`) | yes | 348 passed, 10 skipped (the `test_adopt_core_wheel.py` cases that apply only before the first adoption), coverage 96.01% |
| Browser suite (`make e2e`, `npx playwright test -c tests/e2e/playwright.config.ts`) | **no** | nothing in `web/` or `src/` changed beyond the version string; the `e2e` job of `ci.yml` runs it on the pull request |
| The image's last stage applies Debian's security updates on every publish run | read, not built | `infrastructure/docker/Dockerfile` lines 68 to 73: `ARG PUBLISH_CACHE_BUST=`, then `apt-get update --error-on=any` and `apt-get upgrade -y` with the cache bust named in the command; `tests/security/test_image_security_updates.py` pins it and passed above |
| Docker image build, the in-image boundary checks, Trivy, and the zlib version in a built image | **no**, CI only | the `image` job of `ci.yml` builds one on the pull request; the publish dry run on `main` after the merge is recorded in the pull request |
| Push, provenance, SBOM, attestation and digest of `v0.1.3` | **no** | only the tag `v0.1.3` publishes, and it is the owner's call |
| The live lab host | **no** | it runs the earlier image until the website pins the new digest |

## Run 2026-11-05 (release 0.1.2 prepared)

Toolchain: Python 3.15 (`.python-version`), uv 0.12.0 for the checks and `uvx uv@0.11.32 lock` for the lock file (CI's
`UV_VERSION`), environment from `uv sync --frozen --all-packages`, on a Windows 11 workstation. This run prepares the
version bump only: nothing in `src/`, `web/`, `samples/` or `docs/api/` changed since `v0.1.1` (`git diff v0.1.1
origin/main` over them is empty). The reason for the release is the apt security update of pull request 76 (website issue
1562); its dry run on that commit, run 42115517340, was green. No image was built here.

| Check | Executed here | Result |
| --- | --- | --- |
| The lab application's version in every place that states it: `pyproject.toml`, `uv.lock` (the `cloud-assessment-lab` entry only), `__version__`, `repository.manifest.json` and the two sample lines in `docs/operations/runbook.md` | yes | all `0.1.2`. `uvx uv@0.11.32 lock` changed that one `uv.lock` line and nothing else (`revision = 3` stayed, so no hand edit this time). The engine pin stays `cloud-assessor-core 0.3.2` |
| `docs/api/openapi.yaml`, `info.version` | decided, not changed | stays `0.1.0`, for the reason recorded in the run of 2026-10-27 |
| `uv lock --check` | yes | exit 0 |
| `uv run ruff check .` and `uv run ruff format --check .` | yes | clean (`All checks passed!`, 56 files already formatted) |
| `uv run pytest -q tests/security tests/unit` | yes | 312 passed, 9 skipped; the 16 failures and 17 errors are all in `tests/unit/test_adopt_core_wheel.py`, whose tests run `bash -c`, which on this workstation resolves to WSL rather than Git Bash (the known environmental failure; CI runs them on Ubuntu). With that file deselected, plus `tests/end_to_end/test_repository_manifest.py`: 305 passed |
| `/api/health` and `X-Addon-Version` read `__version__` | yes | `tests/unit/test_api.py` asserts both equal `__version__`; `tests/end_to_end/test_repository_manifest.py` holds `__version__` to `pyproject.toml` and `repository.manifest.json` |
| `uv run python scripts/check-catalog.py` and its `--doc` output against `docs/rules/catalog.md` | **no** | the catalog and `docs/rules/catalog.md` are untouched by this change; the `catalog-check` job of `ci.yml` runs it on the pull request |
| Browser suite (`make e2e`, `npx playwright test -c tests/e2e/playwright.config.ts`) | **no** | nothing in `web/` or `src/` changed; the `e2e` job of `ci.yml` runs it on the pull request |
| Docker image build, the in-image boundary checks, Trivy, and the apt version in a built image | **no**, CI only | the `image` job of `ci.yml` builds one on the pull request; the publish dry run on `main` after the merge is recorded in the pull request |
| Push, provenance, SBOM, attestation and digest of `v0.1.2` | **no** | only the tag `v0.1.2` publishes, and it is the owner's call |
| The live lab host | **no** | it runs `0.1.1` until the website pins the new digest |

## Run 2026-10-31, third round (`core-update.yml` runs from `main` only; auto-merge ignores the bump job's report)

The first step of both jobs refuses a run whose `github.ref` is not `refs/heads/main`, the `pull-request` job's `if:`
also requires it, both checkouts take `github.sha`, and `create-pull-request` gets `base: main`. The auto-merge step's
condition is now `CORE_AUTOMERGE == 'true'`, not a probe, the apply step's success and a pull request number; it no
longer reads the untrusted outcome.

| Check | Executed here | Result |
| --- | --- | --- |
| `uv sync --all-packages`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run python scripts/check-catalog.py` | yes | clean (90 files); catalog 1.0.0, 25 criteria |
| `uv run pytest -q --cov=packages --cov=src` | yes | 406 passed, coverage 98.12% |
| `tests/security/test_core_update_app_token.py` | yes | 21 passed, with three new or rewritten tests: the refusal is the first step of each job, has no `if:`, reads the ref through `env` and names it in an `::error::`; the `bump` job has no job-level `if:` and the `pull-request` job's requires `main`; both checkouts use `github.sha` and the pull request step names `base: main`; the auto-merge condition holds the variable, the apply step and `!inputs.probe` and nothing that reads the outcome, and only the pull request step and a token-free warning read it |
| Mutation check: six breakages, one at a time | yes | each made at least one test fail: either job's refusal step removed, the `main` condition removed from the job's `if:`, the refusal's `exit 1` replaced with `true`, `ref: github.sha` removed from a checkout, `steps.apply.outputs.outcome == 'success'` added back to the auto-merge condition; the workflow was restored byte for byte |
| `actionlint` 1.7.12 on `core-update.yml` (shellcheck off, not installed) | yes | no findings apart from `ubuntu-26.04` being unknown to this actionlint version (already so on `main`) |
| Required checks on `main`, read-only (`gh api repos/saulpatinojr/HCW-CloudAssessor_AddOn/rules/branches/main`) | yes | the active "Protect main" ruleset (id 25825149) requires `lint`, `test`, `image`, `package`, `e2e`, `catalog-check`, `pip-audit`, `secret-scan`, `dependency-review`, which covers the bump job's compatibility check (lint, catalog, tests, e2e) |
| `make e2e` | no | nothing here touches the pane or the API |
| The workflow on GitHub, including a refused run from a branch | no | not run; the value of `CORE_AUTOMERGE` could not be read from this session |

Known limitation: a manual run takes the workflow file itself from the branch it was started on, so a branch that also
edits `core-update.yml` can delete these guards. Closing that needs the App key moved to an environment whose
deployment branches are `main` only (a settings change, not made here).

## Run 2026-10-31, second round (review fixes: two-job split, tag check, exact bump)

Same toolchain as the run below. After an independent review of pull request 67 (head `36251c8`). The wheel was again
built from the App's tag `v0.2.1` and served on `127.0.0.1` for the simulation.

| Check | Executed here | Result |
| --- | --- | --- |
| `uv sync --all-packages`, `uv run ruff check . && uv run ruff format --check .` | yes | clean (90 files) |
| `uv run python scripts/check-catalog.py`, `--doc` drift, `uv lock --check` | yes | catalog 1.0.0, 25 criteria; no drift; exit 0 |
| `uv run pytest -q --cov=packages --cov=src` | yes | 396 passed, coverage 98.12% (gate 85) |
| The refs step's script as written, fed hostile tags through `inputs.ref` and through a stand-in `gh` (`v9\|;etouch${IFS}PWNED;#`, a tag with a newline, `v1.0`, `v1.0.0-rc.1`, and others) | yes (in the tests) | each refused with exit 1, nothing written to `GITHUB_OUTPUT`, no `PWNED` file; a plain `v99.0.0` passes |
| `adopt_core_wheel.py --bump` with the same hostile tags | yes (in the tests) | refused, `pyproject.toml` unchanged; a plain bump moves the URL and the marker |
| The `pull-request` job's apply step as written, against a stand-in checkout and artifact | yes (in the tests) | takes the expected bump; refuses an extra file, a deletion outside the seed, a `..` path, a deletion of an untracked path, a symbolic link, an extra artifact entry, a malformed or missing outcome and a malformed tag, each with the checkout left unchanged |
| A step that runs project code added to the `pull-request` job | yes (a temporary edit, reverted) | `test_the_job_that_holds_the_key_runs_no_project_code` fails |
| `import socket` appended to the installed engine (the `0.2.1` wheel in the simulation's `.venv`, reverted after) | yes | `test_the_engine_opens_no_network_connection` fails with `paths.py: socket`; passes again once removed |
| `check-catalog.py --write-schema` with the wheel installed in the in-project `.venv` | yes | exit 1, "belongs to the installed engine release"; the installed `schema.json` is untouched. With the seed it rewrites the seed's file with no change |
| Simulation, both jobs: the bump by hand, then the `bump` job's collect step, then the `pull-request` job's apply step in a fresh clone | yes | the artifact holds the five files, 39 deletions and `success`; the applied clone is identical to the `bump` job's tree (outside ignored folders) |
| Simulation: the applied clone with an ignored `__pycache__` left under `packages/cloud-assessor-core` | yes | coverage flags pick `--cov=src` only (`ci.yml` and `make -n test`); ruff, catalog 1.1.0, drift, `uv lock --check` clean; pytest 311 passed, 9 skipped, 1 failed (the bump test, only because the simulated URL is `127.0.0.1`; with the release URL form, 120 of 120 run tests pass in the touched files); Playwright 4 passed; `pip-audit --strict` on the `security.yml` export: no known vulnerabilities |
| Third round (Copilot's review of `2a2d3ed`): the `pull-request` job's regenerate-and-compare step as written, with real uv, in a clean clone, against the artifact from the simulation (wheel URL pointed at the local server in that clone's copy of the script) | yes | exit 0; the regenerated `pyproject.toml`, `uv.lock`, Dockerfile, `.dockerignore` and 39 deletions are byte-identical to the artifact's; `outcome=success` |
| The same with one changed line in the artifact's `pyproject.toml` | yes | exit 1, `pyproject.toml in the artifact differs from the one regenerated here`; the checkout is left clean |
| `uv lock --no-build -v` for the first adoption | yes | `Found static pyproject.toml for: cloud-assessment-lab`; nothing built; the wheel's metadata read from the wheel; the lock is identical to the one plain `uv lock` wrote |
| uv by hash: `pip download --require-hashes` of `uv==0.11.32 --hash=sha256:3da76cd4…a6c4` | yes | the manylinux x86_64 wheel downloads and matches (hash from PyPI's JSON for 0.11.32) |
| The apply step against tampered artifacts in the tests (stand-in uv, real script and real collect step): an extra line in `pyproject.toml`, a changed `uv.lock`, an edited Dockerfile, a non-seed deletion, a dropped seed deletion, HTML, a control character, a wrong heading or 300 KB in `catalog.md`, plus the earlier cases | yes | each refused with exit 1, nothing written to `GITHUB_OUTPUT`, checkout unchanged; the untampered artifact is taken |
| `uv run pytest -q --cov=packages --cov=src` at the third round | yes | 404 passed, coverage 98.12% |
| actionlint | **no** | not re-run (running a downloaded linter was not allowed in this session) |
| The two jobs on GitHub, the artifact hand-over, the bump pull request and auto-merge | **no** | GitHub only, after merge |

## Run 2026-10-31 (adoption of engine `v0.2.1` handed to `core-update.yml`)

Toolchain: Python 3.14.6 (`.python-version`), uv 0.11.32 (the version CI uses), Docker 29.9.2 with a daemon, Playwright
1.63.0 with its preinstalled chromium, on the authoring container. The release asset itself could not be downloaded
here, so the wheel was built from a clone of the App at tag `v0.2.1` (`55b7242`) with `uv build`; its sha256,
`6c5564ba0bc82c79060704dd52871e56b51b709c9ee8bdd7b6b7cf0409ca26e7`, is the release asset's (recorded on 2026-10-24 in
`docs/whats-new-upstream.md`). "Simulation" below is a throwaway copy of the branch in which the workflow's bump step
was run by hand, with the wheel served on `127.0.0.1` and passed with `--wheel-url` (the only difference from the run on
GitHub, which uses the release URL).

| Check | Executed here | Result |
| --- | --- | --- |
| `uv sync --all-packages` (branch, seed) | yes | resolved, 51 packages checked |
| `uv run ruff check . && uv run ruff format --check .` | yes | clean (90 files) |
| `uv run python scripts/check-catalog.py`, and `--doc` against `docs/rules/catalog.md` | yes | catalog 1.0.0, 25 criteria, 25 `[VERIFY]`; no drift |
| `uv lock --check` | yes | exit 0 (the `allow-direct-references` setting does not change the lock) |
| `uv run pytest -q --cov=packages --cov=src` | yes | 348 passed, coverage 98.12% (gate 85) |
| `make e2e` | **no, as written**: here `npx --yes playwright@1.63.0` resolves a global Playwright that cannot load `@playwright/test` | the CI way instead (`npm install --no-save @playwright/test@1.63.0`, `CI=1 npx playwright test -c tests/e2e/playwright.config.ts`): 4 passed |
| Image build (branch, seed), then the `image` job's steps from `ci.yml` | yes, with one local-only change: the proxy's CA certificate copied into the build stage for `pip` | built; `import azure` fails; fastapi, pydantic and uvicorn import; `Python 3.14.8` equals `BASE_PYTHON_VERSION=3.14.8`; licence label `MIT` |
| The new Python check with `BASE_PYTHON_VERSION=3.14.7` in a copy of `versions.env` | yes | fails as intended: `the image runs 'Python 3.14.8', versions.env says BASE_PYTHON_VERSION=3.14.7` |
| Simulation: the bump step (`adopt_core_wheel.py`, `git rm -r`, `uv lock`, `uv sync --frozen`, `--doc`) | yes | three files rewritten; `uv.lock` gains `cloud-assessor-core 0.2.1` with hash `sha256:6c5564ba…26e7`; 12 lines of `docs/rules/catalog.md` change |
| Simulation: what `create-pull-request` commits (`git add --` the five add-paths, then `git commit`) | yes | one commit with the five files and the seed's deletion (44 files); the untracked `package.json` from the e2e install is left out |
| Simulation: ruff, `check-catalog.py`, `--doc` drift, `uv lock --check` | yes | clean; catalog 1.1.0, 25 criteria; no drift |
| Simulation: `pytest` with the coverage line `ci.yml` now runs | yes | 263 passed, 9 skipped (the seed-only tests), 1 failed: the sed test, only because the simulated URL is `127.0.0.1` rather than `github.com/.../releases/download/`; with the URL put in the release form it passes. Coverage 96.01% |
| Simulation: Playwright e2e | yes | 4 passed |
| Simulation: image build with the wheel, then the `image` job's steps | yes (build network `host` to reach the local server) | pip installs `cloud-assessor-core-0.2.1` from the lock with `--require-hashes`; no cloud SDK in `/install`; all checks pass; the container answers `/api/health` with catalog `1.1.0` |
| Simulation: `pip-audit --strict` on the export with and without `--no-emit-package cloud-assessor-core` | yes | without it: exit 1, `Dependency not found on PyPI and could not be audited: cloud-assessor-core (0.2.1)`; with it: `No known vulnerabilities found` |
| Findings and scores for both fictional samples, seed against `0.2.1` (`report.json` through the API) | yes | identical; only `catalog_version`, `core_version`, `created_at` and the two new `null` keys `edition` and `scope` differ |
| actionlint on `ci.yml`, `core-update.yml`, `security.yml` | partly | one run printed only the known `ubuntu-26.04` runner-label notice in the part shown; a filtered re-run was not allowed in this session, so a clean result is not claimed |
| The real `core-update.yml` run, the bump pull request, its required checks and auto-merge | **no** | GitHub only, after this pull request merges: the next scheduled run (minute 41 of hours 0, 6, 12, 18 UTC) or `gh workflow run core-update.yml -R saulpatinojr/HCW-CloudAssessor_AddOn --ref main` |

## Run 2026-10-27 (release 0.1.1 published)

Run on GitHub after the owner said yes to the tag ([issue 47](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/issues/47)).
Nothing in the application changed; this records the dry run, the tag and what the registry shows.

| Check | Result |
| --- | --- |
| The gate step of `publish-images.yml` for a manual run, its own shell run with the repository variables set as they are | **Before** [pull request 60](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/60): `push=true` for a manual run on `main`, so a "dry run" could have reached the Docker login. **After**: `push=false` with a notice for anything that is not a `v*` tag; a tag gives `push=true`; a tag with publishing switched off gives `push=false` |
| Publish dry run on `main` at `8079f7ac` (the guard and the release both merged), [run 40501552352](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/actions/runs/40501552352) | success. The build, the in-image boundary check (which asserts the licence label) and the Trivy scan passed; the gate step passed; the Docker login, the push, the attestation and the digest record were skipped |
| Tag `v0.1.1` on that same commit, [publish run 40502008575](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/actions/runs/40502008575) | success: login, push with provenance and SBOM, attestation, digest record |
| Digest in the registry | `sha256:95082857e3b866743ffa5c827c7b897d085e945d80aa4b710f58926b03170456` for `docker.io/hybridcloudworks/img-ca-lab-addon:v0.1.1` |
| Labels on the published image (`docker buildx imagetools inspect <image> --format '{{json .Image.Config.Labels}}'`) | `org.opencontainers.image.licenses=MIT`, `org.opencontainers.image.version=0.1.1`, `org.opencontainers.image.revision=8079f7ac9b92769bf65ec81d9848154dbc74bce2` |
| `gh attestation verify oci://docker.io/hybridcloudworks/img-ca-lab-addon:v0.1.1 --repo saulpatinojr/HCW-CloudAssessor_AddOn` | passes (exit 0). With `--format json`: the attested subject digest equals the registry digest above, the predicate is SLSA provenance v1, the signer is `.github/workflows/publish-images.yml@refs/tags/v0.1.1` of this repository, and the source commit is the tagged commit. Without a terminal the command prints nothing, so read its exit code or use `--format json` |
| GitHub Release | [v0.1.1](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/releases/tag/v0.1.1) |
| The live lab host | **not changed**: it keeps running the `v0.1.0` image until a website change pins the new digest (the owner said nothing changes on the website for this release) |

CodeRabbit's note on the release pull request ([61](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/61)) asked for a tag guard
before any manual publish run; that is pull request 60, merged before the dry run. The section below records the state when the release was
prepared, before the guard, the dry run and the tag.

## Run 2026-10-27 (release 0.1.1 prepared)

Toolchain: Python 3.14.6 (`.python-version`), uv 0.12.0 locally (CI uses uv 0.11.32, which was not run here), environment from
`uv sync --frozen --all-packages`, on a Windows 11 workstation. This run prepares the version bump only: nothing in `src/`,
`web/`, `samples/` or `docs/api/` changed since `v0.1.0` (`git diff v0.1.0 origin/main` over them is empty). No image was built
and no workflow was run for it.

| Check | Executed here | Result |
| --- | --- | --- |
| The lab application's version in every place that states it: `pyproject.toml`, `uv.lock` (the `cloud-assessment-lab` entry only), `__version__`, `repository.manifest.json` and the two sample lines in `docs/operations/runbook.md` | yes | all `0.1.1`. `uv lock` also rewrote the `revision = 5` line of `uv.lock` to `3`; that line was put back by hand so the lock file differs in one line. The engine seed (`packages/cloud-assessor-core`, its `__version__`, its tests, and the `cloud-assessor-core` entry in `uv.lock`) stays `0.1.0` on purpose |
| `docs/api/openapi.yaml`, `info.version` | decided, not changed | stays `0.1.0`. The OpenAPI Specification defines that field as the version of the API document, "distinct from the OpenAPI Specification version or the API implementation version" ([Info Object](https://spec.openapis.org/oas/v3.1.0#info-object)); the document is unchanged since `v0.1.0`; no test ties it to `__version__`; the Migrate AddOn keeps API document `0.3.0` beside release `0.3.2` |
| `uv lock --check` | yes | exit 0 |
| `uv run ruff check .` and `uv run ruff format --check .` | yes | clean (88 files) |
| `uv run pytest -q --cov=packages --cov=src --cov-fail-under=85` | yes | 336 passed, coverage 98.12% (gate 85) |
| `/api/health` and `X-Addon-Version` read `__version__` | yes | `tests/unit/test_api.py` asserts both equal `__version__`; `tests/end_to_end/test_repository_manifest.py` holds `__version__` to `pyproject.toml` and `repository.manifest.json`; a request to the app in the same process printed health `0.1.1` and header `0.1.1` |
| `uv run python scripts/check-catalog.py`, and its `--doc` output against `docs/rules/catalog.md` | yes | catalog 1.0.0, 25 criteria, 25 links marked `[VERIFY]`; no drift |
| The website's `scripts/addons/check-guide-drift.mjs` (the script `guide-drift.yml` runs), on this branch's guide and the website's `main` data | yes, locally | "in step: 13 fields compared". The guide is not touched by this change |
| Docker image build, the in-image boundary checks, Trivy, and the licence label on a built image | **no**, CI only | no image was built here; the `image` job of `ci.yml` builds one and checks the label on the pull request |
| `publish-images.yml` dry run on `main` | **no** | not part of this change. This repository's gate step does not check for a `v*` tag (the Cloud Crawler's does, since its [pull request 18](https://github.com/saulpatinojr/HCW-CloudCrawler_AddOn/pull/18), which says a manual run there reached the Docker login and failed because the connection trusts tags only). What a manual run does here has not been observed |
| Push, provenance, SBOM, attestation and digest of `v0.1.1`; the label on the Docker Hub tag | **no** | only the tag `v0.1.1` publishes, and it is the owner's call ([issue 47](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/issues/47)) |
| The live lab host | **no** | the status route still reported version `0.1.0` on 2026-10-27, as expected until the website pins a new digest |

## Upstream adoption trial 2026-10-24 (nothing in this repository changed)

Question: would the App's engine `0.2.1` (release `v0.2.1`) work in this edition? Method: a throwaway copy of this repository with `packages/cloud-assessor-core` replaced by the App's `packages/cloud-assessor-core` at `5a7ed0b` (engine `0.2.1`, catalog `1.1.0`), `uv sync --all-packages`, then `pytest` over `tests/unit`, `tests/security`, `tests/contract`, `tests/end_to_end` and the engine's own tests. Python 3.14.6, uv 0.11.32.

| Check | Executed here | Result |
|---|---|---|
| Tests with the App's engine swapped in | yes | 160 passed, 1 failed: `tests/unit/test_api.py::test_health_is_flat_and_complete` pins the catalog version at `1.0.0`; the engine reports `1.1.0` (stale test value) |
| `uv run python scripts/check-catalog.py` with the App's engine | yes | catalog 1.1.0, 25 criteria, 25 reference links marked `[VERIFY]` |
| `make rules-doc` with the App's engine | yes | `docs/rules/catalog.md` changes by 6 lines |
| `uv lock --check` on this repository as it is | yes | exit 0 |
| Playwright e2e (`make e2e`) with the App's engine | **no** | not run in the trial |
| Docker image build with the App's engine | **no**, CI only | no daemon here |
| Install of the `v0.2.1` wheel by URL with `pip` on Python 3.14 | yes | installs; `cloud_assessor_core.__version__` is `0.2.1`; the downloaded wheel's sha256 is `6c5564ba0bc82c79060704dd52871e56b51b709c9ee8bdd7b6b7cf0409ca26e7`, matching GitHub's digest |

Limitation: `uv pip install` of the same URL failed with a 401 on the download redirect inside the authoring sandbox (its proxy); `pip` and `curl` worked. The adoption steps are in `docs/whats-new-upstream.md`.

## Run 2026-10-10 (0.1.0, initial)

Toolchain: Python 3.14.6 (`uv python pin 3.14.6`), uv 0.11.32, Node 26.11.1 (for Playwright only), chromium 1243
(`playwright@1.63.0`). Resolved pins: fastapi 0.143.0, uvicorn 0.54.0, pydantic 2.14.0 (pydantic-core 2.50.0,
starlette 1.7.0, anyio 4.15.1, h11 0.16.0, click 8.5.0, idna 3.20, annotated-types 0.8.0, annotated-doc 0.0.5,
opentelemetry-api 1.45.1, typing-extensions 4.16.0, typing-inspection 0.4.4); dev pytest 9.1.1, pytest-cov 7.1.0,
ruff 0.17.0, httpx 0.28.1, pip-audit 2.10.1; build hatchling 1.32.4. `uv.lock` and `requirements.lock.txt`
(`uv export --format requirements-txt --no-dev --no-emit-project --no-emit-workspace --no-header`; hashes are on by
default) are committed; 14 third-party runtime packages, none Azure. Since 2026-10-16 the export is not committed:
the image build runs it from `uv.lock` (see `infrastructure/README.md`), and CI checks `uv lock --check`.

| Check | Executed here | Result |
|---|---|---|
| `uv sync --all-packages` | yes | 52 packages resolved and installed |
| `uv run ruff check . && uv run ruff format --check .` | yes | clean (82 files) |
| `uv run python scripts/check-catalog.py` | yes | catalog 1.0.0, 25 criteria, 25 reference links marked `[VERIFY]`; `schema.json` in sync; `docs/rules/catalog.md` in sync |
| `uv run pytest -q --cov=packages --cov=src --cov-report=term-missing` | yes | 151 tests passed; coverage 98% (2,224 statements, 36 missed; gate 85). `__main__.py` is covered only by its subprocess tests, which coverage does not trace |
| `uv run pytest tests/security tests/contract -q` | yes | 16 passed (edition boundary incl. fresh-process refusal, no secrets, content-free logs, OpenAPI two-way) |
| Live server: `CA_ALLOW_NO_TURNSTILE=1 PORT=8080 uv run python -m cloud_assessment_lab`, `GET /api/health`, `POST /api/assessments` with `samples/sample-resource-graph.json`, `GET …/report.md`, `GET …/bundle.zip`, wrong token, `DELETE`, after-delete, `GET /` | yes | health `ok:true id:cloud-assessment version:0.1.0 edition:lab`, headers `X-Addon-Id`, `X-Addon-Version`, CSP with `frame-ancestors 'none'`, `X-Frame-Options: DENY`, `Cache-Control: no-store`; 201 with 40 resources / 95 findings; report.md 200 (10,480 B); bundle.zip 200 (151,756 B); wrong token 404; `{"deleted":true}`; 404 after delete; index 200. Log lines carried only counts, flags and event names |
| `IDENTITY_ENDPOINT=http://169.254.169.254 uv run python -c "import cloud_assessment_lab.app"` | yes | exit 1 with `EditionBoundaryError: refusing to start: identity environment present (IDENTITY_ENDPOINT)`; `python -m cloud_assessment_lab` under `MSI_ENDPOINT` exits 3 with one scrubbed `startup_refused` line |
| `uv run pip-audit -r requirements.lock.txt --strict` | yes | no known vulnerabilities |
| Playwright e2e (`npx playwright test -c tests/e2e/playwright.config.ts`, chromium) | yes | 4 passed: standalone journey (sample, scorecard, filters, detail, copy report, download, delete); vendor-name scan; framed pane under the site's sandbox posting `loading, ready, working, ready` to the host origin, dark theme by `?theme=dark`; headers and health |
| `bash scripts/package-repository.sh` | yes | `hcw-cloudassessor-addon.zip` (220 KB); archive file set equals `git ls-files`; no excluded path leaked |
| `git status --short \| wc -l` | yes | 29 top-level entries (137 files, all untracked: initial commit pending; the parent commits) |
| Docker image build (`infrastructure/docker/Dockerfile`) | **no**, CI only | no daemon here; `publish-images.yml` builds, proves `import azure` fails and the container exits under `IDENTITY_ENDPOINT`, runs the hardened health check, scans with Trivy, and pushes only when `DOCKERHUB_ENABLED` is `true` |
| Trivy scan, SBOM, provenance, attestation | **no**, CI only | as above |
| `versions.env` vs every `FROM` | locally by the same shell snippet as `ci.yml`; CI | both `FROM` lines equal `BASE_IMAGE@BASE_DIGEST` |
| Human verification against the real siteverify endpoint | **no** | mocked in `tests/unit/test_api.py` and `test_security_modules.py`; the real call needs the owner's widget and secret (`docs/deployment/lab-host.md`) |
| Lab-host deployment, Caddy route, website pane | **no** | owner steps and the website PR (Phase 6); the catalogue row stays `coming` until the digest exists |
| CodeQL, gitleaks, dependency-review | **no**, CI only | `security.yml` |

## Limitations recorded

- An export shows configuration only: spend, budgets, role assignments, diagnostic settings, policy state, Defender
  plans and traffic are `unknown` by design (the panel and `report.md` say so; coverage, never score, reflects it).
- `CA-FIN-003`, `CA-FIN-007`, `CA-ZT-011` and `CA-FIN-002` are estate-level criteria: one finding each, so the sample
  cannot show both a pass and a fail for them (pinned as such in `test_samples_expected.py`).
- The portal "All resources" CSV maps the display names of the 19 types in the sample to ARM types; other display
  names stay as written and match no criterion (they are counted, not assessed).
- Every `learnUrl` is the most plausible page on `learn.microsoft.com` or `www.finops.org` as of 2026-10-10 and is
  marked `[VERIFY]` (`verify: true`) until the owner confirms it; the attribution wording is `[REVIEW REQUIRED]` (R-005);
  the MIT license is `[REVIEW REQUIRED]` (R-003 upstream undecided); the `downloads` sandbox capability is
  `[REVIEW REQUIRED]` on the website side; the base-image digest is `[VERIFY]` at the first image build.
- The 5 MB cap stops reading at the limit and answers 413; the socket close past the limit is uvicorn's behaviour on an
  unread body and was observed only through the test client, not with a raw socket.
- First-party packages are copied into the image as source trees rather than built as wheels (no build backend in
  the image); `importlib.metadata` therefore does not know them, and the version comes from `__version__` (asserted
  equal to `pyproject.toml` and `repository.manifest.json` by a test).
- starlette 1.7 prefers `httpx2` for its test client; this edition pins `httpx` (the brief) and mutes that one
  deprecation notice in `pyproject.toml`.
- The engine is the App's release wheel, not a local seed. `core-update.yml` made the one-time switch in
  [pull request 69](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/69) (merged 2026-10-31 as `8b4d30d`,
  engine `v0.3.0`: the wheel by URL, its sha256 in `uv.lock`; ADR-0001), which deleted the seed under
  `packages/cloud-assessor-core`, and then its first wheel-to-wheel bump in
  [pull request 72](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/72) (merged 2026-11-05 as `99c9a24`,
  `v0.3.0` to `v0.3.2`). The pin now reads `CORE_REF v0.3.2`. The code for the one-time switch was removed on
  2026-11-13, so the workflow now accepts only a plain `v<major>.<minor>.<patch>` pin and fails a run whose
  `pyproject.toml` has no `CORE_REF` line.
- `core-update.yml` opens the pull request with a GitHub App token (the HCW Main Admin App: its client ID is the repository variable
  `HCW_MAIN_ADMIN_CLIENT_ID`, its private key the repository secret `HCW_MAIN_ADMIN_PRIVATE_KEY`), not `GITHUB_TOKEN`, so the required checks run on the pull request itself. That path is covered by
  `tests/security/test_core_update_app_token.py` (static) and was linted with actionlint and zizmor, and it has worked on
  GitHub: the App (`hcw-main-admin[bot]`) opened both pull request 69 and pull request 72. To prove the credential again
  without opening a pull request (a manual run that only makes read-only calls):
  `gh workflow run core-update.yml -R saulpatinojr/HCW-CloudAssessor_AddOn --ref main -f probe=true`.
  The App key lives only as the repository secret `HCW_MAIN_ADMIN_PRIVATE_KEY` and is never printed. To rotate it,
  generate a new private key on the settings page of the App (https://github.com/settings/apps), replace the secret in every repository that holds the key (this one:
  https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/settings/secrets/actions; the App is installed on the four
  add-on repositories, so check the other three; HCW-CloudCrawler_App and HCW-CloudAssessor_App, where the owner decided on 2026-11-04
  to install it too, hold a separate key as Dependabot secrets and are rotated on their own), then delete the old key on the settings page of the App.
  The settings page can hold several keys, so a separate key per repository lets you revoke one without
  touching the others.
  **Accepted risk, so nobody has to rediscover it.** A repository secret can be read by any workflow that runs from a branch
  someone with write access can push, so `base-update.yml` is a second reader of the key beside `core-update.yml` (both can
  be started by hand with `workflow_dispatch`), and the base-update proof depends on that: it runs the workflow from a
  throwaway branch (it did, on 2026-10-27, and minted the token from that branch). As of 2026-10-27, only the owner can push here. The App
  is installed on the four add-on repositories (and, since 2026-11-05, on HCW-CloudCrawler_App and HCW-CloudAssessor_App, as decided on 2026-11-04; its first run there is the proof tracked on HCW-CloudCrawler_App issue #70), and both workflows ask the token action for this repository only
  (`repositories: ${{ github.repository }}`) with Contents and Pull requests write; a token lasts one hour. A modified workflow
  on another branch could ask for more: the limit is then whatever the App was granted when it was installed (that list is on
  the App's settings page, https://github.com/settings/apps, and is not repeated here because a session cannot read it), which
  is why the key is a risk. The owner decided on 2026-10-26 to leave the key as a repository secret
  ([HCW-HybridCloudWorks#1410](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1410)); the stronger options (an
  environment limited to `main`, or a separate App installation for each repository) can be reopened if the key is ever
  suspected leaked. A separate key for each repository on the same App is not one of them: it helps rotation (one key can be
  revoked without touching the others) but it does not shrink what a stolen key can reach, because every key authenticates the
  same App, and that App is installed on all four add-on repositories and, since 2026-11-05, on HCW-CloudCrawler_App and HCW-CloudAssessor_App too
  (their lockfile workflow pushes with it, HCW-CloudCrawler_App issue #70). A stolen key could then reach those
  two repositories as well, though `main` in both still needs a pull request with an approval of its latest push. An environment limited to `main` would also stop the
  base-update proof, which needs a run from a branch.
- Auto-merge of a bump (any bump since pull request 68; it then waits for the required checks) needs the repository
  setting "Allow auto-merge", which was off on 2026-10-26 (UTC) and has since been turned on.
  With it off, `core-update` warns and leaves the pull request for a person to merge.
- `base-update.yml` moves the base image pin to the website's pin by opening a pull request, with the same HCW Main Admin App credential as
  `core-update.yml` (so `core-update.yml`'s probe run also proves the credential here). It is covered by
  `tests/security/test_base_update_workflow.py` (static checks of the workflow text, and its two decision scripts run against stand-ins for
  `docker` and `gh`), `tests/unit/test_follow_website_base.py` (the script, including hostile website content) and
  `tests/unit/test_base_image_pin.py` (fails when `versions.env` and a `FROM` line disagree), and it was linted with actionlint.
  **Proved on GitHub on 2026-10-27** with the proof in `docs/operations/runbook.md`, "Keeping the base image on the website's pin": a throwaway
  branch (`proof/base-update`, deleted afterwards) with the pin set one release back, so nothing on `main` was touched.
  - Run [40488729010](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/actions/runs/40488729010): `plan` and `open-pr` both green. The plan
    printed `changed=true`, old `sha256:a2b82f3c…`, new `sha256:fbecd461…`, and the new digest's platforms included `linux/386` and `linux/s390x`
    (so the registry check works with the runner's own `docker buildx`). The App token was minted and pull request
    [#55](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/55) was opened by `app/hcw-main-admin`, ready for review, with the
    "platforms compared" box ticked. Its commit is credited to `hcw-main-admin[bot]`. The repository's checks (`lint`, `test`, `image`,
    `catalog-check`, `package`, `e2e`, CodeQL, `pip-audit`, `secret-scan`, `dependency-review`) ran on that pull request and all passed, which is
    what the App token is for.
  - Run [40490178354](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/actions/runs/40490178354): with a commit a person had pushed to
    `base-update/website-base`, the run logged that the pull request was left alone, `open-pr` was skipped, and the person's commit stayed the last
    commit on the branch.
  - Run [40493622020](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/actions/runs/40493622020): after the throwaway branch went back to the
    website's pin, the run logged that the pull request was obsolete, `open-pr` succeeded, and pull request
    [#58](https://github.com/saulpatinojr/HCW-CloudAssessor_AddOn/pull/58) ended closed (not merged) with `base-update/website-base` deleted
    (`create-pull-request` with `delete-branch: true`).
  - The workflow's pull request asks the repository owner for a review (`CODEOWNERS` names the owner for every path), so a proof pull request looks like any other. Two of them (#55 and #57)
    were merged into the throwaway branch by the owner's account, about ten minutes after they opened, before the next step could use them; nothing
    on `main` was affected. The runbook now says to run steps 7 to 11 straight after step 5.
  Still unverified: whether the ruleset "Protect main" option "require extra approval for unattributed changes" asks for an approval on a pull
  request into `main` (the proof's pull requests went into the throwaway branch, which that ruleset does not govern; it is read from the first real
  pull request); the first scheduled run (the daily trigger, 07:37 UTC); what happens when the website moves again while a pull request holds a
  person's commit (only the "left alone" half was seen live); and a run on the Python that `.python-version` names (since
  [HCW-HybridCloudWorks#1707](https://github.com/saulpatinojr/HCW-HybridCloudWorks/issues/1707) both jobs install it with `actions/setup-python`
  instead of using the runner's own older Python; the script ran on the runner's Python before, and it uses only Python's standard library, but no
  run on the chosen version has been seen yet). Scheduled workflows in a public repository are switched off by GitHub after 60 days without repository activity. That switches off
  `base-update` and the weekly `base-follows-website` job together, so after a quiet spell the weekly job is not an independent second
  check. It is also not a full second check at any time: it compares only the image and its digest, so if the website changes only
  `BASE_PYTHON_VERSION` to another minor line, `base-update` refuses and goes red while the weekly job stays green. How to see whether
  either has been switched off, and how to switch them back on, is in `docs/operations/runbook.md`, "If the daily run goes quiet";
  failed `base-update` runs should be watched on their own ("When the run is red").
