# Infrastructure

| Path | What |
|---|---|
| `docker/Dockerfile` | The lab image (`docker.io/hybridcloudworks/hcw-addon-cloud-assessment`): two stages on one digest-pinned base, hash-pinned dependencies, no pip at runtime, uid 10001, `HEALTHCHECK`, `CMD python -m cloud_assessment_lab`. `ARG EDITION=lab` is asserted in both stages. |
| `docker/versions.env` | `BASE_IMAGE`, `BASE_DIGEST`, `BASE_PYTHON_VERSION`; CI fails when any `FROM` differs from `BASE_IMAGE@BASE_DIGEST`. |
| `../docker-compose.yml` | Local development only, hardened like the lab host's `docker_container` (read-only root, tmpfs `/tmp`, `cap_drop ALL`, `no-new-privileges`, 512m, 256 pids, one CPU). |

There is no Terraform here and there must not be (AddOn Integration Standard, section 3): the lab host belongs to the
website repository (`lab-host/ansible`, role `addons`), and the Azure appliance belongs to `HCW-CloudAssessor_App`.

First-party packages are copied into `/usr/local/lib/python3.14/site-packages` as source trees (engine, catalog as
`cloud_assessor_core/catalog_data`, lab application) rather than built as wheels, so no build backend enters the image.
`requirements.lock.txt` is `uv export --format requirements-txt --hash --no-dev --no-emit-project --no-emit-workspace`
and is the only input `pip install --require-hashes --no-deps` reads.

Image build, Trivy and the `import azure` image check run in CI (`publish-images.yml`); the authoring container had no
Docker daemon (see `VALIDATION.md`).
