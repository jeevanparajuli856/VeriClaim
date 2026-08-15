# ADR-0004 — Vertex AI Gemini development provider

## Status

Accepted during project inception on 2026-08-14.

## Context

The bounded agent-development workflow requires an initial LLM provider so provider, privacy, credential, failure, cost, and reproducibility boundaries are explicit. Initial development uses synthetic healthcare-shaped data only. Credentials are not yet available and will be configured later when model-backed work begins.

## Decision

Use Google Cloud Vertex AI Gemini as the initial provider for agent-development LLM calls.

The integration must use a provider adapter and may send only the minimum approved synthetic context required for the current task. Before the first external call, the tracked task must pin or record the Google Cloud project, region, exact model identifier/version, quota and cost limits, applicable retention/training/data-use settings, timeouts, and failure behavior. Credentials must be supplied through approved local environment configuration or Application Default Credentials and must never be committed, embedded in code/prompts/datasets, exposed to the frontend, or written to traces.

This decision does not approve:

- real PHI, production claims, or production healthcare-system data;
- general Google Cloud hosting for the application, database, identity, storage, or telemetry;
- arbitrary model or region substitution during a controlled experiment;
- an embedding or reranking provider that has not been selected by the relevant task; or
- autonomous external side effects or unrestricted network tools.

If credentials or approved configuration are absent, model-backed execution must remain disabled or fail closed; foundation, data design, and other provider-independent work may continue.

## Alternatives considered

- **Leave the initial LLM provider unknown:** rejected because it would leave a material platform and trust-boundary blocker unresolved.
- **Store an API key or service-account credential in repository configuration:** rejected because secrets must remain outside Git and least privilege is required.
- **Treat Vertex AI selection as approval for all Google Cloud services:** rejected because each hosted data, identity, telemetry, and deployment boundary has separate security, privacy, residency, and cost implications.
- **Allow silent provider fallback:** rejected because it undermines reproducibility and can change data-use and security terms.

## Consequences

### Positive

- Gives agent-development tasks a concrete provider boundary while preserving adapter-based isolation.
- Allows provider-independent inception and foundation work to proceed before credentials exist.
- Makes model version, region, quota, cost, and data-use controls explicit verification evidence.

### Negative

- Model-backed work depends on later human configuration of a Google Cloud project, access, region, and credentials.
- Provider/model changes may affect behavior, availability, latency, cost, and experiment comparability.

### Security and privacy implications

- The application-to-Vertex boundary is external and untrusted; outbound context must be minimized, classified, and auditable.
- Synthetic-only approval does not relax the prohibition on PHI or production claims.
- Credentials require least privilege, secret isolation, rotation/revocation, and redaction from errors and telemetry.
- Provider terms and settings must be reviewed before first use; unsafe configuration, unavailable credentials, or provider errors fail closed.

### Operational implications

- Exact runtime configuration is deferred until a task needs model access and must remain outside committed files.
- Every controlled run records model/configuration identifiers, token use, latency, failures, and estimated cost.
- Final per-case and experiment ceilings are set after FOUNDATION-001 measures baselines and before autonomous tool loops are enabled.
