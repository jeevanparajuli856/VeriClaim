# VeriClaim Project Definition

> This document is the product source of truth. Classification labels are **Confirmed**, **Assumption**, **Recommendation**, and **Open question**.

## 1. Project summary

### Working name

VeriClaim

### One-sentence description

VeriClaim is a polished local demonstration that extracts a small supported subset of synthetic FHIR R4 data, applies transparent anomaly checks, and uses Vertex AI Gemini once to produce a bounded evidence-referenced investigation summary through FastAPI `/docs`.

### Status

**INCEPTION_READY.** The one-day backend milestone is complete, HARDEN-001 is PR-ready, and a separate local frontend prototype is the approved proposed follow-up. The frontend remains disabled until FRONTEND-001 planning resolves and records its technology and integration decisions.

## 2. Problem statement

### Confirmed

- A resume project needs a working, understandable end-to-end demonstration that can be built and shown locally in one focused day.
- The existing repository contains versioned synthetic CMS Blue Button FHIR R4 examples for one beneficiary, including Patient, Coverage, and ExplanationOfBenefit resources.
- Deterministic rules should identify inspectable signals; an LLM should summarize supplied evidence rather than act as the anomaly detector or decision-maker.

### Assumption

- The ten EOB resources and related Patient/Coverage records are sufficient to demonstrate the selected rules, including repeated product codes, amount variation, and reference/date checks. Tests may use clearly labeled project-authored synthetic variants outside `dataset/` to exercise failure paths without changing the source corpus.

## 3. Goal and intended outcome

### Primary goal

Deliver a working local demonstration in one day that loads the approved synthetic FHIR files, extracts a narrow explicit subset, runs five deterministic checks, calls Vertex AI Gemini once, validates its structured output, and returns an evidence-grounded JSON report from `POST /api/v1/analyze-demo`.

### Secondary goals

- Make the deterministic reasoning easy to explain in a resume discussion.
- Demonstrate safe use of structured LLM output and graceful provider failure.
- Provide focused unit/integration tests and a resume-quality root README.

### Non-goals

- Production healthcare operation, regulatory compliance, real PHI, production claims, or production readiness.
- Fraud determination, claim approval/denial, payment action, medical necessity, coding validation, diagnosis, or clinical decision-making.
- Strict CARIN conformance, comprehensive FHIR profiling, terminology packages, payer-specific semantics, or benchmark research infrastructure.
- PostgreSQL, pgvector, Supabase, migrations, persistence, authentication, RBAC, a custom frontend, RAG, policy ingestion, multi-agent orchestration, Google ADK, Agent Platform Runtime, MCP/A2A, agent memory, cloud application deployment, production observability, or production scaling.

## 4. Intended user

| Classification | User | Need | Interaction |
|---|---|---|---|
| Confirmed | Resume reviewer, interviewer, or developer | Understand the design and see a credible local AI-assisted data workflow | Starts FastAPI, opens `/docs`, invokes the demo endpoint, and inspects the structured response |

The model is an external summarization component, not an accountable user or decision-maker.

## 5. Core use case

1. Start the local FastAPI application with externally configured Vertex AI credentials.
2. Invoke `POST /api/v1/analyze-demo` from FastAPI `/docs`.
3. Load the three approved versioned JSON resources from `dataset/` without modifying them.
4. Perform minimal JSON/FHIR-shape checks and extract only the supported facts.
5. Run the deterministic rules and create stable evidence references.
6. Send only the extracted synthetic facts, signals, evidence references, and limitations to Gemini in one controlled call.
7. Validate the structured Gemini response with Pydantic and return the combined report.
8. If Gemini is unavailable, times out, or returns invalid output, return the deterministic report with explicit model-failure metadata.

## 6. Confirmed capabilities

- Local, versioned JSON input and in-memory processing only.
- Explicit extraction of identifiers/references, Coverage periods, EOB service dates, product/service codes as opaque values, and narrowly selected monetary values/currencies.
- Five deterministic, explainable checks:
  1. missing, malformed, broken, or ambiguous Patient/Coverage references;
  2. EOB service dates outside a referenced Coverage period when the relevant boundary is present;
  3. exact duplicate items and repeated opaque product/service codes within the supplied sample;
  4. an explicitly named sample-field arithmetic check comparing observed `drugcost` with the available `benefit` and `paidbypatient` components, reported only as a possible inconsistency with missing-component limitations; and
  5. a documented sample-relative high-amount threshold, reported as unusual only within this small sample.
- One Google Gen AI SDK call configured for Vertex AI per analysis.
- Pydantic validation for both application boundaries and Gemini structured output.
- FastAPI `/docs` as the only user interface.

No rule assigns fraud, clinical, coding, coverage, payment, or medical-necessity meaning.

## 7. Scope

### Confirmed one-day scope

