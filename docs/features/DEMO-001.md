# DEMO-001 — Build the local FHIR anomaly investigation demo

## Goal

Deliver the complete one-day VeriClaim milestone: a runnable local FastAPI endpoint that loads the existing synthetic FHIR R4 sample, extracts a narrow supported Patient/Coverage/ExplanationOfBenefit subset, runs transparent deterministic anomaly checks, optionally obtains one bounded evidence-grounded Vertex AI Gemini summary, and returns a structured report demonstrable through `/docs`.

## User-visible flow

```text
POST /api/v1/analyze-demo
  -> load approved read-only synthetic FHIR files
  -> perform bounded minimal structural checks
  -> extract supported observed facts with stable evidence IDs
  -> run deterministic anomaly rules
  -> call Vertex AI Gemini zero or one time
  -> validate structured output and evidence references
  -> return the combined JSON report
```

No request upload or arbitrary path is needed. The endpoint analyzes the fixed approved local dataset.

## In scope

- Python, FastAPI, Pydantic, Google Gen AI SDK configured for Vertex AI, pytest, local JSON, and in-memory processing.
- One API operation: `POST /api/v1/analyze-demo`, visible in FastAPI `/docs`.
- Read-only loading of:
  - `dataset/patient_bbuser29999.json`
  - `dataset/coverage_bundle_bbuser29999.json`
  - `dataset/eob_bundle_bbuser29999.json`
- Minimal bounded JSON/FHIR-shape validation for the supported standalone Patient and Coverage/EOB searchset Bundle shapes.
- Explicit extraction of only identifiers/references, Coverage periods, EOB service dates, opaque product/service system+code values, selected exact adjudication category values, and currency needed by the rules.
- Stable evidence IDs that every deterministic signal and Gemini candidate finding can reference.
- Five deterministic rules:
  1. required Patient/Coverage reference resolution;
  2. service-date comparison against present Coverage start/end bounds;
  3. exact duplicate items and repeated opaque product/service codes under a documented definition/window;
  4. exact supported-field arithmetic comparing observed `drugcost` to available `benefit + paidbypatient`, with tolerance and missing-component limitations; and
  5. a fixed documented sample-relative high-amount statistic/threshold.
- One controlled, no-tools Gemini call per successful deterministic analysis, with Pydantic structured-output validation and supplied-evidence reference validation.
- Graceful model failure that returns deterministic output with typed status/limitations.
- Focused unit/integration tests and a resume-quality root README.

## Out of scope

- Strict base FHIR/CARIN conformance, offline NCPDP or other terminology packages, comprehensive FHIR profiling, live terminology lookup, payer semantics, fraud determination, coding validation, medical necessity, clinical/diagnostic conclusions, or payment/coverage decisions.
- Modification of `dataset/`, uploads, remote inputs, arbitrary file paths, persistence, PostgreSQL, pgvector, Supabase, migrations, authentication/RBAC, custom frontend, RAG/policy ingestion, multi-agent application behavior, Google ADK, Agent Platform Runtime, MCP/A2A, model tools, agent memory, model training, cloud deployment, production observability/scalability, real PHI/production claims, or compliance/production-readiness claims.
- A second model repair/fallback call, silent model/provider fallback, autonomous side effects, or generated writes.

## Architecture impact

- Backend: expected yes; the FastAPI application, extractor, rules, Gemini boundary, models, and README must be implemented.
- Testing: expected yes; independent test evidence is required.
- Contract: expected yes; `contracts/openapi.yaml` must define the endpoint and response/error schemas.
- Database: expected no; the approved component is disabled and processing is in memory.
- Frontend: expected no; FastAPI `/docs` is the interface.
- Infrastructure: expected no; no deployment/container/service work is required.

The architecture specialist must confirm every impact flag before the architecture gate.

## Contract impact

Define `POST /api/v1/analyze-demo` with no application input payload and explicit schemas that separate:

- source/analysis metadata;
- observed facts and evidence index;
- deterministic rule results/signals;
- Gemini status, candidate findings, missing evidence, and limitations;
- global limitations; and
- sanitized model/configuration metadata.

The contract must define deterministic-pipeline failures separately from Gemini partial/failure states. A successful deterministic analysis with Gemini unavailable or invalid remains a successful combined report; raw provider errors and secrets must not appear.

## Security considerations

- Treat local JSON/FHIR strings and model output as untrusted; bound files, strings, arrays, numeric values, and model output.
- Use allowlisted repository-owned input paths only and never modify source files.
- Keep credentials/private configuration outside Git, prompts, responses, fixtures, and logs.
- Minimize model input and exclude unnecessary patient attributes/raw resources.
- Make no tools available to Gemini and enforce at most one call.
- Validate model schema and every cited evidence ID before accepting candidate findings.
- Local unauthenticated `/docs` is for the synthetic demonstration only and is not a deployment security model.

## Dependencies

- FOUNDATION-001 is complete historical groundwork.
- The 2026-08-15 project scope reset is approved and `INCEPTION_READY`.
- Vertex AI authentication/configuration is externally available and smoke-tested; tests must not depend on live credentials.
- DATA-001 is cancelled and is not a dependency. Its source inventory is useful history, but its CARIN/offline terminology contract and unresolved review blockers must not be imported as demo requirements.

## Acceptance criteria

1. `POST /api/v1/analyze-demo` runs locally and is demonstrable from `/docs` with no separate frontend/database/upload/arbitrary path.
2. Only the approved three JSON files are loaded; the supported subset and minimal structural checks are explicit, bounded, and tested; `dataset/` remains byte-identical.
3. The response distinctly represents observed facts, stable evidence references, deterministic signals, Gemini candidate explanations, missing evidence, limitations, and sanitized model/configuration metadata.
4. Three to five rules are implemented; target all five approved checks when the sample/test variants support them honestly. Each rule exposes stable ID, exact inputs/formula/threshold/tolerance, evidence, and limitations.
5. Rules and wording do not invent payer-specific, terminology, fraud, coding, clinical, coverage, payment, diagnostic, or medical-necessity semantics.
6. One or zero Google Gen AI SDK/Vertex AI calls occur per analysis, with no tools or loops and only minimized structured synthetic facts/signals/evidence/limitations sent.
7. Gemini structured output is validated by Pydantic and evidence allowlist. Any model/configuration/timeout/provider/parsing/schema/citation failure preserves deterministic output and performs no repair/fallback call.
8. OpenAPI validates and matches implementation behavior for full success, deterministic failure, and Gemini partial/failure states.
9. Focused unit/integration tests cover rules, extraction, endpoint, model success/failures, citations, call count, no-live-credential operation, and source immutability.
10. The root README contains setup, architecture, exact rule descriptions, example request/response, graceful failure, tests, limitations, and a resume-ready summary without CARIN/compliance/production/healthcare-validity claims.
