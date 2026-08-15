# VeriClaim one-day demo architecture

> Status: **INCEPTION_READY; validated 2026-08-15.** This architecture implements the approved scope reset. It is a local demonstration/research prototype, not a production healthcare platform.

## 1. Architectural objective

Build the smallest credible end-to-end path from the existing synthetic FHIR R4 JSON files to an evidence-grounded response visible in FastAPI `/docs`, while preserving deterministic behavior when Vertex AI Gemini fails.

## 2. Active components

| Component | Enabled | Technology | Responsibility |
|---|---:|---|---|
| Local API/backend | Yes | Python, FastAPI, Pydantic | Load fixed inputs, perform minimal checks/extraction, run deterministic rules, call Gemini once, validate and return the report |
| Separate frontend | No | — | FastAPI `/docs` is the demonstration interface |
| Database | No | — | All processing and output are in memory; source JSON stays read-only |
| Model integration | Yes | Google Gen AI SDK configured for Vertex AI | Produce one bounded structured candidate summary from supplied synthetic evidence |

Existing Next.js, PostgreSQL/pgvector, Supabase, Docker, retrieval, identity, multi-agent, and platform-runtime scaffolds are not active components and are not milestone dependencies.

## 3. Runtime flow

```text
POST /api/v1/analyze-demo
  -> fixed local dataset loader
  -> minimal JSON and supported-shape checks
  -> narrow Patient/Coverage/EOB extractor
  -> deterministic rule engine (five pure checks)
  -> evidence-indexed deterministic report
  -> one bounded Vertex AI Gemini call
  -> Pydantic + evidence-reference validation
  -> combined JSON response
```

If the model call, configuration, transport, parsing, schema validation, or evidence validation fails, the flow skips model findings and returns the deterministic report with a typed failure status and limitation.

## 4. Module boundaries proposed for DEMO-001

The exact filenames belong to task architecture, but the implementation should keep these responsibilities explicit:

- **API route:** thin `POST /api/v1/analyze-demo` handler and response mapping.
- **Dataset loader:** allowlisted repository-relative input paths, read-only byte loading, JSON parsing, and source metadata.
- **Minimal extractor:** supports only the documented Patient, Coverage Bundle entries, and ExplanationOfBenefit Bundle entries/fields.
- **Rule engine:** pure deterministic checks with stable rule IDs and evidence references.
- **Evidence index:** stable IDs for source resources, extracted fields, and rule signals.
- **Gemini summarizer:** constructs minimized structured input, performs at most one Google Gen AI SDK/Vertex AI call, and exposes no tools.
- **Response validator/assembler:** validates Pydantic output and confirms every model citation resolves to supplied evidence.

No repository, ORM, migration, queue, cache, retrieval layer, agent framework, custom UI, or deployment module is needed.

## 5. Supported extraction boundary

### Patient

- `resourceType`, `id`, and only the minimum identifier/reference facts needed to resolve links.
- Do not send name, address, birth date, narrative, or other unnecessary patient attributes to Gemini.

### Coverage

- Bundle/resource identity, Coverage `id`, `status` as an observed opaque value, `beneficiary.reference`, and optional `period.start`/`period.end`.

### ExplanationOfBenefit

- Bundle/resource identity, EOB `id`, `patient.reference`, `insurance[*].coverage.reference`, billable/service dates, item sequence, opaque product/service system+code, selected adjudication category codes, numeric values, and currency.
- Displays and coding systems are untrusted labels. They do not establish terminology membership or domain correctness.

### Minimal structural checks

- UTF-8 JSON object parsing with clear bounded failures.
- Expected standalone Patient and searchset Bundle/resource shapes for the three approved files.
- Required identifiers, relevant arrays/objects, date strings, numeric amount values, and reference strings used by the extractor.
- Unique `(resourceType, id)` keys for supported resources.

This boundary intentionally does not perform strict base FHIR, profile, CARIN, NCPDP, or comprehensive terminology validation.

## 6. Deterministic rule boundary

Each rule returns a stable rule ID, outcome, severity/priority label limited to the demo, plain-language rationale, evaluated facts, evidence references, threshold/formula metadata, and limitations.

1. **Reference integrity:** required Patient and Coverage references resolve exactly once within the loaded supported resource set.
2. **Coverage-date bound:** a service date is compared only with present start/end boundaries on its referenced Coverage; absent boundaries are missing evidence, not inferred dates.
3. **Duplicate/repetition:** exact item keys can identify duplicates; repeated opaque product/service codes are counted within a documented window or the entire supplied sample. Repetition is only an investigation signal.
4. **Observed amount relationship:** for exact supported category fields, compare `drugcost` with available `benefit + paidbypatient` using an explicit tolerance. A mismatch says only that the selected observed components do not reconcile; unmodeled components are a stated limitation.
5. **Sample-relative high amount:** compare the selected amount with a fixed, documented small-sample statistic/threshold. It never claims the amount is improper outside this sample.

