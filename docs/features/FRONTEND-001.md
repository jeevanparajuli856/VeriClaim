# FRONTEND-001 — Build the local investigation dashboard prototype

## Goal

Create a polished, accessible local single-page dashboard that lets a resume reviewer run the existing fixed-dataset analysis and understand the result without using FastAPI `/docs` directly. The dashboard is a read-only view over the existing bodyless `POST /api/v1/analyze-demo` operation; it does not change the backend, model authority, or local synthetic-data boundary.

## Approved technology and local integration

- Runtime/toolchain: Node.js 24 LTS, React, TypeScript in strict mode, and Vite.
- Dependency workflow: npm only, with `package-lock.json` committed and `npm ci` used for reproducible installation.
- Contract typing: generate and commit TypeScript API types from `contracts/openapi.yaml`; CI must prove regeneration is clean.
- Browser integration: the application always calls the relative same-origin path `/api/v1/analyze-demo`. Vite's development server proxies only `/api` to the fixed local allowlisted target `http://127.0.0.1:8000`.
- Testing: Vitest and Testing Library for units/components, plus Playwright Chromium coverage for the browser flow.
- Delivery boundary: `npm run build` proves a production bundle can be created, but deployment, hosting, preview-server integration, and a production reverse proxy are not approved.

The fixed proxy keeps provider credentials and Google Cloud configuration in FastAPI and avoids a CORS or backend change. It is local-development configuration, not an arbitrary browser-configurable API target. The frontend must not read provider credentials, accept a backend URL from query/user input, or use a `VITE_*` variable to redirect API traffic.

## User flow and information architecture

The single page has semantic header, main, and footer landmarks and this ordered flow:

1. A concise local-demo/human-authority notice and one **Run analysis** control.
2. A status region that announces loading, completion, deterministic-only fallback, or deterministic-pipeline failure without moving keyboard focus unexpectedly.
3. On a completed deterministic analysis: source/sample metadata; observed facts; five rule-result sections and their deterministic signals; Gemini status and candidate findings; missing evidence; limitations; sanitized model metadata; and an evidence explorer.
4. Evidence-reference controls beside every signal and candidate finding. Activating a reference selects the exact matching `evidence_index` record, reveals its summary/source references, scrolls it into view, and moves focus to its heading. A clear return control restores focus to the invoking reference.
5. A **Run again** or **Retry** control after completion or failure. Only one submission may be active; repeated activation while loading must not create concurrent calls.

Observed facts, rule execution/results, deterministic signals, Gemini candidate text, missing evidence, limitations, and metadata must remain visibly and semantically distinct. A zero-signal rule is shown as completed with no signals; it is never omitted or described as proof that no anomaly exists. Gemini content is labeled non-authoritative and is never styled as a decision or risk/fraud score.

## UI state model and failure behavior

The analysis controller owns one discriminated state:

- `idle`: no request has been made; show the run control and scope notice.
- `loading`: one request is in flight; disable duplicate submission, expose an accessible busy state, and retain no stale result as if it belonged to the new request.
- `success`: HTTP 200 passed the minimal response guard. Render deterministic content first, then either:
  - `gemini.status=success`, with summary and candidate findings; or
  - `configuration_error`, `timeout`, `provider_error`, `invalid_output`, or `invalid_evidence`, with the sanitized fallback message and all deterministic content retained.
- `pipeline_error`: HTTP 500 matches `DeterministicPipelineErrorResponse`. Show its public code/message, state that no model call occurred, and offer retry. Do not fabricate partial deterministic content.
- `client_error`: network failure, non-JSON response, unexpected HTTP status, or response failing the minimal transport/discriminant guard. Show a generic local-connection or incompatible-response message and retry; never display raw exceptions or response bodies.

An `AbortController` belongs to each request and is cancelled on component teardown or replacement. A retry begins a new state transition and must not merge new and old evidence. Unknown enum values, missing reference targets, and malformed optional display data degrade to an explicit unavailable/incompatible-data label rather than crashing or silently relabeling content.

## Component and data boundaries

