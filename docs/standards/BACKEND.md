# Backend standards — active one-day demo

- Use Python, FastAPI, Pydantic, and the Google Gen AI SDK configured for Vertex AI.
- Keep `POST /api/v1/analyze-demo` transport handling thin; put loading, extraction, deterministic rules, model integration, and response assembly in focused modules.
- Validate every external/file/model boundary with explicit Pydantic or bounded parser rules.
- Read only the allowlisted synthetic files under `dataset/`; never modify them or accept arbitrary paths/URLs/uploads.
- Keep deterministic extraction and rule logic pure where practical and independently testable.
- Make at most one model call per analysis; expose no tools or agent loop.
- Treat model output as untrusted. Validate schema and every evidence reference before including candidate findings.
- Preserve deterministic results when the model is unavailable or invalid.
- Do not leak credentials, private configuration, raw provider errors, or unnecessary patient attributes.
- Add focused unit and integration tests for behavior changes.
- Do not silently diverge from the approved API contract created during DEMO-001.
- Authentication/authorization is not an active component for this local synthetic-only demo. Any shared/network deployment requires a new approved security design.