Rules must not infer drug/procedure meaning, allowed/billed semantics absent from the sample, payer policy, fraud, medical necessity, clinical meaning, or payment correctness.

## 7. Response contract shape

The DEMO-001 API contract must define a response that keeps these sections separate:

- analysis/source metadata and source-file identities;
- `observed_facts` with evidence IDs;
- `deterministic_signals` and rule execution metadata;
- `gemini` status, validated candidate findings, missing evidence, and limitations;
- a resolvable evidence index;
- global limitations; and
- sanitized model/configuration metadata such as provider, model name, prompt/schema versions, invocation/validation status, and available latency/token data.

Every Gemini finding must cite one or more evidence IDs supplied in its request. Unknown or absent citations invalidate the Gemini portion without discarding deterministic output.

## 8. Gemini trust boundary

- Use the Google Gen AI SDK configured for Vertex AI and local Application Default Credentials.
- Make zero or one model call per endpoint invocation and expose no tools, file access, retrieval, code execution, or agent loop.
- Send only minimized structured synthetic facts, deterministic signals, evidence IDs, and limitations.
- Require structured output matching a Pydantic-owned schema.
- Treat candidate explanations as untrusted, non-authoritative text.
- Explicitly prohibit fraud conclusions; approve/deny/payment/coverage/coding/medical-necessity/diagnostic/clinical decisions; data modification; and requests for missing external facts.
- Keep credentials, project IDs, private environment values, raw unnecessary identifiers, and full raw FHIR payloads out of prompts, responses, and committed fixtures.

## 9. Failure behavior

| Failure | Required behavior |
|---|---|
| Source missing/malformed or unsupported required shape | Fail the deterministic pipeline clearly; no model call |
| Individual optional fact missing | Record missing evidence; continue when rules can remain honest |
| Gemini configuration/provider timeout/error | Return deterministic report with `gemini` unavailable/error status |
| Gemini non-JSON or schema-invalid output | Return deterministic report with invalid-output status |
| Gemini cites unknown evidence | Reject Gemini findings and return deterministic report with evidence-validation failure |

No silent provider fallback or second repair call is allowed in the one-day milestone.

## 10. Data integrity and state

- `dataset/` is immutable application input. Tests must hash or otherwise prove source files are unchanged.
- All parsed resources, extracted facts, signals, request payloads, model output, and assembled responses live in process memory only.
- Project-authored negative fixtures live outside `dataset/` and are clearly marked synthetic.
- No database, file upload, remote URL loading, model-written file, or generated dataset mutation exists.

## 11. Security boundary

- Bind the demonstration server to a local development interface by default and make no deployment claim.
- Validate file allowlists, parsed types, bounded collection/string sizes, numeric finiteness, and model response sizes.
- Do not render untrusted FHIR or model strings as HTML.
- Redact provider errors and never log secrets or private runtime values.
- Authentication/RBAC is explicitly out of scope because this is a local synthetic-only demo; any networked or shared deployment must add a new security architecture first.

## 12. Verification strategy

- Pure unit tests for extraction, stable evidence IDs, and every rule including no-signal and missing-evidence cases.
- Integration tests for endpoint response separation, model success via a fake client, timeout/provider failure, invalid structured output, unknown citations, and no second model call.
- Source immutability check before/after relevant tests.
- Standard project/task/report validation plus the project-level pytest command declared in `.ai/project.json` once DEMO-001 exists.

## 13. Historical reconciliation

- FOUNDATION-001 remains `DONE`; its reports are retained as historical research.
- DATA-001 is `CANCELLED` through `agentctl.py`. Its reports/contracts remain intact, including its final review blockers concerning diagnostic evidence binding, contradictory schema states, strict-JSON numeric failure, and Bundle field inconsistency.
- The DATA-001 CARIN/offline terminology compatibility contract is historical evidence, not an active dependency or conformance claim for this demo.
- ADR-0003 is superseded for the current milestone; ADR-0004 is amended to select direct Google Gen AI SDK integration for one bounded Vertex AI call.

## 14. Future architecture

Custom UI, persistence, identity, retrieval, deployment, observability, additional FHIR resources, production hardening, and regulated-data work are possible future projects only. They must not add components, blockers, or implied requirements to DEMO-001.
