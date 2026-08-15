# Security Standards

## Baseline

- least privilege
- secure defaults
- explicit authorization
- input validation
- output encoding where needed
- secure secret handling
- dependency review
- auditability

## Forbidden

- hard-coded credentials
- production secrets in Git
- disabled certificate verification without explicit justification
- authorization based only on frontend state
- destructive production operations without human approval

## Vertex AI development boundary

- Authenticate local development with Google Cloud Application Default Credentials; keep ADC and all runtime values outside Git.
- Send only approved, minimized synthetic/public context to Vertex AI Gemini.
- Treat Gemini output as untrusted candidate findings, never as the sole anomaly signal or a claim decision.
- Require evidence citations plus deterministic schema, authorization, evidence, and governance validation before human review.
- Keep prompts, FHIR data, model output, credentials, and private runtime configuration out of external telemetry.
- Local model connectivity does not approve production credentials/data, Google ADK, Gemini Enterprise Agent Platform Runtime, Cloud Run, GKE, or general Google Cloud hosting.

## Reviews should consider

- authentication
- authorization
- IDOR/BOLA
- injection
- SSRF
- XSS
- CSRF where applicable
- insecure deserialization
- file upload risk
- secret exposure
- logging/privacy
- rate limiting
- dependency/supply-chain risk
