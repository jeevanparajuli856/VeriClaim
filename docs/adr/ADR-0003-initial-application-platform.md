# ADR-0003 — Initial application platform

## Status

Accepted during project inception on 2026-08-14.

## Context

VeriClaim needs a concrete development platform before deterministic task creation can begin. The first milestone is a local, synthetic-only research vertical slice with FHIR processing, transparent risk analysis, policy retrieval, bounded agent workflows, governance, traceability, and human review. The platform should support those concerns without introducing premature distributed-system or managed-cloud complexity.

## Decision

Use the following initial platform:

- a Python modular-monolith backend using FastAPI and Pydantic;
- a TypeScript/Next.js analyst frontend targeting WCAG 2.2 AA;
- local PostgreSQL with pgvector and native full-text search;
- Git-tracked database migrations under `database/migrations/`;
- local Docker-based development;
- standards-based OIDC, a local/test identity provider for development, deny-by-default RBAC, and server-side/object-level authorization;
- a deterministic workflow/state machine with a coordinator and bounded typed specialist tools behind a common experiment interface;
- OpenTelemetry-compatible identifiers and local-only telemetry by default; and
- deterministic/statistical and interpretable scikit-learn risk baselines before more complex models.

Keep the backend, workflow, and frontend in one initial deployment boundary unless a later threat, isolation, or scale requirement justifies separation. Managed database hosting and a hosted application cloud are not selected. Detailed contracts, package choices, migration tooling, identity provider, schemas, and component verification commands belong to later tracked tasks and must not be inferred from this ADR.

## Alternatives considered

- **Leave all technologies unresolved:** rejected because it would prevent truthful `INCEPTION_READY` operational configuration and block the first task.
- **Start with microservices or independently deployed agents:** rejected because it adds distributed-system and trust-boundary complexity before measured isolation or scaling needs exist.
- **Use a dedicated vector database immediately:** rejected because PostgreSQL full-text search plus pgvector supports the initial hybrid-retrieval research surface with fewer operational components.
- **Select a managed cloud stack during inception:** rejected because hosted application, database, identity, residency, and operating requirements are not yet established.

## Consequences

### Positive

- Establishes concrete component and migration boundaries for task planning.
- Keeps local development reproducible and limits early credentials and cloud cost.
- Supports healthcare parsing, ML research, typed APIs, human review, hybrid retrieval, and audit relationships in a cohesive platform.

### Negative

- Local development will not establish production availability, isolation, backup, residency, or managed-service behavior.
- The modular monolith may later need internal or deployment-boundary changes if evidence demonstrates different scaling or isolation requirements.

### Security implications

- Authentication and authorization remain server-side and deny by default.
- Database, workflow, retrieval, and provider access require separate least-privilege credentials.
- Local Docker, dependency, browser, ingestion, retrieval, agent-tool, and database boundaries require explicit threat tests in later tasks.

### Operational implications

- `.ai/project.json` enables backend, frontend, and database with the selected technologies and migration path.
- PLATFORM-001 must create runnable manifests and then add required project-specific verification and security commands to `.ai/project.json`.
- Any managed database, hosted identity, external telemetry, or hosted application deployment requires a later approved decision.
