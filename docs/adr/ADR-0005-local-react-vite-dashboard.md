# ADR-0005 — Local React and Vite dashboard

## Status

Accepted on 2026-08-15 for FRONTEND-001.

## Context

The completed FastAPI demonstration exposes a single bodyless analysis operation and previously used `/docs` as its only interface. The approved final local-prototype task needs a polished, accessible visual flow that helps a resume reviewer distinguish deterministic evidence from non-authoritative Gemini candidate explanations.

The project previously disabled its separate frontend after superseding a production-scale Next.js direction. Re-enabling a frontend, selecting its stack, and defining its browser/backend trust boundary are project-wide decisions. The dashboard must remain small, local, read-only, contract-driven, and compatible with the existing FastAPI behavior without adding CORS, credentials to the browser, persistence, identity, or deployment.

## Decision

Enable a separate frontend at `frontend/` using:

- Node.js 24 LTS;
- React with strict TypeScript;
- Vite for development and build;
- npm with a committed `package-lock.json` and `npm ci` installation;
- generated TypeScript types from the authoritative `contracts/openapi.yaml`;
- Vitest and Testing Library for unit/component coverage; and
- Playwright Chromium for browser coverage.

The browser always sends a bodyless POST to the relative same-origin path `/api/v1/analyze-demo`. During the approved local demonstration, Vite binds locally and proxies only `/api` to the exact allowlisted FastAPI origin `http://127.0.0.1:8000`. The API origin is source-controlled, not user/query/runtime configurable, and no provider or Google Cloud configuration enters the frontend.

The result is an in-memory single page. It keeps source/fact/rule/signal evidence, Gemini candidate content, missing evidence, limitations, and sanitized metadata distinct. All returned values are untrusted plain text, evidence navigation resolves only within the current response, and no browser persistence or mutation surface is added.

CI must explicitly provision Node.js 24, install with `npm ci`, install the Playwright Chromium runtime, and execute contract freshness, lint, typecheck, unit, build, browser, and npm audit checks. This CI/tooling impact does not select a hosting or deployment platform.

## Alternatives considered

- **Keep FastAPI `/docs` only:** remains useful for API inspection but does not satisfy the approved accessible visual investigation flow.
- **Restore the historical Next.js direction:** adds server/runtime, routing, and deployment concepts that are unnecessary for one local read-only page.
- **Call FastAPI directly from a different browser origin:** would require backend CORS/configuration changes and broaden the integration/security surface.
- **Serve compiled assets from FastAPI:** couples backend packaging and routes to the UI and is unnecessary for the local development demonstration.
- **Handwritten TypeScript response interfaces:** can silently drift from OpenAPI and duplicates the authoritative contract.
- **A configurable proxy/API URL:** expands the browser's network target surface and is not needed for the fixed local demo.

## Consequences

### Positive

- A small, familiar component model supports an accessible polished dashboard within the prototype scope.
- Same-origin relative calls avoid a backend/CORS change and keep provider credentials server-side.
- Generated types and lockfile-based installation make API and dependency drift visible.
- Unit/component and real-browser layers cover state, evidence navigation, accessibility, and proxy integration without live model credentials.

### Negative

- The repository gains a Node/npm dependency graph, generated contract artifact, frontend build, browser runtime download, and additional CI duration.
- Vite's proxy is a development-only integration; a future deployed frontend would need a separately approved serving/reverse-proxy, identity, and security design.
- Compile-time generated types do not validate untrusted network data at runtime, so the controller still needs bounded transport/discriminant checks and safe failure behavior.

### Security implications

- Returned FHIR-derived and Gemini text remains untrusted and must never be executed as HTML, Markdown, URL, selector, script, or style.
- The browser receives no ADC, token, project/location/model configuration, arbitrary URL/file input, provider client, raw provider error, or model tool capability.
- The fixed local proxy must not be generalized to remote/user-selected targets. Shared/network deployment remains unapproved and would require authentication, authorization, abuse controls, and a new architecture/security review.
- npm dependencies and the lockfile add supply-chain risk; lockfile integrity, required audit, secret scanning, security review, and exact CI toolchain setup mitigate but do not eliminate it.

### Operational implications

- Developers run FastAPI on `127.0.0.1:8000` and Vite locally, then open the Vite origin.
- Node.js 24 and the npm lockfile are the supported frontend toolchain boundary.
- CI/workstation browser tests must install the Playwright Chromium version matched to the locked Playwright package.
- `npm run build` is verification evidence only. No hosting, CDN, container, cloud resource, or production runtime is selected.