- `App`/page shell: semantic landmarks, local-only scope notice, human-authority language, and responsive layout.
- `AnalysisController`: request lifecycle, abort/duplicate-submit protection, minimal response guard, and state selection. It calls only the relative bodyless POST operation.
- Contract adapter: imports generated OpenAPI types and converts the transport union into small view models without changing field meaning or inventing defaults.
- `SourceSummary` and `ObservedFacts`: source identities/counts and fact rows, using human-readable labels while retaining exact values as plain text.
- `RuleResults`: all five rule executions, parameters/formula, signals, rule-level missing evidence, and limitations. Deterministic content is presented before model content.
- `GeminiSummary`: success or typed fallback status, candidate-only wording, findings, missing evidence, limitations, and sanitized metadata.
- `EvidenceExplorer`: a response-local map keyed by exact evidence ID. DOM targets use application-generated safe indexes, not raw evidence strings as selectors or HTML. Missing/duplicate evidence IDs produce a visible data-integrity warning.
- Shared primitives: status callout, disclosure, definition list/table/card as appropriate, evidence-reference button/link, and visually hidden live-region text. Components receive typed props and do not fetch independently.

Keep state local to this page. No router, global state library, persistence, analytics, service worker, data cache, file/URL input, or model client is required.

## Safe rendering and trust boundary

- Treat every API string—including source paths, fact values, codes, messages, evidence summaries, model text, and provider-status text—as untrusted plain text.
- Use React text interpolation only. Do not use `dangerouslySetInnerHTML`, direct `innerHTML`, HTML/Markdown execution, dynamic script/style injection, or untrusted values as URLs, CSS selectors, DOM IDs, or event-handler source.
- Do not create clickable links from returned values. Evidence navigation is internal application state resolved only against the current response's `evidence_index`.
- Parse the fetch response as `unknown`; check HTTP/content type and the minimal top-level object/array plus `gemini.status`/error discriminants before adapting it. Generated TypeScript types provide compile-time alignment but do not make network data trusted.
- Never log or display raw response bodies, stack traces, provider exceptions, credentials, environment values, or private Google Cloud configuration.
- Keep all processing in browser memory. Reloading clears the report; no local/session storage, IndexedDB, cookie, download/export, clipboard, or mutation action is added.

## Accessibility and responsive behavior

- Use native buttons, links only for genuine navigation, semantic landmarks/headings/lists/tables, associated labels, and logical source/focus order.
- Provide visible `:focus-visible` treatment, keyboard activation for every control, a skip link, and focus restoration for evidence navigation.
- Announce request status through a restrained `aria-live` region; do not repeatedly announce the full report. Loading indicators have a text equivalent.
- Meet WCAG 2.2 AA contrast targets for normal/large text and meaningful non-text UI states. Color is never the only status distinction.
- Support common narrow/mobile and desktop widths without horizontal page scrolling. Dense facts may wrap; any genuinely tabular region gets a labeled local overflow container.
- Honor `prefers-reduced-motion: reduce`; no animation is required for comprehension and focus/scroll behavior remains usable with motion reduced.
- Tests use role/name queries, keyboard interaction, focus assertions, representative mobile/desktop viewports, reduced-motion emulation, and an automated accessibility scan for the primary states.

## In scope

- Reconcile project/architecture/ADR/frontend standards and operational configuration to enable the approved frontend stack.
- Implement the one-page local dashboard and fixed Vite `/api` proxy.
- Generate contract-derived TypeScript types and keep them current with OpenAPI.
- Cover idle, loading, model-success, every typed model-fallback status, typed deterministic-pipeline failure, incompatible/network failure, retry, and evidence navigation.
- Add unit/component/browser tests using contract-shaped synthetic fixtures; add one credential-free local proxy/backend smoke path.
- Update root and frontend local setup documentation.

## Out of scope

- Backend or OpenAPI behavior changes, new endpoints/fields, request bodies, arbitrary paths/uploads/URLs, direct Vertex AI access, database, persistence, authentication, RBAC, analytics, cloud/shared deployment, CORS enablement, real PHI, or production operation.
- Changing deterministic rules, Gemini authority, evidence semantics, one-call/no-tools behavior, or synthetic source data.
- Strict FHIR/CARIN conformance, healthcare-validity claims, or fraud/payment/coverage/coding/medical-necessity/diagnostic/clinical decisions.
- Starting frontend implementation before lifecycle gates and the human-started Gemini handoff are complete.

## Architecture impact

- `frontend=true`: a new active React/Vite component is implemented under `frontend/`.
- `testing=true`: implementation and independent browser/contract/accessibility tests are required.
- `infrastructure=true`: CI must provision Node.js 24, use `npm ci`, and install the lock-matched Playwright Chromium runtime before repository verification. This does not add deployment infrastructure.
- `database=false`, `backend=false`: the fixed in-memory backend is consumed unchanged.
- `contract_change=false`: `contracts/openapi.yaml` already defines all required success/fallback/error data. FRONTEND-001 generates types from and validates that unchanged interface.

## Contract and configuration impact

