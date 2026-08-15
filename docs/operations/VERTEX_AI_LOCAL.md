# Local Vertex AI connectivity boundary

## Confirmed readiness

The sponsor confirms the following local-development facts as of 2026-08-14:

- Vertex AI Gemini is the approved external LLM provider for bounded agent-development evidence analysis/reasoning.
- Google Cloud Application Default Credentials provide local authentication.
- The local uncommitted environment contains non-empty Google Cloud, Vertex AI, model, timeout, output-token, tool-call, workflow-duration, and cost-limit configuration.
- A direct Gemini request through Vertex AI completed successfully.
- Runtime values and credentials remain outside Git.

This confirms local Vertex AI model connectivity only. It is not verification or approval of an application deployment, production readiness, production credentials, production data/PHI handling, model quality, anomaly-detection authority, autonomous claim action, or another Google Cloud service.

## Committed variable-name contract

`.env.example` contains placeholders only; its Vertex/workflow-specific names are:

- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_GENAI_USE_VERTEXAI`
- `VERTEX_GEMINI_MODEL`
- `VERTEX_GEMINI_TIMEOUT_SECONDS`
- `VERTEX_GEMINI_MAX_OUTPUT_TOKENS`
- `AGENT_MAX_TOOL_CALLS`
- `AGENT_MAX_TOTAL_SECONDS`
- `AGENT_MAX_COST_USD`

Actual values must remain in the ignored local `.env` or the external ADC/configuration stores. Do not copy project IDs, credentials, tokens, or private runtime values into source-controlled documentation, task reports, traces, prompts, datasets, browser code, or logs.

## Data and telemetry boundary

- Only approved synthetic/public development context may be sent to Vertex AI Gemini.
- Minimize outbound context and treat Gemini output as untrusted candidate findings/explanations.
- Do not send PHI, production claims, production credentials, secrets, or unnecessary identifiers.
- Keep telemetry local by default. Do not export prompts, FHIR data, model output, credentials, or private runtime configuration.
- Disable or fail closed when ADC, required settings, limits, provider access, schema validation, evidence checks, or governance checks fail.

## Explicitly unselected or unapproved

- project-owned state-machine implementation;
- direct Google Gen AI SDK integration;
- Google ADK;
- Gemini Enterprise Agent Platform Runtime deployment;
- Cloud Run, GKE, or general Google Cloud application hosting;
- embedding or reranking providers without separate approval;
- write-capable claim-system tools; and
- autonomous claim decisions.

The orchestration/integration choice remains a task-level architecture decision. Any future production or managed deployment requires a separate approved architecture, security, privacy, IAM, data, cost, and operations review.
