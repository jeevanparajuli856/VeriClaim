# Local Vertex AI connectivity boundary

## Confirmed readiness

The sponsor confirms local Google Cloud Application Default Credentials, Google Cloud/Vertex/model configuration, timeout/output-token limits, and a successful direct Gemini smoke test. Actual values and credentials remain outside Git.

This proves connectivity only. It does not prove model quality, anomaly-detection authority, healthcare correctness, CARIN conformance, compliance, production readiness, production-data handling, or deployment approval.

## Active SDK/configuration boundary

The one-day demo uses the Google Gen AI SDK configured for Vertex AI. Source-controlled variable-name placeholders are:

- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_GENAI_USE_VERTEXAI`
- `VERTEX_GEMINI_MODEL`

The request timeout (30 seconds) and maximum model output (2,048 tokens) are fixed source-controlled
DEMO-001 constants. They are not environment variables.

The application makes at most one model call per analysis and exposes no tools. It sends only minimized structured facts/signals from the approved synthetic dataset, requests structured output, validates it with Pydantic, and verifies every evidence reference. Failures return deterministic results with a typed model status; no second repair call or silent provider fallback is allowed.

Do not copy project IDs, credentials, tokens, private environment values, raw unnecessary FHIR, or raw provider errors into source-controlled docs/reports/fixtures, API responses, prompts beyond the minimized payload, or logs.

## Explicitly outside the milestone

Google ADK, Agent Platform Runtime, MCP/A2A, agent memory, tool calling, embeddings/reranking/RAG, Cloud Run/GKE/general cloud deployment, external telemetry carrying healthcare-shaped content, production credentials/data, and autonomous or consequential actions.