- Python, FastAPI, Pydantic, Google Gen AI SDK configured for Vertex AI, pytest, local JSON, and in-memory processing.
- One endpoint: `POST /api/v1/analyze-demo`.
- Patient, Coverage, and ExplanationOfBenefit only, with a documented field-level support list.
- Minimal structural checks rather than strict FHIR or CARIN validation.
- Stable evidence identifiers connecting facts, signals, and model findings.
- Graceful model/configuration/API failure with deterministic results retained.
- Focused tests and a root README covering setup, architecture, example request/response, limitations, and a resume-ready summary.

### Explicitly out of scope

All production platform concerns and research infrastructure listed in the Non-goals section are outside this milestone and do not block it.

### Future possibilities, not commitments or blockers

- More synthetic scenarios, additional resource types, richer rule configuration, a custom UI, persistence, authentication, RAG, deployment, observability, or controlled evaluation.
- Any real-data, regulated, clinical, coding, payer, or consequential workflow would require a new approved scope, architecture, and safety review.

## 8. Functional requirements

### Confirmed

- Load only the approved local paths; never discover remote input or modify `dataset/`.
- Reject malformed JSON and unsupported top-level resource shapes with clear errors while preserving source-file identity.
- Keep observed facts, deterministic anomaly signals, Gemini candidate explanations, evidence references, missing evidence, limitations, and model/configuration metadata distinct in the response.
- Give every extracted fact and deterministic signal a stable evidence reference.
- Allow each Gemini finding to cite only supplied evidence references; reject unknown references.
- Make one controlled model call at most; do not expose tools or agent loops.
- Treat Gemini output as untrusted until Pydantic and evidence-reference validation pass.
- On model timeout, provider/configuration error, invalid JSON, invalid schema, or unsupported evidence reference, return deterministic results and a bounded failure status instead of failing the whole analysis.
- Record only sanitized model/configuration metadata such as provider, configured model name, prompt/schema version, invocation status, latency/token metadata when available, and validation status. Do not expose credentials or private project configuration.

## 9. Non-functional requirements

### Confirmed

- **Time:** the implementation and documentation must fit one focused development day.
- **Explainability:** every rule has a stable identifier, plain-language description, explicit inputs, threshold/formula, and evidence references.
- **Reliability:** deterministic analysis is available even when Vertex AI is unavailable or returns invalid output.
- **Privacy:** only the approved synthetic files and minimized derived facts may cross the Vertex AI boundary; no secrets, real PHI, or production claims.
- **Maintainability:** prefer small pure extraction/rule functions, explicit Pydantic models, thin routes, and no speculative infrastructure.
- **Demonstrability:** a reviewer can run the app locally and complete the flow from `/docs` without a separate frontend.

### Recommendation

- Freeze thresholds and prompt/schema versions as named constants during DEMO-001 so output remains reproducible and easy to discuss.

## 10. Data and privacy

### Confirmed data

- `dataset/patient_bbuser29999.json`
- `dataset/coverage_bundle_bbuser29999.json`
- `dataset/eob_bundle_bbuser29999.json`
- `dataset/readme.txt` as provenance context, not model input unless a specifically extracted non-sensitive fact is needed

These files are approved synthetic local-development input. DATA-001 recorded immutable inventory and provenance limitations; its cancellation does not erase those useful historical facts or turn its strict compatibility contract into an active milestone dependency.

### Data boundary

```text
read-only dataset/ -> minimal parser/extractor -> in-memory facts and signals
                                            -> one Vertex AI Gemini request
                                            <- validated structured summary
                                            -> FastAPI JSON response
```

- Raw files remain unchanged and are not persisted elsewhere by the application.
- Gemini receives only the minimum structured synthetic facts/signals needed for summarization, not credentials, environment values, unrestricted raw resources, real PHI, or production data.
- Generated output stays in memory and in the API response; application persistence is out of scope.

### Open privacy/compliance questions

None block the local synthetic-only milestone. No compliance claim is made.

The proposed local frontend does not change the data classification or authorize shared deployment, real PHI, persistence, or browser-held provider credentials.

## 11. Security and trust boundaries

### Confirmed

- Local files and FHIR string values are untrusted input and must not become instructions, paths, code, HTML, or tool arguments.
- Vertex AI Gemini is an external, fallible summarizer. Its output cannot create anomaly signals or consequential decisions.
- Application Default Credentials and runtime configuration stay outside Git and out of responses/logs.
- The model has no tools, no data mutation ability, and no autonomous loop.
- Local unauthenticated `/docs` is acceptable only for this local synthetic demo; it is not an approved deployment security model.

### Human authority boundary

Any interpretation beyond the displayed synthetic evidence, and every fraud, coverage, payment, coding, medical-necessity, diagnostic, clinical, or production action, remains outside the application and under qualified human authority.

## 12. External integration

| System/provider | Purpose | Status |
|---|---|---|
| Local versioned `dataset/` | Synthetic FHIR R4 demonstration input | Confirmed |
| Vertex AI Gemini through Google Gen AI SDK | One bounded structured investigation summary | Confirmed; local ADC/configuration smoke-tested and kept outside Git |

