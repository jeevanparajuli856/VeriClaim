# VeriClaim Project Definition

> This document is the product source of truth. Classification labels are **Confirmed**, **Assumption**, **Recommendation**, and **Open question**.

## 1. Project summary

### Working name

VeriClaim

### One-sentence description

VeriClaim is a polished local demonstration that extracts a small supported subset of synthetic FHIR R4 data, applies transparent anomaly checks, optionally uses Vertex AI Gemini once for a bounded evidence-referenced summary, and presents the result in an accessible local dashboard.

### Status

**INCEPTION_READY.** The backend milestone is complete and the final local-prototype task, FRONTEND-001, is ready for its human-started Gemini implementation. ADR-0005 approves and enables a Node.js 24 LTS/React/TypeScript/Vite dashboard over the unchanged API; integration, verification, security, review, and human merge gates remain.

## 2. Problem statement

### Confirmed

- A resume project needs a working, understandable end-to-end demonstration that can be built and shown locally in one focused day.
- The existing repository contains versioned synthetic CMS Blue Button FHIR R4 examples for one beneficiary, including Patient, Coverage, and ExplanationOfBenefit resources.
- Deterministic rules should identify inspectable signals; an LLM should summarize supplied evidence rather than act as the anomaly detector or decision-maker.

### Assumption

- The ten EOB resources and related Patient/Coverage records are sufficient to demonstrate the selected rules, including repeated product codes, amount variation, and reference/date checks. Tests may use clearly labeled project-authored synthetic variants outside `dataset/` to exercise failure paths without changing the source corpus.

## 3. Goal and intended outcome

### Primary goal

Deliver a working local demonstration that loads the approved synthetic FHIR files, extracts a narrow explicit subset, runs five deterministic checks, optionally calls Vertex AI Gemini once, validates its structured output, returns an evidence-grounded report from `POST /api/v1/analyze-demo`, and presents it in a local accessible dashboard.

### Secondary goals

- Make the deterministic reasoning easy to explain in a resume discussion.
- Demonstrate safe use of structured LLM output and graceful provider failure.
- Make evidence references and the distinction between deterministic signals and Gemini candidate text easy to inspect visually.
- Provide focused unit/integration tests and a resume-quality root README.

### Non-goals

- Production healthcare operation, regulatory compliance, real PHI, production claims, or production readiness.
- Fraud determination, claim approval/denial, payment action, medical necessity, coding validation, diagnosis, or clinical decision-making.
- Strict CARIN conformance, comprehensive FHIR profiling, terminology packages, payer-specific semantics, or benchmark research infrastructure.
- PostgreSQL, pgvector, Supabase, migrations, persistence, authentication, RBAC, server-side frontend runtime, RAG, policy ingestion, multi-agent orchestration, Google ADK, Agent Platform Runtime, MCP/A2A, agent memory, cloud/shared deployment, production observability, or production scaling.

## 4. Intended user

| Classification | User | Need | Interaction |
|---|---|---|---|
| Confirmed | Resume reviewer, interviewer, or developer | Understand the design and see a credible local AI-assisted data workflow | Starts FastAPI and the Vite dashboard, runs the fixed analysis, and navigates evidence-linked results |

The model is an external summarization component, not an accountable user or decision-maker.

## 5. Core use case

1. Start FastAPI on the approved local origin and the Vite dashboard on its local origin; Vertex AI configuration is optional and remains backend-only.
2. Open the dashboard and activate **Run analysis**.
3. The browser sends the bodyless relative `POST /api/v1/analyze-demo` through Vite's fixed same-origin `/api` development proxy.
4. FastAPI loads the three approved versioned JSON resources, extracts only supported facts, runs five deterministic rules, and creates stable evidence references.
5. When configured, send only minimized facts, signals, evidence references, and limitations to Gemini in one controlled call; validate its response with Pydantic.
6. Return the combined report, or deterministic content with explicit model-failure metadata when Gemini is unavailable/invalid.
7. Render deterministic results first, label Gemini text as candidate-only, and let the reviewer navigate each signal/finding to returned evidence.

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
- A Node.js 24 LTS/React/strict TypeScript/Vite single-page local dashboard using generated OpenAPI types and a fixed `/api` development proxy.
- Accessible loading, success, deterministic-only, typed pipeline error, retry, and evidence-navigation behavior; FastAPI `/docs` remains available for API inspection.

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
- Node.js 24 LTS, React, strict TypeScript, Vite, npm/package-lock, generated OpenAPI types, Vitest/Testing Library, and Playwright Chromium for the final dashboard.
- A bodyless same-origin browser request through a fixed local Vite proxy to `http://127.0.0.1:8000`; no backend CORS change.

### Explicitly out of scope

All production platform concerns and research infrastructure listed in the Non-goals section are outside this milestone and do not block it.

### Future possibilities, not commitments or blockers

- More synthetic scenarios, additional resource types, richer rule configuration, persistence, authentication, RAG, deployment, observability, or controlled evaluation.
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
- The dashboard invokes only the approved relative bodyless operation, renders all API values as inert plain text, keeps deterministic/model/evidence sections distinct, and uses response-local evidence navigation.
- Browser failures and incompatible responses produce bounded retryable states without raw bodies/exceptions; the browser stores nothing persistently and never receives provider configuration.

## 9. Non-functional requirements

### Confirmed

