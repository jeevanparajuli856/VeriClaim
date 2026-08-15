# Backend

The active application component is a local Python/FastAPI/Pydantic demo with direct Google Gen AI SDK integration configured for Vertex AI.

DEMO-001 will add the runnable implementation here. It must load the fixed read-only synthetic FHIR JSON input, extract the supported Patient/Coverage/EOB subset, run five deterministic rules, make at most one structured Gemini call, preserve deterministic output on model failure, and expose the flow through FastAPI `/docs`.

No database, separate frontend, authentication/RBAC, RAG, agent framework, or cloud deployment is active.
