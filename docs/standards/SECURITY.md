# Security standards

## Active local-demo baseline

- Use only the approved synthetic files; never introduce real PHI or production claims.
- Treat local JSON, FHIR strings, and model output as untrusted.
- Allowlist input paths and bound JSON/model sizes, collection lengths, numeric values, timeouts, and output tokens.
- Keep Application Default Credentials and real runtime values outside Git, prompts, responses, fixtures, and logs.
- Send only minimized structured synthetic facts/signals to Vertex AI Gemini.
- Make at most one model call, expose no tools, and permit no data modification or external side effect.
- Treat Gemini output as candidate explanation only. Require Pydantic schema validation and resolvable evidence references.
- Preserve deterministic results on provider/configuration/output failure and redact raw provider errors.
- Bind local demonstration serving conservatively; unauthenticated `/docs` is not approved for shared or cloud deployment.
- Scan for committed secrets and review dependencies through the repository verification baseline.

## Forbidden claims/actions

- hard-coded credentials, production secrets, real PHI, or production claims;
- fraud determination, claim approval/denial, payment/coverage/coding/medical-necessity/diagnostic/clinical decisions;
- arbitrary file/network access, unrestricted tools, silent provider fallback, or autonomous loops;
- claims of HIPAA compliance, CARIN conformance, production readiness, or healthcare validity.

Authentication, RBAC, production logging, rate limiting, cloud IAM, and regulated-data controls are future requirements only if the scope changes to a shared/deployed system.
