# VeriClaim local demonstration architecture

> Status: **INCEPTION_READY; frontend decision accepted 2026-08-15.** This is a local synthetic-data demonstration/research prototype, not a production healthcare platform. FRONTEND-001 enables the final local dashboard while preserving the completed backend boundary.

## 1. Architectural objective

Provide the smallest credible end-to-end path from the approved synthetic FHIR-shaped JSON files through transparent deterministic checks and one optional bounded Vertex AI Gemini summary to an accessible local dashboard. The deterministic analysis remains useful when Gemini fails, and the browser never owns provider credentials or analysis authority.

## 2. Active components

| Component | Enabled | Technology | Responsibility |
|---|---:|---|---|
| Local API/backend | Yes | Python, FastAPI, Pydantic | Load fixed inputs, extract the supported subset, run deterministic rules, call Gemini at most once, validate, and return the report |
| Local dashboard | Yes | Node.js 24 LTS, React, strict TypeScript, Vite, npm | Invoke the existing operation and render an accessible read-only evidence investigation view |
| Database | No | — | All processing/output stays in memory; source JSON remains read-only |
| Model integration | Yes | Google Gen AI SDK configured for Vertex AI | Produce one bounded structured candidate summary from supplied synthetic evidence |

PostgreSQL/pgvector, Supabase, Docker as a requirement, server-side frontend rendering, retrieval, identity, agents/tools, analytics, persistence, cloud hosting, and production observability remain inactive and are not task dependencies.

## 3. End-to-end runtime flow

```text
browser at local Vite origin
  -> bodyless same-origin POST /api/v1/analyze-demo
  -> Vite development proxy (only /api; fixed target http://127.0.0.1:8000)
  -> FastAPI route
  -> fixed local dataset loader
  -> supported-subset extractor + five deterministic rules + evidence index
  -> zero/one bounded Vertex AI Gemini call
  -> Pydantic + evidence-reference validation
  <- AnalysisResponse or sanitized DeterministicPipelineErrorResponse
  <- frontend transport guard + in-memory view model
  -> deterministic-first dashboard + evidence navigation
```

The browser does not call FastAPI at a configurable absolute origin, call Vertex AI, read Google Cloud configuration, or send a request body. The fixed development proxy avoids CORS/backend changes. Vite and FastAPI bind locally; this path defines no deployed reverse proxy or shared serving topology.

## 4. Backend boundaries preserved from DEMO-001/HARDEN-001

- **API route:** thin bodyless `POST /api/v1/analyze-demo` handler and response mapping.
- **Dataset loader:** three allowlisted repository-relative source paths, read-only byte loading, JSON parsing, and source metadata.
- **Minimal extractor:** only the documented Patient, Coverage Bundle, and ExplanationOfBenefit Bundle fields.
- **Rule engine/evidence index:** five pure deterministic checks with stable evidence IDs and non-consequential labels.
- **Gemini summarizer:** minimized structured input, fixed system/user role separation, at most one direct SDK/Vertex AI call, and no tools.
- **Response validator/assembler:** Pydantic output validation and exact evidence-reference allowlist.

FRONTEND-001 does not modify these modules, their data limits, the one-call/no-tools boundary, or the public OpenAPI operation.

## 5. Frontend boundaries

### 5.1 Page and components

- **App/page shell:** header/main/footer landmarks, skip link, local synthetic-demo notice, human-authority wording, and responsive layout.
- **Analysis controller:** owns the request, one `AbortController`, duplicate-submit protection, transport guard, and one discriminated UI state. Child display components do not fetch.
- **Contract adapter:** imports generated OpenAPI types and maps contract fields into display-only view models without changing meaning or supplying invented defaults.
- **Source/fact views:** show source identities/counts and observed facts as plain text.
- **Rule results:** show all five results, formula/parameters, signals, missing evidence, and limitations. A completed zero-signal rule remains visible and is not a clean-bill conclusion.
- **Gemini view:** labels summary/findings as candidate and non-authoritative; handles success or each typed fallback independently of deterministic content.
- **Evidence explorer:** resolves exact IDs within the current response, uses application-generated safe DOM target indexes, moves focus to selected evidence, and restores focus on return.
- **Shared UI primitives:** accessible status, disclosure, definition/table/card layouts, evidence controls, and visually hidden live-region content.

No router, server rendering, global state library, service worker, analytics, browser persistence, cache, upload/download, clipboard, or mutation surface is required.

### 5.2 UI state machine

```text
idle --run--> loading --HTTP 200 + guarded response--> success
                  |--typed HTTP 500---------------> pipeline_error
                  |--network/status/parse/shape---> client_error

success | pipeline_error | client_error --retry--> loading
loading --unmount/replacement--> aborted (no stale state commit)
```

