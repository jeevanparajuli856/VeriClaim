# Backend

The active application component is a local Python/FastAPI/Pydantic demo with direct Google Gen AI SDK integration configured for Vertex AI.

DEMO-001 implements the runnable application in `backend/app/`. It loads the fixed read-only synthetic FHIR JSON input, extracts the supported Patient/Coverage/EOB subset, runs five deterministic rules, makes at most one structured Gemini call, preserves deterministic output on model failure, and exposes the flow through FastAPI `/docs`.

Install `backend/requirements.txt` and run `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --env-file .env` from the repository root. See the root README for the complete setup, rule definitions, response shape, tests, and limitations.

No database, separate frontend, authentication/RBAC, RAG, agent framework, or cloud deployment is active.
