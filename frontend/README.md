# VeriClaim Frontend Dashboard

A local, evidence-grounded single-page dashboard built with React 19, TypeScript (strict mode), and Vite.

The dashboard connects to the local FastAPI backend via a same-origin development proxy (`/api` -> `http://127.0.0.1:8000`) and presents deterministic invariant check results, evidence citations, and non-authoritative Gemini candidate findings.

## Local Development

Prerequisites: Node.js 24 LTS and npm.

```bash
cd frontend
npm ci
npm run dev
```

The Vite dev server will start at `http://127.0.0.1:5173`. Ensure the backend is running at `http://127.0.0.1:8000`.

## Scripts

- `npm run dev`: Starts the local Vite development server with `/api` proxy.
- `npm run build`: Typechecks and creates the production distribution bundle.
- `npm run lint`: Runs ESLint across all TypeScript and React files.
- `npm run typecheck`: Runs TypeScript typecheck in strict mode (`tsc --noEmit`).
- `npm run test:unit`: Executes unit and component tests with Vitest and React Testing Library.
- `npm run test:e2e`: Runs Chromium and Mobile Chromium browser tests with Playwright (including axe accessibility audits and real proxy smoke).
- `npm run generate:api`: Generates TypeScript types from `contracts/openapi.yaml` into `src/api/generated/schema.d.ts`.
- `npm run check:api`: Verifies that generated types match the OpenAPI contract.
- `npm run verify`: Runs the full verification pipeline (`check:api`, `lint`, `typecheck`, `test:unit`, `build`, `test:e2e`).
- `npm audit --audit-level=high`: Verifies dependency security.

## Boundary Notes

- Demonstration and research prototype only.
- Does not collect, store, or process real Protected Health Information (PHI).
- Does not make fraud, coverage, payment, coding, clinical, or diagnostic determinations.