## 13. Constraints

- One focused development day and one developer-oriented demonstration flow.
- Existing dataset is read-only and must remain byte-identical.
- Network access is needed only for the optional model-backed portion; deterministic analysis must survive its failure.
- No separate database, frontend, identity system, container platform, orchestration framework, retrieval system, or deployment target.

## 14. Success criteria

The milestone succeeds when:

- `POST /api/v1/analyze-demo` works from FastAPI `/docs` against the existing synthetic data.
- The response clearly separates facts, five deterministic rule results/signals, Gemini candidate explanations, references, missing evidence, limitations, and sanitized model metadata.
- Model/configuration/API failures leave a useful deterministic report.
- Unit tests cover extraction and each rule; integration tests cover endpoint success, invalid model output, provider failure, and source-dataset immutability.
- The root README contains setup, architecture, example request/response, limitations, and a concise resume-ready project summary.
- The project makes no strict CARIN, production-readiness, fraud, clinical, coding, payment, coverage, medical-necessity, HIPAA, or regulatory claim.

## 15. Assumptions register

| ID | Assumption | Validation |
|---|---|---|
| A-001 | The existing sample plus project-authored test variants can exercise all five rules without modifying `dataset/`. | Confirm during DEMO-001 tests; if a rule cannot be exercised honestly, keep 3–4 supported rules rather than inventing semantics. |

## 16. Recommendations

| ID | Recommendation | Rationale | Approval needed? |
|---|---|---|---|
| R-001 | Keep the API request body empty or configuration-free and analyze the fixed approved dataset. | Produces the smallest safe `/docs` demonstration and prevents path/upload scope growth. | No; consistent with approved direction. |
| R-002 | Return HTTP 200 with explicit `gemini.status` for provider/output failure after deterministic analysis succeeds; reserve 4xx/5xx for request or deterministic pipeline failure. | Makes fallback behavior easy to demonstrate and test. | No; implementation detail for DEMO-001 contract review. |

## 17. Open questions

No unresolved decision blocks the completed backend milestone or HARDEN-001. Before FRONTEND-001 implementation, task planning must resolve the frontend technology, package manager/lock strategy, local frontend/backend integration pattern, and project verification commands. No stack is approved merely by creating the proposed task.

## 18. Proposed backlog

These records reflect completed work and the user-approved task order. A PROPOSED task still requires the normal architecture, contract, implementation, verification, security, review, and human/Gemini gates.

### Historical tasks

| Task | Status | Disposition |
|---|---|---|
| FOUNDATION-001 | DONE | Preserved completed foundation/research history. Its production-scale recommendations are historical context, not active milestone requirements. |
| DATA-001 | CANCELLED | Preserved reports and contracts document substantial compatibility work and the final review blockers. The task was cancelled on 2026-08-15 because strict CARIN/offline terminology/comprehensive compatibility work was superseded by this approved scope reset. |
| DEMO-001 | DONE | Delivered and merged the local FastAPI anomaly-investigation demonstration and its CI remediation. |

### Approved task order

| Order | Task ID | Status | Title | Purpose | Depends on |
|---:|---|---|---|---|---|
| 1 | HARDEN-001 | PR_READY | Harden prompt isolation and dependency reproducibility | Close the two accepted DEMO-001 defense-in-depth findings without changing the API or product boundary. | DEMO-001 (DONE) |
| 2 | FRONTEND-001 | PROPOSED | Build the local investigation dashboard prototype | Add an accessible local visual prototype over the existing API after explicitly approving/enabling the frontend technology and integration architecture. | HARDEN-001 (must be DONE) |

**Next task:** FRONTEND-001, only after HARDEN-001 is merged and closed. It is intentionally left PROPOSED; its first work is architecture/source-of-truth reconciliation, not frontend implementation.

## 19. Approved project-level decisions

- Python, FastAPI, Pydantic, Google Gen AI SDK configured for Vertex AI, pytest, local JSON, in-memory processing, and FastAPI `/docs`.
- Backend enabled; separate frontend and database disabled.
- Existing synthetic Patient/Coverage/EOB files are the only application input for the demonstration.
- One bounded Gemini call per analysis with structured Pydantic-validated output and evidence-reference enforcement.
- Deterministic rules remain authoritative for signals; Gemini is a candidate-explanation summarizer only.
- No production, real-PHI, compliance, CARIN-conformance, payer, clinical, coding, fraud, or autonomous-action claim.

## 20. Related documents

- `docs/architecture/SYSTEM.md`
- `docs/adr/`
- `.ai/project.json`
- `.ai/tasks/FOUNDATION-001/`
- `.ai/tasks/DATA-001/`
- `.ai/tasks/DEMO-001/`
- `.ai/tasks/HARDEN-001/`
- `.ai/tasks/FRONTEND-001/`
- `contracts/fhir/data-001/` (preserved historical DATA-001 artifacts, not an active DEMO-001 dependency)
