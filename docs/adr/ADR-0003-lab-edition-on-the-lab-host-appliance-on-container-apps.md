# ADR-0003: The lab edition runs on the lab host; the appliance on Azure Container Apps

Status: accepted, 2026-10-10. Scope: this repository (lab); `HCW-CloudAssessor_App` (appliance, by its `REFACTOR_APP.md` sections 12 and 15).

## Context

The website already operates a lab host (`*.lab.hybridcloudworks.com` behind Caddy, configured by the website
repository's Ansible) with a pane model, a status proxy and a hardening baseline, and ADR 0032 there reserves Compose
for Coder. The program decided that every AddOn is one hardened container on that host, published by digest to Docker
Hub, framed by the site. The appliance edition, by contrast, must run inside the client's Azure tenant under a managed
identity, which the lab host can neither offer nor should.

## Decision

- **Lab edition: the lab host.** One `docker_container` named `hcw-addon-cloud-assessment`, image
  `docker.io/hybridcloudworks/hcw-addon-cloud-assessment` by digest, loopback port 18083, hostname
  `cloud-assessment.lab.hybridcloudworks.com`, env from `group_vars`, secret from the host vault
  (`vault_addon_cloud_assessment_turnstile_secret`), run by the website repository's generic `addons` role with
  read-only root, `tmpfs /tmp`, `cap_drop ALL`, `no-new-privileges`, 512m, 256 pids, one CPU, the image's own
  `HEALTHCHECK`, no volumes, no socket, user-namespace remap composing with the image's uid 10001. This repository ships
  no Terraform for the host and only a local `docker-compose.yml` for development.
- **Appliance edition: Azure Container Apps**, specified upstream: one Consumption Container App per client scope with
  a user-assigned managed identity holding `Reader` and `Cost Management Reader`, image by digest, `min_replicas 1`,
  `max_replicas 1` recommended (scale-to-zero is an owner option because the in-memory snapshot is lost), Terraform in
  the App repository. The lab image refuses to start there (`edition.py`), and the appliance image is a different build
  target that is never framed by the site.
- **Publishing** for both is tag-driven, scanned before push (Trivy HIGH/CRITICAL, fixed only), with provenance, SBOM
  and attestation, through the Docker OIDC connection rather than long-lived registry credentials.

## Consequences

- The site's coupling to this AddOn is one digest in `group_vars` plus one app setting; rollback is the previous digest.
- The lab host's resource ceiling gains one container (512m / 256 pids); the website records it next to the Coder
  capacity assertion.
- Running the lab anywhere that offers an identity endpoint is impossible by construction, which keeps the two editions
  from being confused in deployment as well as in code.
