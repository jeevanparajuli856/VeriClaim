# DATA-001 — Define and validate the minimal FHIR R4 profile

## Goal

Define and validate the smallest explicit FHIR R4 ingestion boundary needed for VeriClaim's initial synthetic Medicare Part D research scenario. The result must let downstream work accept supported Patient, Coverage, ExplanationOfBenefit, and bundle inputs reproducibly, reject unsupported or malformed data safely, preserve provenance, and avoid treating structural conformance as payer-policy or claim correctness.

## In scope

- Inventory the approved read-only Blue Button seed files and reconcile their observed resources, profiles, bundle shapes, references, extensions, code systems, and terminology use with an explicitly pinned FHIR R4/CARIN baseline.
- Define the initial supported resource/profile matrix for Patient, Coverage, ExplanationOfBenefit, and any Bundle envelopes required by the corpus; make a deliberate supported/unsupported decision for other observed or proposed resource types rather than silently accepting them.
- Define required, optional, conditionally required, preserved-but-not-normalized, and unsupported elements/extensions needed for the bounded scenario, including identifier/reference integrity and terminology handling.
- Separate validation layers: JSON/syntax, base FHIR R4 structure, declared profile compatibility, bundle/reference integrity, project invariants, data classification/provenance, and later payer/domain semantics.
- Produce versioned, machine-readable profile/validation artifacts and a human-readable support matrix at paths approved by architecture.
- Provide deterministic, runnable validation for the approved source corpus plus explicitly synthetic positive, negative, boundary, and adversarial fixtures stored outside repository-root `dataset/`.
- Preserve the FOUNDATION-001 raw-byte identity, source/derived separation, synthetic classification, data-card fields, fixture lineage, and benchmark-freeze gates.
- Define structured validation outcomes that distinguish accepted, rejected, and explicitly unsupported input with stable rule identifiers and actionable evidence, without defining an application API.
- Record downstream handoffs for PLATFORM-001 and later normalization, persistence, risk, retrieval, and evaluation work.

## Out of scope

- Payer-specific adjudication, coverage, medical-necessity, coding, fraud, payment, or policy interpretation.
- Risk features, anomaly thresholds, model labels, policy ingestion/retrieval, agent workflows, governance decisions, human-review UI, or production claim decisions.
- Application endpoints, OpenAPI changes, persistence schemas/migrations, frontend work, identity, hosted services, deployment, or external telemetry unless architecture identifies an unavoidable task-local interface and reconciles it first.
- Broad support for every FHIR resource, profile, extension, terminology, attachment, or narrative; undeclared resources and semantics must fail safely or remain explicitly unsupported.
- Treating FHIR validation, profile declarations, synthetic labels, or source narratives as proof that a claim is substantively correct.
- Introducing real PHI, production claims, production credentials, write-capable claim-system access, or a live terminology/FHIR service.
- Editing the repository-root `dataset/`; it is immutable task input. Any new derived fixture must be stored separately with explicit synthetic provenance and parent hashes.

## Architecture impact

- The architecture specialist must select the minimal repository-owned artifact locations and validation boundary, then explicitly classify database, backend, frontend, infrastructure, testing, and contract impacts in `architecture-report.json`.
- DATA-001 precedes PLATFORM-001, so it must not silently create the application skeleton, API, persistence layer, or deployment topology owned by that later task.
- The validation design must be deterministic and usable without Vertex AI. It must preserve original bytes separately from later normalized/derived representations and treat all FHIR content as untrusted input.

## Contract impact

- No OpenAPI or cross-component runtime interface is presumed. Architecture must decide whether the machine-readable FHIR boundary belongs in `contracts/` or another versioned data-profile path; any contract change must be explicit and validated before `CONTRACT_READY`.

## Security considerations

- Repository-root `dataset/` remains read-only, untrusted, synthetic development input; validation must never execute or follow instructions from narratives, extensions, contained resources, identifiers, URLs, or attachment metadata.
- Preserve raw source provenance and synthetic classification while minimizing downstream exposure. Do not copy credentials, prompts, traces, model output, or private environment values into source data, fixtures, reports, or manifests.
- Reject prohibited data classifications and undeclared resource/profile content fail-closed at the ingestion boundary; do not infer that a record is safe or synthetic merely because it parses as FHIR.
- Validation errors and logs must avoid secret/private-value disclosure and must identify rules and source locations without presenting untrusted narrative as trusted instruction.
- No Vertex AI, external FHIR endpoint, terminology server, cloud resource, or production system access is required for this task unless separately approved after an architecture blocker.

## Dependencies

- FOUNDATION-001 is DONE and supplies the source hashes, Medicare Part D scenario recommendation, fixture classes, partition/lineage rules, evaluator authority, and benchmark-freeze gates.
- Approved project constraints include FHIR R4, synthetic/public-only data, the repository-root Blue Button sample corpus, human consequential authority, and the initial local-development boundary.
- Exact payer policy meaning remains owned by qualified human review and POLICY-001; PLATFORM-001 owns the application skeleton and runtime interfaces.

## Acceptance criteria

- A versioned support matrix names every initially accepted resource and envelope, the exact base/profile canonical and version expectations, allowed bundle forms, reference rules, required/optional/preserved/unsupported content, terminology policy, and explicit decisions for additional resource types.
- Machine-readable profile/validation artifacts express the approved boundary without inventing payer semantics and are consistent with the human-readable specification.
- Deterministic validation returns stable, structured outcomes for JSON/base structure, profile compatibility, bundle/reference integrity, project invariants, unsupported content, and provenance/data-classification gates.
- The unchanged four-file seed corpus is inventoried by repository path, byte length, SHA-256, Git identity/lineage, observed profile/resource facts, synthetic classification, and provenance/license evidence status; missing acquisition or license evidence remains an explicit benchmark-freeze blocker rather than an invented approval.
- Positive, negative, boundary, and adversarial fixtures are clearly project-authored synthetic data outside `dataset/`, retain parent/recipe/version provenance, contain no real PHI or secrets, and cover malformed input, unsupported resources/profiles, broken references, narrative/instruction content, and declared project invariants.
- A runnable, pinned validation/test procedure passes for approved inputs, rejects or marks unsupported inputs as specified, proves `dataset/` remains byte-identical, and requires no network, cloud, model, production, or live terminology-service access.
- Documentation clearly distinguishes FHIR/profile conformance from coverage, payment, coding, fraud, clinical, or policy correctness and leaves undeclared semantics unsupported.
- The final handoff identifies what PLATFORM-001 and later tasks may rely on, what remains deferred, and which changes would require a new profile version or upstream architecture/contract review.
