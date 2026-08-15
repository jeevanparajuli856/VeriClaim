# VeriClaim

VeriClaim is a local, evidence-grounded FHIR anomaly investigation demo. It loads three fixed synthetic FHIR R4 JSON files, extracts a deliberately small Patient/Coverage/ExplanationOfBenefit subset, runs five transparent deterministic checks, and optionally asks Vertex AI Gemini for one structured candidate summary. The complete flow is available through FastAPI's built-in `/docs` interface.

This is a demonstration and research prototype. Deterministic signals and model text are review aids, not fraud findings or healthcare decisions.

## What it demonstrates

- allowlisted, read-only local JSON loading with file hashes and bounded structural checks;
- narrow FHIR-shaped extraction with stable RFC 6901-based evidence IDs;
- deterministic, independently tested anomaly signals with explicit formulas and limitations;
- one no-tools Google Gen AI SDK call configured for Vertex AI;
- Pydantic structured-output and evidence-citation validation;
- graceful model failure that never discards the deterministic report; and
- a small FastAPI contract that is easy to run and inspect locally.

## Local setup

Python 3.10 or newer is recommended. From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
cp .env.example .env
```

Set the non-secret Vertex AI identifiers in `.env`. Authentication uses Application Default Credentials; credential files and real values stay outside Git. If model configuration is absent, the API still runs and returns `gemini.status: configuration_error` with all deterministic output.

Start the local server, loading `.env` without committing it:

```bash
.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --env-file .env
```

Open `http://127.0.0.1:8000/docs`, expand `POST /api/v1/analyze-demo`, and select **Execute**. The endpoint has no request body, upload, URL, or path parameter. It always analyzes only:

- `dataset/patient_bbuser29999.json`
- `dataset/coverage_bundle_bbuser29999.json`
- `dataset/eob_bundle_bbuser29999.json`

The same operation can be invoked with:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze-demo
```

### Frontend dashboard

In a separate terminal, start the local React/Vite dashboard:

```bash
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173` to explore the interactive investigation interface. The frontend proxies `/api` directly to `http://127.0.0.1:8000`.

## Architecture

```text
POST /api/v1/analyze-demo
  -> fixed allowlisted loader (1 MiB/file; read-only)
  -> bounded Patient/Coverage/EOB subset extractor
  -> stable observed-fact evidence index
  -> five pure deterministic rules
  -> zero or one Vertex AI Gemini call (no tools)
  -> Pydantic schema + supplied-evidence validation
  -> combined JSON response
```

Everything is processed in memory. The local React single-page frontend communicates with the local FastAPI backend via a same-origin proxy. There is no database, persistence, authentication, arbitrary file upload, RAG layer, agent loop, or cloud deployment component. The route stays thin; loading, extraction, rules, model integration, and response assembly live in separate modules under `backend/app/`.

## Deterministic checks

| Rule | Exact demonstration behavior |
|---|---|
| `REF-001` | A required local `Patient/<id>` or `Coverage/<id>` reference must resolve to exactly one supplied supported resource. Missing, malformed, wrong-type, unresolved, and ambiguous references are separate signals. |
| `DATE-001` | Compares each present `item.servicedDate` inclusively with each present bound of a uniquely resolved Coverage period. It never substitutes `billablePeriod`; absent dates, unresolved Coverage, and absent bounds become missing evidence. |
| `REPEAT-001` | Signals exact supported-field duplicate item signatures and, separately, exact opaque product/service `(system, code)` values occurring on at least two distinct items across this supplied sample. An item with any missing signature slot, including any Coverage-reference slot, is excluded and reported as missing evidence. It performs no near matching or code interpretation. |
| `AMOUNT-001` | When exactly one same-currency `benefit`, `paidbypatient`, and `drugcost` component is present, signals when `abs(drugcost - (benefit + paidbypatient)) > 0.01`. Missing, duplicate, or currency-conflicting components are not treated as zero. |
| `OUTLIER-001` | Per exact currency, with at least four `drugcost` observations, uses Tukey hinges and signals values strictly above `Q3 + 1.5 × IQR`. For the unchanged ten-value USD sample, `Q1=0`, `Q3=20`, and the threshold is `50`. |

The labels `information` and `review` are presentation priorities only. The rules do not interpret payer policy, product meaning, coding, medical necessity, clinical meaning, fraud, or payment correctness.

