# FRONTEND-001 — Build the local investigation dashboard prototype

## Goal

Create a polished, accessible local dashboard prototype that lets a resume reviewer run the existing fixed-dataset analysis and understand observed facts, deterministic signals, evidence, Gemini status/findings, missing evidence, and limitations without using FastAPI `/docs` directly.

## In scope

- Reconcile the project, architecture, ADR, frontend standard, and `.ai/project.json` before implementation so the separate frontend becomes an explicitly enabled component with an approved technology.
- Build one local prototype flow over the existing `POST /api/v1/analyze-demo` contract.
- Present loading, successful model summary, deterministic-only/model-failure, deterministic-pipeline error, and retry states.
- Keep observed facts, deterministic signals, Gemini candidate findings, evidence references, missing evidence, limitations, and sanitized metadata visually distinct.
- Provide evidence-reference navigation or expansion so a reviewer can connect every displayed signal/finding to returned evidence.
- Preserve keyboard operation, visible focus, semantic structure, responsive layout, readable contrast, and reduced-motion support.
- Add focused frontend unit/component and browser-facing integration tests using synthetic/fake responses; no live Vertex AI credentials are required.
- Update local setup documentation for running the API and UI together.

## Out of scope

- New backend analysis behavior, endpoints, arbitrary paths/uploads, database, persistence, authentication, RBAC, cloud deployment, real PHI, production operation, or consequential claim actions.
- Changing deterministic rules, Gemini authority, evidence semantics, or the one-call/no-tools boundary.
- Strict FHIR/CARIN conformance, healthcare-validity claims, or expanding beyond the approved synthetic dataset.
- Starting frontend implementation before the technology/component decision, task architecture, contract validation, and human-started Gemini handoff are complete.

## Architecture impact

- Frontend impact is expected and testing is required.
- The project currently disables the frontend and does not name an active frontend technology. Task planning must recommend and obtain approval for the technology, local frontend/backend integration pattern, verification commands, and replacement/amendment of the superseded frontend decision before implementation.
- Database impact is expected to remain false. Any backend, infrastructure, or contract impact must be evidenced by the task architect rather than inferred here.

## Contract impact

- The frontend must consume `contracts/openapi.yaml` and must not invent endpoints or fields.
- No API change is currently requested. If browser integration requires a backend or contract change, stop and reconcile the feature, architecture, permissions, and contract before implementation.

## Security considerations

- Render FHIR-derived and Gemini text as untrusted plain text; never use unsafe HTML execution.
- Keep credentials, Google Cloud configuration, and provider access in the backend only.
- Do not expose arbitrary URL/file input, model tools, raw provider errors, or environment values.
- Preserve local-only demonstration wording and the human-authority boundary throughout the UI.
- A shared/network deployment remains unapproved and would require authentication, authorization, abuse controls, and a new security architecture.

## Dependencies

- `HARDEN-001` must be `DONE` so the UI is built on the merged prompt-isolated, hash-locked, dependency-audited backend.
- `DEMO-001` is already `DONE` and supplies the implemented API and authoritative OpenAPI contract.
- Database and cancelled `DATA-001` compatibility work are not dependencies.

## Acceptance criteria

1. Before implementation, project/architecture source of truth explicitly enables a frontend, records its approved technology and local integration pattern, updates frontend verification commands, and preserves database-disabled/local-synthetic boundaries.
2. The UI invokes only the approved bodyless `POST /api/v1/analyze-demo` operation and remains aligned with generated or contract-derived types where practical.
3. A reviewer can trigger analysis and clearly distinguish sources/observed facts, five deterministic rule results/signals, evidence, Gemini candidate findings/status, missing evidence, limitations, and sanitized metadata.
4. The UI handles loading, success, configuration/provider/timeout/invalid-output/invalid-evidence deterministic fallback, typed deterministic-pipeline failure, and user retry without losing or mislabeling authoritative deterministic content.
5. Every displayed finding/signal retains resolvable evidence references, and candidate model text is visibly non-authoritative and never styled as a fraud, payment, coverage, coding, clinical, diagnostic, or medical-necessity decision.
6. All untrusted API text is rendered safely; no secret, private configuration, raw provider error, arbitrary path/URL, HTML execution, tool invocation, or data mutation surface is added.
7. The primary flow is keyboard accessible, uses semantic landmarks/headings/controls, has visible focus and readable contrast, adapts to common desktop/mobile widths, and respects reduced-motion preferences.
8. Deterministic frontend tests cover rendering and interaction for all response states, evidence navigation, accessibility-critical behavior, contract alignment, and no-live-credential operation.
9. Local documentation explains how to start both components and demonstrates the prototype without database, authentication, or deployment claims.
10. Gemini frontend implementation begins only after the task reaches IMPLEMENTATION, the orchestrator prepares the frontend worktree, and the human manually starts Gemini as required by AGENTS.md.
