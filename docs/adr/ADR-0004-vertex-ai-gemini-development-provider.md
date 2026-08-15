# ADR-0004 — Vertex AI Gemini development provider

## Status

Accepted on 2026-08-14; **amended on 2026-08-15** for the approved one-day demo.

## Context

The demo needs one bounded LLM summarization step after deterministic anomaly analysis. Local Google Cloud Application Default Credentials and external Vertex AI model configuration are already working and smoke-tested. Credentials and real configuration values remain outside Git.

The earlier ADR selected Vertex AI Gemini but deliberately left the integration mechanism open among direct SDK use, a project state machine, Google ADK, and managed Agent Platform options. The scope reset now resolves that choice.

## Decision

Use the **Google Gen AI SDK configured for Vertex AI** for at most one model call per `POST /api/v1/analyze-demo` invocation.

The application sends only minimized structured facts extracted from the approved synthetic Patient/Coverage/EOB input, deterministic signals, stable evidence references, and explicit limitations. It requests structured output owned and validated by Pydantic. Every candidate finding must cite supplied evidence; unknown references invalidate the model portion.

Gemini may explain deterministic signals, correlate supplied synthetic facts, identify missing evidence, produce candidate findings, and state limitations. It must not determine fraud; approve or deny claims; make payment, coverage, coding, medical-necessity, diagnostic, or clinical decisions; modify data; use tools; request unrestricted external data; or receive secrets, real PHI, or production claims.

Provider/configuration/timeout/transport errors, non-JSON output, schema failure, or invalid evidence references do not erase deterministic output and do not trigger a repair or fallback model call. The response records a bounded model status and limitations.

## Configuration and metadata

- Authenticate locally with Application Default Credentials.
- Keep project ID, credentials, tokens, and actual environment values outside Git and out of API responses/logs.
- Source control may document variable names and placeholders only.
- Return or log only sanitized metadata: provider, configured model name, prompt/schema version, invocation status, output validation status, and latency/token counts when the SDK supplies them.
- Use explicit timeouts and output-token limits. Cost/tool-loop budgets from the former agent platform are not required because there is one call and no tools.

## Explicitly not approved

- Google ADK, Gemini Enterprise Agent Platform Runtime, MCP/A2A, agent memory, tool calling, model training, or autonomous loops;
- Cloud Run, GKE, or general application/cloud deployment;
- silent provider/model fallback;
- embeddings, reranking, RAG, external telemetry carrying healthcare-shaped content, or other Google Cloud service selection;
- real PHI, production claims, production credentials, or consequential claim actions.

## Consequences

### Positive

- A direct integration matches the one-day constraint and is easy to demonstrate and fake in tests.
- Structured validation and evidence checks make the model boundary explicit.
- Deterministic fallback keeps the endpoint useful when model access fails.

### Limitations

- Output remains variable and non-authoritative even when schema-valid.
- Local execution depends on working ADC, provider availability, and external configuration.
- The smoke test proves connectivity only, not model quality, healthcare validity, compliance, or production readiness.