## Response shape

The full response is intentionally verbose and evidence-oriented. A shortened response looks like:

```json
{
  "analysis_id": "demo-d93ca1ac085b285cb82f2272",
  "source": {
    "dataset_name": "cms-blue-button-local-sample",
    "synthetic": true,
    "files": [{"alias": "patient", "path": "dataset/patient_bbuser29999.json", "sha256": "...", "size_bytes": 6196}],
    "resource_counts": {"Patient": 1, "Coverage": 4, "ExplanationOfBenefit": 10}
  },
  "observed_facts": [
    {"evidence_id": "ev:eob:/entry/0/resource/item/0/servicedDate", "source_alias": "eob", "json_pointer": "/entry/0/resource/item/0/servicedDate", "fact_type": "service_date", "value": "2015-10-01"}
  ],
  "rule_results": [
    {"rule_id": "OUTLIER-001", "status": "completed", "signals": [{"evidence_id": "sig:OUTLIER-001:0001", "priority": "information", "evidence_refs": ["ev:eob:/entry/8/resource/item/0/adjudication/7/amount/value"]}]}
  ],
  "evidence_index": [],
  "gemini": {
    "status": "success",
    "summary": "Bounded candidate summary based only on supplied synthetic evidence.",
    "candidate_findings": [{"title": "Candidate review item", "explanation": "...", "evidence_refs": ["sig:OUTLIER-001:0001"]}],
    "missing_evidence": [],
    "limitations": ["Candidate model text is non-authoritative."]
  },
  "model_metadata": {"provider": "vertex-ai", "sdk": "google-genai", "model": "...", "invoked": true, "call_count": 1, "output_validated": true},
  "limitations": ["This local demonstration uses a small synthetic sample."]
}
```

The actual contract requires complete rule metadata, evidence records, and model metadata; see `contracts/openapi.yaml` or `/docs`.

## Model boundary and failure behavior

Gemini receives only minimized structured synthetic facts, deterministic signals, supplied evidence IDs, and limitations. It receives no credentials, full FHIR resources, unnecessary patient attributes, real PHI, production claims, tools, file access, or external retrieval. The adapter permits at most one call, limits the prompt to 128 KiB, output to 2,048 tokens/64 KiB, and uses a 30-second client timeout.

Model output is accepted only if it matches the bounded Pydantic schema and every candidate finding cites supplied evidence. The typed model states are:

- `success`
- `configuration_error`
- `timeout`
- `provider_error`
- `invalid_output`
- `invalid_evidence`

All five failure states return HTTP 200 after deterministic success, with empty candidate findings and the complete deterministic report. Source, JSON, supported-shape, or extraction-limit failures return a sanitized HTTP 500 error and make no model call. There is no retry, repair call, or silent fallback model.

## Tests

Automated tests use injected fake model clients and require no cloud credentials:

```bash
PATH="$PWD/.venv/bin:$PATH" python -m pytest -q tests/backend
```

The focused suite covers extraction and evidence IDs, every rule's signal/no-signal/missing-evidence paths, sample quartile math, model configuration/provider/timeout/schema/citation failures, one-call enforcement, minimized prompts, endpoint responses, OpenAPI exposure, and source-file hash immutability.

## Limitations

- The three files contain a small synthetic sample and do not represent a payer, population, benchmark, or production distribution.
- Extraction is a narrow, explicit FHIR-shaped subset, not comprehensive FHIR profiling or strict CARIN conformance.
- Opaque codes and observed amount categories are not terminology, coding, clinical, coverage, payment, or medical-necessity judgments.
- Gemini output remains variable, candidate-only, and non-authoritative even when schema-valid and evidence-grounded.
- The unauthenticated local `/docs` interface is not approved for shared or cloud deployment.
- The project does not process real PHI and makes no HIPAA compliance, healthcare-validity, production-readiness, or autonomous-action claim.

## Resume-ready summary

Built a local FastAPI/Pydantic research demo that performs bounded extraction from synthetic FHIR R4 Patient, Coverage, and ExplanationOfBenefit JSON; generates five reproducible anomaly signals with stable evidence citations; and safely integrates one structured Vertex AI Gemini summarization call with strict output validation, citation allowlisting, deterministic fallback, and focused automated tests.
