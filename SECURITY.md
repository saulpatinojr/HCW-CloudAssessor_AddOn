# Security policy

Report vulnerabilities privately to security@hybridcloudworks.com (or via GitHub private vulnerability reporting). Please do not open public issues for security findings. Expect an acknowledgement within 3 business days.

Scope highlights: the lab processes uploaded Resource Graph exports in memory only, never connects to a cloud, holds no credentials and has no execution surface; uploads are gated by human verification (fail closed); per-assessment owner tokens are hashed and compared in constant time; logs carry no visitor data. See `docs/security/threat-model.md`. The engine (`cloud-assessor-core`) is owned and released by `https://github.com/saulpatinojr/HCW-CloudAssessor_App`; report engine issues there. Supported version: `main`.
