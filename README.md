# VeriClaim

VeriClaim is being re-incepted as a one-day local resume demonstration: load the existing synthetic FHIR R4 Patient/Coverage/ExplanationOfBenefit samples, run five transparent deterministic anomaly checks, and use one bounded Vertex AI Gemini call to create an evidence-referenced candidate investigation summary through FastAPI `/docs`.

## Current status

Project re-inception is `INCEPTION_READY`. Application implementation has not started. The single proposed task is `DEMO-001 — Build the local FHIR anomaly investigation demo`; it has not been created.

The approved stack is Python, FastAPI, Pydantic, Google Gen AI SDK configured for Vertex AI, pytest, local versioned JSON, and in-memory processing. There is no database, separate frontend, authentication/RBAC, RAG, agent framework, cloud deployment, or production healthcare scope.

See [docs/PROJECT.md](docs/PROJECT.md) for requirements and [docs/architecture/SYSTEM.md](docs/architecture/SYSTEM.md) for the architecture. DEMO-001 must turn this into the final resume-quality README with runnable setup, architecture, example request/response, limitations, tests, and resume summary.

## Safety boundary

This is a synthetic-data demonstration and research prototype. It does not determine fraud, approve or deny claims, make payment/coverage/coding/medical-necessity/diagnostic/clinical decisions, process real PHI, claim CARIN conformance, claim HIPAA compliance, or claim production readiness.