- Only one request is active. Loading disables repeat submission and exposes a concise accessible busy status.
- `success` always renders deterministic content first. `gemini.status=success` adds candidate findings; `configuration_error`, `timeout`, `provider_error`, `invalid_output`, and `invalid_evidence` retain deterministic content and show the sanitized fallback.
- A typed deterministic-pipeline HTTP 500 shows only its public code/message and `model_called=false`; it does not fabricate partial results.
- Network, non-JSON, unexpected-status, or minimally incompatible responses use a generic client error. Raw response bodies, exceptions, and private configuration are never displayed.
- Retry replaces rather than merges results. Unknown values or unresolved/duplicate evidence produce explicit incompatible/data-integrity UI rather than a crash or guessed meaning.

### 5.3 Contract/type boundary

`contracts/openapi.yaml` is sufficient and unchanged. The frontend commits deterministically generated TypeScript types at `frontend/src/api/generated/schema.d.ts` and verifies regeneration is clean. Network parsing starts as `unknown`; lightweight top-level/discriminant checks protect rendering because compile-time types alone are not runtime validation. No parallel handwritten API schema is authoritative.

The only browser transport is `fetch("/api/v1/analyze-demo", { method: "POST" })` with no body. Vite proxies only `/api` to `http://127.0.0.1:8000`. Browser/query/user configuration cannot select another origin.

## 6. Supported backend extraction boundary

### Patient

- `resourceType`, `id`, and only identifier/reference facts needed to resolve links.
- Names, addresses, birth dates, narratives, and unnecessary patient attributes are not sent to Gemini.

### Coverage

- Bundle/resource identity, Coverage `id`, status as an observed opaque value, `beneficiary.reference`, and optional period bounds.

### ExplanationOfBenefit

- Bundle/resource identity, EOB `id`, patient/coverage references, billable/service dates, item sequence, opaque product/service system+code, selected adjudication codes, numeric values, and currency.
- Displays and systems are untrusted labels and do not establish terminology or domain correctness.

### Minimal structural checks

- UTF-8 JSON objects in expected standalone Patient and searchset Bundle shapes.
- Required bounded identities, references, arrays/objects, date strings, numeric values, and strings.
- One-to-many identity indexing preserves duplicates for the reference-integrity rule.
- Monetary numbers are finite decimals; currencies compare only by exact equality.
- Limits remain: 1 MiB/source file, 100 Bundle entries, 100 EOB items, 32 adjudications/item, 16 codings/concept, and 2,048 characters/extracted string.

This is not strict base FHIR, profile, CARIN, NCPDP, or terminology validation.

## 7. Deterministic rule boundary

Each rule returns its stable ID, execution status, signals, rationale, evaluated inputs, evidence references, formula/parameters, missing evidence, and limitations. Priorities are `information` or `review`, not fraud, clinical, payment, coverage, coding, or risk scores.

1. **`REF-001` — reference integrity:** exact local relative Patient/Coverage reference resolution, including missing, malformed, wrong-type, unresolved, and ambiguous references; never dereference URLs.
2. **`DATE-001` — coverage-date bound:** inclusive comparison of item `servicedDate` against present bounds of uniquely resolved Coverages; missing values are missing evidence and `billablePeriod` is not substituted.
3. **`REPEAT-001` — duplicate/repetition:** exact documented item signatures and exact repeated opaque system+code values only; no near-match or product semantics.
4. **`AMOUNT-001` — observed amount relationship:** exact selected benefit/paidbypatient/drugcost categories, one same-currency finite value each, and signal only when `abs(drugcost - (benefit + paidbypatient)) > 0.01`; missing/duplicates/currency mismatch are missing evidence.
5. **`OUTLIER-001` — sample-relative high amount:** exact-currency groups with at least four values and threshold `Q3 + 1.5 * IQR`; no currency conversion or generalization beyond the sample.

## 8. Response and evidence boundary

The response keeps source metadata, observed facts, five rule results/signals, the evidence index, Gemini status/findings, missing evidence, limitations, and sanitized model metadata separate. Fact IDs use fixed source aliases plus RFC 6901 pointers; signal IDs use stable rule IDs and canonical ordinals. Application-generated evidence IDs, never untrusted content, establish navigation identity.

The dashboard builds a response-local exact-ID map. Finding/signal reference controls reveal the matching evidence record and its source refs. Safe DOM IDs are generated from record indexes instead of using returned values in selectors. Missing/duplicate targets show a data-integrity warning and remain inert.

Gemini statuses remain `success`, `configuration_error`, `timeout`, `provider_error`, `invalid_output`, and `invalid_evidence`. Only success contains candidate findings, and every finding cites one or more supplied evidence IDs.

## 9. Trust and safe-rendering boundaries

- Dataset values, FHIR strings, evidence summaries, API data, and model output are untrusted.
- React text interpolation is used for returned values. `dangerouslySetInnerHTML`, `innerHTML`, HTML/Markdown execution, dynamic script/style injection, untrusted URLs, and returned values in selectors/event code are prohibited.
- Returned values never become external links. Evidence navigation is internal and resolves only within the current response.
- Browser memory is the only frontend state store; reload clears results.
- ADC, tokens, Google project/location/model values, provider SDKs/errors, raw payload dumps, and secrets stay outside browser code, bundles, UI, logs, and fixtures.
- The backend remains the only component that calls Gemini and validates model schema/evidence. The UI does not upgrade candidate text into authoritative signals or decisions.
- Local unauthenticated serving is acceptable only for this fixed synthetic demonstration. Shared/network/cloud serving requires new identity, abuse-control, configuration, and deployment architecture.