- **Time:** the implementation and documentation must fit one focused development day.
- **Explainability:** every rule has a stable identifier, plain-language description, explicit inputs, threshold/formula, and evidence references.
- **Reliability:** deterministic analysis is available even when Vertex AI is unavailable or returns invalid output.
- **Privacy:** only the approved synthetic files and minimized derived facts may cross the Vertex AI boundary; no secrets, real PHI, or production claims.
- **Maintainability:** prefer small pure extraction/rule functions, explicit Pydantic models, thin routes, contract-generated frontend types, bounded display components, and no speculative infrastructure.
- **Demonstrability:** a reviewer can run FastAPI and the dashboard locally, complete the primary flow visually, and trace signals/findings to evidence.
- **Accessibility:** the dashboard provides semantic structure, keyboard operation, visible focus, readable AA contrast, responsive layout, and reduced-motion behavior.
- **Reproducibility:** frontend dependencies install from `package-lock.json` with Node.js 24/npm, and contract/type generation, lint, typecheck, unit, build, browser, and audit checks fail closed.

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
                                            -> fixed local Vite proxy -> in-memory dashboard
```

- Raw files remain unchanged and are not persisted elsewhere by the application.
- Gemini receives only the minimum structured synthetic facts/signals needed for summarization, not credentials, environment values, unrestricted raw resources, real PHI, or production data.
- Generated output stays in memory and in the API response; application persistence is out of scope.

### Open privacy/compliance questions

None block the local synthetic-only milestone. No compliance claim is made.

The local frontend does not change the data classification or authorize shared deployment, real PHI, persistence, or browser-held provider credentials.

## 11. Security and trust boundaries

### Confirmed

- Local files and FHIR string values are untrusted input and must not become instructions, paths, code, HTML, or tool arguments.
- Vertex AI Gemini is an external, fallible summarizer. Its output cannot create anomaly signals or consequential decisions.
- Application Default Credentials and runtime configuration stay outside Git and out of responses/logs.
- The model has no tools, no data mutation ability, and no autonomous loop.
- Returned API/FHIR/model strings remain untrusted plain text in React and never become HTML, Markdown, URLs, selectors, scripts, or styles.
- The browser calls only the same-origin relative API path, has no provider/API-origin environment variable, and keeps results only in memory.
- Local unauthenticated `/docs` and dashboard serving are acceptable only for this local synthetic demo; they are not an approved deployment security model.

### Human authority boundary

Any interpretation beyond the displayed synthetic evidence, and every fraud, coverage, payment, coding, medical-necessity, diagnostic, clinical, or production action, remains outside the application and under qualified human authority.

## 12. External integration

| System/provider | Purpose | Status |
|---|---|---|
| Local versioned `dataset/` | Synthetic FHIR R4 demonstration input | Confirmed |
| Vertex AI Gemini through Google Gen AI SDK | One bounded structured investigation summary | Confirmed; local ADC/configuration smoke-tested and kept outside Git |
| Local Vite development server | Same-origin dashboard and fixed `/api` proxy to local FastAPI | Confirmed; development-only, no hosting/deployment selection |

## 13. Constraints

- One bounded local-prototype task and one reviewer-oriented dashboard flow.
- Existing dataset is read-only and must remain byte-identical.
- Network access is needed only for the optional model-backed portion; deterministic analysis must survive its failure.
- No database, identity system, container platform, orchestration framework, retrieval system, or deployment target.
- Node.js 24 LTS/npm and lock-matched Playwright Chromium are required for frontend build/test; browser runtime has no configurable remote API target.

## 14. Success criteria

The milestone succeeds when:

- `POST /api/v1/analyze-demo` works from FastAPI `/docs` and through the fixed local dashboard proxy against the existing synthetic data.
- The response clearly separates facts, five deterministic rule results/signals, Gemini candidate explanations, references, missing evidence, limitations, and sanitized model metadata.
- Model/configuration/API failures leave a useful deterministic report.
- Unit tests cover extraction and each rule; integration tests cover endpoint success, invalid model output, provider failure, and source-dataset immutability.
- Frontend unit/component/browser tests cover response states, safe rendering, evidence focus/navigation, accessibility-critical behavior, responsive layouts, generated contract freshness, and credential-free proxy integration.
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

No unresolved product or architecture decision blocks FRONTEND-001. ADR-0005 approves Node.js 24 LTS, React, strict TypeScript, Vite, npm/package-lock, generated OpenAPI types, a fixed local same-origin `/api` proxy, and Vitest/Testing Library/Playwright verification. Normal task gates and the human-started Gemini handoff still apply.

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
| 1 | HARDEN-001 | DONE | Harden prompt isolation and dependency reproducibility | Closed the accepted DEMO-001 defense-in-depth findings without changing the API or product boundary. | DEMO-001 (DONE) |
| 2 | FRONTEND-001 | IMPLEMENTATION | Build the local investigation dashboard prototype | Add the final accessible local visual prototype over the unchanged API using ADR-0005. | HARDEN-001 (DONE) |

**Final planned project task:** FRONTEND-001. Architecture/source-of-truth reconciliation precedes contract validation and the manually started Gemini implementation gate.

## 19. Approved project-level decisions

- Python, FastAPI, Pydantic, Google Gen AI SDK configured for Vertex AI, pytest, local JSON, and in-memory backend processing.
- Backend enabled; Node.js 24 LTS/React/strict TypeScript/Vite frontend enabled; database disabled.
- npm with committed `package-lock.json`, generated OpenAPI TypeScript types, and Vitest/Testing Library plus Playwright browser verification.
- Browser uses only the relative bodyless API operation through a fixed local Vite `/api` proxy to `http://127.0.0.1:8000`; no CORS/backend change or deployment target.
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
