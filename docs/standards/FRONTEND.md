# Frontend standards

## Active component baseline

The active frontend is a local single-page dashboard built with Node.js 24 LTS, React, strict TypeScript, and Vite. Use npm only, commit `package-lock.json`, install with `npm ci`, and keep a compatible Node engine/toolchain declaration. Do not add another package-manager lockfile.

This is a browser presentation component over the existing FastAPI API. It has no database, server-side rendering, authentication, provider SDK, deployment target, analytics, or persistent browser state.

## Contract and transport

- `contracts/openapi.yaml` is authoritative. Generate and commit TypeScript types; never hand-maintain a competing response interface or invent endpoints/fields.
- Provide `generate:api` and `check:api` scripts. Contract freshness must be deterministic and fail verification when regeneration changes committed output.
- Fetch only the relative bodyless `POST /api/v1/analyze-demo` path. Browser code must not accept, derive, or expose another API origin.
- Vite development configuration may proxy only `/api` to the exact source-controlled local origin `http://127.0.0.1:8000`. Bind development serving locally. Do not add backend CORS to support this component.
- Parse network data as `unknown` and apply minimal transport/discriminant checks before using generated types. On non-JSON, unexpected status/schema, or network failure, show a bounded generic client error rather than raw response/exception content.

## State and component ownership

- One analysis controller owns `idle`, `loading`, completed analysis, typed pipeline error, and client error states.
- Use one `AbortController` per request, cancel on teardown/replacement, and prevent concurrent submissions.
- Fetch at the page/controller boundary. Presentational components receive typed props and do not initiate network activity.
- Keep source metadata/facts, deterministic rule results/signals, Gemini candidate output, evidence, missing evidence, limitations, and model metadata in separate components and semantic sections.
- Always show all five rule results. A completed rule with zero signals is not proof of no anomaly.
- Keep deterministic content ahead of and visually stronger than Gemini candidate text. Preserve the human-authority and local-synthetic-demo wording.
- Keep state in memory. Do not add a router, global state library, local/session storage, IndexedDB, cookies, service worker, cache, upload, export, clipboard, or mutation behavior without new architecture.

## Evidence navigation

- Resolve signal/finding references only against the current response's `evidence_index` using exact string equality.
- Use safe application-generated DOM target IDs/indexes; never interpolate returned evidence values into selectors, HTML, URLs, styles, or executable contexts.
- Evidence controls must be keyboard operable, move focus to the selected record heading, expose its summary/source references, and provide focus return to the invoking control.
- Missing or duplicate evidence records produce a visible data-integrity warning and remain inert; they must not crash the page or silently point elsewhere.

## Safe rendering

- All backend/FHIR/model values are untrusted plain text. React text interpolation is the only allowed rich-data rendering path.
- Do not use `dangerouslySetInnerHTML`, `innerHTML`, runtime HTML/Markdown evaluation, dynamic script/style injection, or returned text as a clickable URL.
- Do not log/display raw bodies, provider errors, stack traces, credentials, project/location/model environment values, or private configuration.
- Avoid third-party runtime content, fonts, scripts, trackers, and CDNs. Prefer small local CSS and system fonts for the prototype.
- Unknown enum/status values and malformed display data become explicit unavailable/incompatible-data states, never guessed semantics.

## Accessibility and interaction

- Prefer native semantic HTML and accessible names; use ARIA only to fill a native semantic gap.
- Provide header/main/footer landmarks, a skip link, hierarchical headings, logical focus order, keyboard operation, and persistent visible `:focus-visible` styling.
- Announce concise request status in `aria-live`; use `aria-busy` while loading and do not announce the full result repeatedly.
- Meet WCAG 2.2 AA contrast targets and never rely on color alone.
- Support narrow/mobile and desktop widths without page-level horizontal scrolling. Wrap dense values; label any local overflow region used for a real data table.
- Respect `prefers-reduced-motion`; motion is optional and never necessary to understand state or navigation.

## Testing and verification

Use Vitest and Testing Library for controller, adapter, component, keyboard, focus, safe-rendering, and state tests. Use Playwright Chromium for the assembled browser flow, representative desktop/mobile widths, reduced-motion behavior, evidence navigation, an automated accessibility scan, all response classes, retry, and one real fixed-proxy smoke path. Model/provider calls must be faked or explicitly disabled; tests never require live credentials.

Required frontend scripts are:

- `npm run check:api`
- `npm run lint`
- `npm run typecheck`
- `npm run test:unit`
- `npm run build`
- `npm run test:e2e`

CI and local acceptance use Node.js 24 and `npm ci`; Playwright's lock-matched Chromium is installed explicitly. `npm audit --audit-level=high` is required and must fail closed on high/critical advisories or audit unavailability. Passing component tests does not replace independent task testing, repository verification, security review, or final review.
