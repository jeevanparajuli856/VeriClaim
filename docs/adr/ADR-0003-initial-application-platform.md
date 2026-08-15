# ADR-0003 — Initial application platform

## Status

**Superseded for the active milestone on 2026-08-15 by the approved project scope reset.** Retained to preserve the earlier decision history.

## Historical decision — 2026-08-14

The original inception selected a production-oriented local research platform: a Python/FastAPI/Pydantic modular monolith, TypeScript/Next.js frontend, PostgreSQL with pgvector and full-text search, Git-tracked migrations, Docker, OIDC/RBAC, bounded agent workflows, OpenTelemetry-compatible tracing, and statistical/ML baselines. That direction was reasonable for the former multi-stage healthcare research-platform goal, but it expanded the work beyond a one-day resume demonstration.

The historical consequences included database and frontend components, migration and identity design, retrieval, audit relationships, managed-service decisions, and later platform/orchestration tasks. These are no longer active requirements or blockers. Existing scaffold files may remain as historical repository artifacts until a scoped cleanup, but `.ai/project.json` is authoritative for active component enablement.

## Replacement decision — 2026-08-15

For the one-day milestone, use only:

- Python, FastAPI, and Pydantic in the `backend/` component;
- Google Gen AI SDK configured for Vertex AI;
- pytest;
- the existing versioned JSON files under `dataset/`;
- in-memory processing; and
- FastAPI `/docs` as the demonstration interface.

The database and separate frontend components are disabled. PostgreSQL, pgvector, Supabase, migrations, Docker as a requirement, OIDC/RBAC, RAG, policy ingestion, multi-agent orchestration, Google ADK, Agent Platform Runtime, MCP/A2A, custom UI, cloud deployment, and production observability/scalability are outside the milestone.

## Rationale

- The entire flow can be implemented, tested, documented, and demonstrated in one focused day.
- The architecture still shows meaningful engineering: narrow FHIR extraction, pure deterministic rules, structured model output, evidence validation, and graceful failure.
- Removing unused infrastructure makes the trust boundary and explanation clearer.

## Consequences

### Positive

- One runnable component and one demonstration interface.
- No persistence or migration risk and no frontend integration dependency.
- Smaller test surface and a clearer resume narrative.

### Limitations

- The demo establishes no production availability, identity, tenancy, audit retention, scalability, compliance, or deployment behavior.
- Local unauthenticated `/docs` is suitable only for the synthetic local demonstration.

### Change control

Adding a database, custom frontend, authentication, deployment, retrieval, agent framework, or production-data boundary requires a later approved architecture decision and must not be inferred from the preserved historical platform.