## 10. Environment and dependency boundary

- Node.js 24 LTS is the supported frontend runtime/toolchain major. React, TypeScript, Vite, tests, linting, type generation, and audit dependencies resolve through the committed npm lockfile.
- npm is the only package manager. CI and documented setup use `npm ci`; alternate lockfiles and unpinned ad-hoc runtime CDN dependencies are prohibited.
- Browser application code has no environment-specific API or provider variables. Vite's proxy target is the exact source-controlled local FastAPI origin.
- The existing backend environment owns optional Vertex AI configuration. Browser tests and the real proxy smoke explicitly disable it, requiring no live credentials.
- The production build is verification evidence only. No hosting, domain, TLS, container, CDN, cloud service, or production reverse proxy is selected.

## 11. Failure behavior

| Failure | Backend/API behavior | Dashboard behavior |
|---|---|---|
| Source/shape/limit deterministic failure | Sanitized typed HTTP 500; no model call | Public error code/message, no fabricated partial result, retry |
| Gemini configuration/provider/timeout failure | HTTP 200 with deterministic report and typed fallback | Preserve deterministic content; label model unavailable/failure |
| Gemini invalid schema/output/evidence | HTTP 200 with deterministic report and typed fallback | Preserve deterministic content; show bounded validation fallback |
| Network, Vite proxy, unexpected HTTP/content | No trusted contract response | Generic local-connection/incompatible-response message; no raw body; retry |
| Missing/duplicate evidence target | Contract/data-integrity mismatch | Visible unresolved reference warning; no misnavigation or crash |
| Component/request replacement | Abort active browser request | Ignore stale completion and return through the new state transition |

No browser retry loop, background polling, silent provider fallback, or second model call is introduced. User-initiated retry invokes the complete backend analysis again and is labeled accordingly.

## 12. Accessibility and responsive boundary

- Native semantic controls/landmarks/headings, logical order, skip navigation, visible focus, and keyboard access are required.
- Concise status is announced via a restrained live region; the complete report is not repeatedly announced.
- Text/non-text contrast meets WCAG 2.2 AA and color is never the sole status cue.
- Layout supports representative narrow/mobile and desktop widths without page-level horizontal scrolling; dense facts wrap and true tables may use labeled local overflow.
- `prefers-reduced-motion` is honored; animation is never required for comprehension.
- Evidence navigation moves focus deliberately and offers return to the invoking reference.

## 13. Verification strategy

### Frontend implementation checks (Node.js 24, `frontend/`)

1. `npm ci`
2. `npm run check:api`
3. `npm run lint`
4. `npm run typecheck`
5. `npm run test:unit`
6. `npm run build`
7. install lock-matched Playwright Chromium
8. `npm run test:e2e`
9. `npm audit --audit-level=high`

Unit/component coverage includes transport/adaptation, every UI state/status, concurrent-submit prevention/abort/retry, safe rendering, evidence resolution/focus, and semantic interaction. Playwright covers assembled success/fallback/error flows, keyboard/focus, an automated accessibility scan, mobile/desktop widths, reduced motion, and a credential-free real Vite-to-FastAPI proxy smoke.

CI explicitly provisions Node.js 24 and Chromium before `agentctl.py verify` runs project checks. Contract generation freshness, lockfile install, lint, typecheck, unit, build, browser tests, and high-severity npm audit are required and fail rather than skip when tooling/audit service is unavailable. Existing Python/OpenAPI/backend/agentic/security/source-integrity checks remain required.

Independent testing adds or validates contract-shaped fixtures, all typed pipeline codes, adversarial HTML/instruction-like strings as inert text, unknown response/status handling, fixed proxy configuration, and no-live-credential behavior. Security and final review assess the exact integrated commit.

## 14. Historical and change-control reconciliation

- FOUNDATION-001 and DEMO-001 remain `DONE`; HARDEN-001 must be `DONE` before frontend implementation.
- DATA-001 remains cancelled historical compatibility work and is not a frontend dependency.
- ADR-0003's one-day backend replacement remains historical context; ADR-0005 is the accepted decision that now enables this bounded local frontend without reviving the former production-scale Next.js/database platform.
- ADR-0004 continues to own the backend-only one-call Vertex AI boundary.
- `contracts/openapi.yaml` remains unchanged for FRONTEND-001. Its stale placeholder description in `contracts/README.md` is non-interface documentation hygiene for the orchestrator.

Adding API behavior, persistence, authentication, browser provider access, arbitrary input/targets, shared deployment, production/real-PHI use, or consequential healthcare actions requires a new approved feature, contract/architecture reconciliation, and security review.
