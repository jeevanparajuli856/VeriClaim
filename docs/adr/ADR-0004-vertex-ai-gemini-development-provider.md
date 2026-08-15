# ADR-0004 — Vertex AI Gemini development provider

## Status

Accepted during project inception on 2026-08-14.

## Context

The bounded agent-development workflow requires an initial LLM provider so provider, privacy, credential, failure, cost, and reproducibility boundaries are explicit. Initial development uses synthetic/public healthcare-shaped data only. The sponsor confirms that local Google Cloud Application Default Credentials, required Vertex/model configuration, and timeout/token/tool/workflow/cost limits are present outside Git and that a direct Gemini request through Vertex AI succeeded.

## Decision

Use Google Cloud Vertex AI Gemini as the initial provider for agent-development LLM calls.

The integration must preserve a provider boundary and may send only the minimum approved synthetic/public context required for the current task. Local authentication uses Application Default Credentials. Required runtime names and bounded limits are present and non-empty, but their values remain private and outside Git. Source-controlled documentation, examples, traces, and reports must not record the Google Cloud project ID, credentials, tokens, or private environment values.

The successful direct request confirms local Vertex AI model connectivity only. Before model-backed work expands beyond connectivity testing, task architecture and verification must define sanitized model/version change control, applicable retention/training/data-use evidence, quota/cost enforcement, timeouts, failure behavior, and reproducibility evidence without committing private configuration.

This decision does not approve:

- real PHI, production claims, or production healthcare-system data;
- general Google Cloud hosting for the application, database, identity, storage, or telemetry;
- arbitrary model or region substitution during a controlled experiment;
- an embedding or reranking provider that has not been selected by the relevant task;
- autonomous external side effects or unrestricted network tools;
- Gemini Enterprise Agent Platform Runtime deployment, Google ADK selection, direct Google Gen AI SDK selection, Cloud Run, GKE, or general Google Cloud application hosting; or
- external telemetry containing prompts, FHIR data, model output, credentials, or private runtime configuration.

If local authentication or required bounded configuration becomes absent or invalid, model-backed execution must remain disabled or fail closed; foundation, data design, and other provider-independent work may continue.

## Alternatives considered

- **Leave the initial LLM provider unknown:** rejected because it would leave a material platform and trust-boundary blocker unresolved.
- **Store an API key or service-account credential in repository configuration:** rejected because secrets must remain outside Git and least privilege is required.
- **Treat Vertex AI selection as approval for all Google Cloud services:** rejected because each hosted data, identity, telemetry, and deployment boundary has separate security, privacy, residency, and cost implications.
- **Allow silent provider fallback:** rejected because it undermines reproducibility and can change data-use and security terms.

## Consequences

### Positive

- Gives agent-development tasks a concrete provider boundary while preserving provider isolation.
- Confirms local connectivity without representing it as application deployment or production readiness.
- Makes model version, region, quota, cost, and data-use controls explicit verification evidence.

### Negative

- Model-backed work depends on maintaining valid local ADC, private configuration, limits, and provider access outside Git.
- Provider/model changes may affect behavior, availability, latency, cost, and experiment comparability.

### Security and privacy implications

- The application-to-Vertex boundary is external and untrusted; outbound context must be minimized, classified, and auditable.
- The synthetic/public-only approval does not relax the prohibition on PHI or production claims.
- Credentials require least privilege, secret isolation, rotation/revocation, and redaction from errors and telemetry.
- Provider terms/settings evidence must be reviewed before development expands beyond connectivity smoke testing; unsafe configuration, unavailable credentials, or provider errors fail closed.

### Operational implications

- Local runtime configuration and limits are present and connectivity is smoke-tested; values remain outside committed files and must never be copied into task reports or documentation.
- The orchestration/integration implementation remains task-level; this ADR does not select a project-owned state machine, direct Google Gen AI SDK integration, Google ADK, or managed Agent Platform runtime.
- Every controlled run records sanitized, non-secret model/version evidence, token use, latency, failures, and estimated cost without copying private environment values.
- Final per-case and experiment ceilings are set after FOUNDATION-001 measures baselines and before autonomous tool loops are enabled.
