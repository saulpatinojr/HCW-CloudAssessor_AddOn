# Deployment: the Azure appliance (upstream, not here)

The appliance edition (`edition: "appliance"`, live Resource Graph and Cost Management collectors under a user-assigned
managed identity with `Reader` and `Cost Management Reader`, one Consumption Container App, no upload route) is
specified in the upstream repository's plan: `HCW-CloudAssessor_App/REFACTOR_APP.md` (sections 7.3–7.11, 12 and 15),
and will be published from there as its own image. Nothing in this repository deploys to Azure.

Why the **lab** image refuses managed-identity endpoints: `src/cloud_assessment_lab/edition.py` checks, at import of
the application, that no cloud SDK is importable and that none of `IDENTITY_ENDPOINT`, `MSI_ENDPOINT`,
`AZURE_CLIENT_SECRET`, `AZURE_FEDERATED_TOKEN_FILE`, `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` is set, and exits non-zero
otherwise. A lab image started inside an Azure compute environment that offers an identity therefore never serves a
request: the edition boundary (AddOn Integration Standard, section 19; ADR-0008 by analogy) is enforced at runtime, not
only by the absence of packages. `publish-images.yml` proves both: `import azure` fails inside the image, and a
container started with `IDENTITY_ENDPOINT` set exits.

Recommendation carried from the program decisions for the appliance (CONTRACT-DECISIONS item 21): `min_replicas 1`,
`max_replicas 1`; scale-to-zero is an owner option (the in-memory snapshot is lost on idle), not the default.