- The only operation is bodyless `POST /api/v1/analyze-demo` from `contracts/openapi.yaml`.
- Commit generated types at `frontend/src/api/generated/schema.d.ts` and provide deterministic `generate:api` and `check:api` scripts. `check:api` must fail when regeneration changes the committed file.
- The stale statement in `contracts/README.md` that calls OpenAPI an empty placeholder is documentation hygiene for the orchestrator/contract-validation step; it does not require or authorize an interface change.
- Pin the Node major line to 24 in repository/frontend tooling, declare a compatible Node engine, commit npm's lockfile, and prohibit alternate package-manager lockfiles.
- Browser code has no API-origin or provider environment variable. Vite binds locally and its `/api` proxy target is the source-controlled exact origin `http://127.0.0.1:8000`.

## Verification expectations

From `frontend/` on Node.js 24:

1. `npm ci`
2. `npm run check:api`
3. `npm run lint`
4. `npm run typecheck`
5. `npm run test:unit`
6. `npm run build`
7. `npm run test:e2e`
8. `npm audit --audit-level=high`

CI must install Node.js 24 explicitly and run `npx playwright install --with-deps chromium` after `npm ci` and before browser tests. Required checks fail rather than skip when Node, Chromium, the audit service, or another required tool is unavailable. Browser fixtures must conform to generated types and use no live credentials; the real-proxy smoke starts FastAPI with Vertex AI explicitly disabled and asserts the rendered deterministic-only result. Repository verification continues to run backend tests, agentic tests, OpenAPI validation, secret/safety checks, and the Python dependency audit.

Independent testing must cover safe text rendering with instruction/HTML-like strings, all Gemini statuses, all deterministic pipeline error codes at least at the adapter/component layer, unexpected transport data, retry/no-concurrent-submit behavior, exact evidence resolution and focus return, source/fact/rule/model separation, accessibility-critical behavior, representative responsive widths, reduced motion, the fixed proxy path/target, generated-type freshness, and build reproducibility.

## Dependencies and handoff

- `HARDEN-001` must be `DONE`; `DEMO-001` supplies the implemented backend and authoritative OpenAPI contract.
- Database and cancelled `DATA-001` compatibility work are not dependencies.
- The orchestrator must update `.ai/project.json`, CI Node/Playwright setup, and the stale contracts README within its permission boundary before implementation/verification gates require them.
- Gemini reads `AGENTS.md`, `GEMINI.md`, this feature, `architecture-report.json`, `docs/architecture/SYSTEM.md`, ADR-0005, `docs/standards/FRONTEND.md`, and `contracts/openapi.yaml`; it must not edit contracts/backend/task state.
- The human manually starts Gemini only after the task reaches `IMPLEMENTATION` and the orchestrator prepares the frontend worktree. Gemini records commands/evidence in `frontend-report.json` and runs `scope check FRONTEND-001 frontend` before completion.

## Acceptance criteria

1. Project/architecture source of truth enables Node.js 24 LTS + React + strict TypeScript + Vite with npm/package-lock and the fixed local same-origin proxy, while database/auth/deployment stay disabled.
2. The browser invokes only the approved bodyless relative `POST /api/v1/analyze-demo`; generated TypeScript types are reproducible from unchanged OpenAPI and freshness is verified.
3. A reviewer can trigger analysis and clearly distinguish source metadata, observed facts, all five rule results/signals, evidence, Gemini candidate findings/status, missing evidence, limitations, and sanitized metadata.
4. Idle/loading, successful Gemini, all five model-fallback statuses, deterministic-pipeline failure, client/incompatible-response failure, retry, abort, and duplicate-submit prevention behave as specified.
5. Every displayed finding/signal reference resolves through the current evidence index with keyboard-operable focus navigation/return; unresolved or duplicate evidence degrades visibly and never crashes.
6. Untrusted API values remain inert plain text and create no HTML/Markdown/URL/style/script execution, secret/config disclosure, arbitrary target, storage, download, model tool, persistence, or mutation surface.
7. The primary flow has semantic structure, keyboard support, visible focus, readable AA contrast, restrained live announcements, responsive layouts, and reduced-motion behavior.
8. Vitest/Testing Library and Playwright deterministically cover the specified states, contract generation, safe rendering, evidence navigation, accessibility-critical behavior, responsive views, fixed proxy integration, and credential-free operation.
9. Node/npm/Chromium CI setup and required frontend verification/security checks are operational and fail closed; existing backend/security verification remains passing.
10. Local documentation explains starting FastAPI and Vite together without database, authentication, shared deployment, production, compliance, or healthcare-validity claims.
11. Gemini implementation begins only after `IMPLEMENTATION`, an orchestrator-created frontend worktree, and explicit human startup.
