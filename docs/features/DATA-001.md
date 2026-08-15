# DATA-001 — Define and validate the minimal FHIR R4 profile

## Goal

Define and validate the smallest explicit FHIR R4 ingestion boundary needed for VeriClaim's initial synthetic Medicare Part D research scenario. The result must let downstream work accept supported Patient, Coverage, ExplanationOfBenefit, and bundle inputs reproducibly, reject unsupported or malformed data safely, preserve provenance, and avoid treating structural conformance as payer-policy or claim correctness.

## In scope

- Inventory the approved read-only Blue Button seed files as immutable negative evidence and reconcile their observed resources, profiles, bundle shapes, references, extensions, code systems, and terminology use with an explicitly pinned FHIR R4/CARIN baseline.
- Define the initial supported resource/profile matrix for Patient, Coverage, ExplanationOfBenefit, and any Bundle envelopes required by the corpus; make a deliberate supported/unsupported decision for other observed or proposed resource types rather than silently accepting them.
- Define required, optional, conditionally required, preserved-but-not-normalized, and unsupported elements/extensions needed for the bounded scenario, including identifier/reference integrity and terminology handling.
- Separate validation layers: JSON/syntax, base FHIR R4 structure, declared profile compatibility, bundle/reference integrity, project invariants, data classification/provenance, and later payer/domain semantics.
- Produce versioned, machine-readable profile/validation artifacts and a human-readable support matrix at paths approved by architecture.
- Provide deterministic, runnable validation for byte-identical official publication-example candidates, the unchanged negative seed corpus, and explicitly synthetic derived-envelope, negative, boundary, and adversarial fixtures stored outside repository-root `dataset/`; no official example becomes an approved positive until both strict conformance and synthetic classification are authoritatively established.
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
- The unchanged four-file seed corpus is inventoried by repository path, byte length, SHA-256, Git identity/lineage, observed profile/resource facts, synthetic classification, and provenance/license evidence status; it is nonconformant/unsupported as an accepted CARIN 2.2.0 source and is used only as deterministic negative rejection evidence. Missing acquisition or license evidence remains an explicit benchmark-freeze blocker rather than an invented approval.
- Candidate resource fixtures are byte-identical publication examples from the checksum-pinned official `hl7.fhir.us.carin-bb#2.2.0` archive and retain package path, package/resource digest, publication-example classification, exact package-manifest license evidence, and an explicit `UNVERIFIED_AS_SYNTHETIC` classification until authoritative generation/no-real-person provenance is supplied. Project-authored derived-envelope, negative, boundary, and adversarial fixtures are clearly distinguished outside `dataset/`, retain parent/recipe/version provenance, contain no real PHI or secrets, and cover malformed input, unsupported resources/profiles, broken references, narrative/instruction content, and declared project invariants.
- A runnable, pinned validation/test procedure passes for approved inputs, rejects or marks unsupported inputs as specified, proves `dataset/` remains byte-identical, and requires no network, cloud, model, production, or live terminology-service access.
- Documentation clearly distinguishes FHIR/profile conformance from coverage, payment, coding, fraud, clinical, or policy correctness and leaves undeclared semantics unsupported.
- The final handoff identifies what PLATFORM-001 and later tasks may rely on, what remains deferred, and which changes would require a new profile version or upstream architecture/contract review.

## Approved architecture decision package

### 1. Boundary and artifact ownership

DATA-001 defines a versioned ingestion-data contract, not an application API. Its validation unit is a **declared source set**: one or more JSON documents whose manifest, byte identities, classification, resources, and permitted cross-document references are evaluated together. The machine boundary remains under `contracts/fhir/data-001/`: `boundary.json`, `packages.lock.json`, `validation-outcome.schema.json`, `source-manifest.json`, `data-card.json`, and `README.md`. Conformance fixtures and the independent reference harness remain under `tests/fixtures/fhir/data-001/` and `tests/data/`.

These are contract and test artifacts only. DATA-001 does not add an OpenAPI endpoint, persistence schema, runtime ingestion service, normalization implementation, application dependency, or deployment resource. `contracts/openapi.yaml` remains unchanged.

### 2. Pinned strict baseline and corpus authority

The selected baseline is FHIR R4 `4.0.1`, `hl7.fhir.us.carin-bb#2.2.0`, and HL7 FHIR Validator CLI `6.10.2`, using the checksum-pinned dependency closure in `packages.lock.json` with `-no-http-access` and `-tx n/a`. No latest-version lookup, older CARIN release, profile substitution, source rewrite, fabricated StructureDefinition, or invented terminology semantics is permitted.

The repository-root seed is preserved byte-identical but is not an accepted positive. Its unversioned profiles and structural/profile errors make it nonconformant/unsupported under this strict 2.2.0 boundary; its expected contract behavior is fail-closed rejection evidence only.

Positive resources must come byte-identical from publication-labeled examples in the exact official package archive, produce no validator `error` or `fatal` result under the pinned offline invocation, and have authoritative synthetic generation/no-real-person provenance. Warnings and informational findings are retained, not silently discarded. The package manifest supplies package identity, FHIR version, example-directory labeling, and `CC0-1.0` license evidence, but it does not attest a synthetic generation method or no-real-person provenance. Accordingly all three official examples have `synthetic_classification=UNVERIFIED_AS_SYNTHETIC`; the fixture manifest must record that status with each archive path and resource digest.

| Official archive example | SHA-256 | Strict offline result | Positive status |
|---|---|---|---|
| `package/example/Patient-Patient2.json` | `5126c680cdcb0ccd1d0c0c032b720f1a92224fff2f5bf3fa30ab7319e437a188` | zero errors; warnings/information retained | structural candidate only; synthetic classification unverified |
| `package/example/Coverage-Coverage3.json` | `e72295932c41b57291e0013dfb3e81d2ae37fbcf549090fdf14932a6fefc7d83` | zero errors; warnings/information retained | structural candidate only; synthetic classification unverified |
| `package/example/ExplanationOfBenefit-EOBPharmacy1.json` | `46952eba56089a44272d2707c87accc5f16325ec8d91acdf7eed107a1080fe62` | pinned strict offline validator reports eight terminology errors; publisher QA reports zero errors and five warnings | not an offline strict positive; blocks DATA-001 |

The same official archive contains publisher-generated `package/other/validation-summary.json` (SHA-256 `39dfcb19c9e522e8e812778f327f22766c0405f53a10e6cfc550e1d33a48514e`) and `package/other/validation-oo.json` (SHA-256 `d214c310a03f88cc1384d76945417395a7ae92cee04d906c87c72e9f29d07aaf`). They record zero errors for Patient/Patient2, Coverage/Coverage3, and ExplanationOfBenefit/EOBPharmacy1; the EOB OperationOutcome contains five warnings: four unavailable NCPDP CodeSystems and one inactive NDC concept.

That publisher QA is provenance evidence, not a substitute for the approved strict offline procedure. The pinned local validator produces eight errors for the exact EOB: four report that a CodeSystem definition is not found, and four report that CodeSystem version `null` is not found while available metadata names version `1.0.2`. The four affected CARIN slices use `required` bindings. In the exact package closure their NCPDP ValueSets contain no expansion/concept content and compose CodeSystems whose definitions are `content=not-present`; the package points to restrictively copyrighted NCPDP standards access. No usage-approved authoritative offline terminology corpus is available.

Therefore neither publisher-QA substitution nor `TERM-UNVERIFIED-001` severity normalization is approved. Either would treat unverifiable required bindings as a strict positive. An exact authoritative pharmacy EOB that produces no offline validator error under the approved lock, or a usage-approved authoritative offline terminology corpus that validates the unchanged official example without rewriting it, is required before DATA-001 can proceed.

Independently, publication-example status and CC0 licensing do not prove that any example is synthetic or unrelated to a real person. Patient2 and Coverage3 therefore remain structural candidates rather than approved fixtures despite their zero-error results. An authoritative source attestation or equivalent approved provenance establishing synthetic generation/no-real-person status is required for the candidate corpus. Validator success cannot promote this classification.

### 3. Target resource and envelope boundary after the blocker is resolved

The intended accepted resource surface is exactly one version-qualified CARIN 2.2.0 Patient, Coverage, and pharmacy ExplanationOfBenefit profile. The byte-identical official Patient and Coverage resources are zero-error structural candidates but are not approved positives while their synthetic classification is unverified; an authoritative strict offline pharmacy EOB positive also remains unavailable. Project-authored envelopes may wrap only fully approved positive resource JSON deterministically and may not edit child resources or claim official provenance for the envelope.

The minimal envelope remains a homogeneous FHIR `Bundle` with `type=searchset`, one supported resource type per Bundle, deterministic `total` and `entry.fullUrl`, and no request/response execution content. A declared source set may contain the Patient, Coverage, and EOB searchsets together so relative EOB-to-Coverage and Coverage/EOB-to-Patient references resolve across documents. The generated envelope is labeled `project-authored-synthetic`, records its recipe/version and all parent hashes, and asserts only contract transport/reference behavior—not that an upstream search occurred or that any domain fact is true. No accepted EOB envelope may be generated until its parent is a strict offline positive.

Relative Patient and Coverage references required for this bounded chain must resolve exactly once within the declared source set. Profile-valid Organization references in the official examples are preserved as untrusted, unresolved, unsupported-target references and are never dereferenced or treated as authoritative organization evidence. Every other resource/profile, mixed searchset, other Bundle type, contained resource, attachment, modifier extension, executable request/response content, and non-JSON representation remains unsupported or rejected according to the rule registry.

### 4. Elements, terminology, and outcome policy

The contract allowlist is derived from the locked profile plus official candidates only after they satisfy both strict conformance and classification gates, never from the nonconformant root seed. Required fields and terminology retain the locked profile's cardinalities, constraints, slices, and binding strengths. Profile-valid optional content in an approved example may be supported/preserved only when enumerated. Narratives, displays, identifiers, URLs, and allowed reference strings remain inert, untrusted data and are never rendered, executed, dereferenced, or echoed in findings.

`TERM-UNVERIFIED-001` is permitted only for unavailable terminology on `extensible`, `preferred`, or `example` bindings, or preserved values not governed by a binding. It must never downgrade a validator error on a `required` binding, fixed/pattern conformance, slice discrimination, invariant, or coding-version resolution. Required terminology that is absent, ambiguous, version-mismatched, or unverifiable fails closed with `FHIR-PROFILE-001` or the more specific locked rule.

Validation retains the ordered layers: source/provenance, strict JSON, envelope/support, base FHIR, CARIN profile/terminology, reference/project invariants, and content isolation. The structured overall result remains exactly `accepted`, `rejected`, or `unsupported`; `rejected` takes precedence for malformed, unsafe, or invalid attempted supported content, while structurally recognizable out-of-surface content is `unsupported`. No outcome message may echo names, identifiers, narrative, URLs, or other untrusted values.

FHIR conformance establishes only recorded structural/profile behavior. It does not establish coverage, payment, coding, fraud, clinical, payer-policy, beneficiary, provider, amount, or real-world correctness.

### 5. Provenance and fixtures

The root source manifest must preserve the existing FOUNDATION-001 inventory and source-lineage commit `3fda38143e95c58a91b54781b15c84bc8436a1fa` exactly:

| Path | Bytes | Raw SHA-256 | Git blob |
|---|---:|---|---|
| `dataset/patient_bbuser29999.json` | 6,196 | `6fb43e72120e3a3cfb7bc756d0661eebcc0925a2bc994f60ecbf573813e3f58a` | `7ffe93441490616e32bd917774c4c5d86cc009d0` |
| `dataset/coverage_bundle_bbuser29999.json` | 83,096 | `fef088d7c6df3fb33bc02a1e32be53a67db0815046b1e2d998d44cb1536ec33c` | `dd33f5708a9ff2c1286417b50b27544d36232f6b` |
| `dataset/eob_bundle_bbuser29999.json` | 288,342 | `d48c12a8d94e331c786f3876ea94df4356209c216c54392346dae87f84fc34f0` | `2d6544059ea695946849199c1ec2daa9b28517d2` |
| `dataset/readme.txt` | 335 | `5c5c7641a7dbb1c5c21864e429390f7021d303fef5ad8eabacd01b805e205fe8` | `e123e526d2c29925c6faf175b0b9e24e7965919a` |

The seed data card retains synthetic local-development approval but keeps acquisition, generation, upstream release, chain-of-custody, license, and redistribution fields `unverified`. It is never copied, repaired, normalized into a positive, or promoted by validator behavior.

Official resource candidates retain exact package/archive provenance and bytes and remain `UNVERIFIED_AS_SYNTHETIC` until authoritative evidence changes that classification. They must not be copied into an approved positive-fixture partition or used as parents of accepted envelopes before then. Every permitted derived envelope or perturbation is separately labeled `project-authored-synthetic` and records its raw hash, parent hashes, deterministic recipe/version, author/reviewer state, expected structural outcome/rule IDs, intended use, and limitations. Fixture labels describe validator behavior only and are never domain labels.

### 6. Offline verification, change control, and handoff

The independent procedure must start with network disabled, verify validator/package/fixture/publisher-QA digests, validate contract artifacts and classification evidence, re-hash the root dataset before and after, require zero validator errors and approved synthetic classification for every positive, assert stable rejection/unsupported results for the root seed and negative/adversarial fixtures, verify derived-envelope lineage, and finish with a zero-diff dataset check. It must not require Vertex AI, cloud credentials, a FHIR server, a live terminology service, or production access.

Any validator, package, terminology artifact, boundary, official fixture, derived recipe, source byte, classification, or evidence change invalidates the relevant results and reruns the entire offline suite. Profile/package/envelope changes or weakened required-binding/reference/safety behavior require major-version architecture and contract review. Rule identifiers are never reused with different meanings.

Architecture impact remains deliberately limited: `contract_change=true` and `testing=true`; `database=false`, `backend=false`, `frontend=false`, and `infrastructure=false`. Contract and test work must remain paused: Patient/Coverage are unverified-synthetic structural candidates rather than approved positives, the pharmacy EOB is not a strict offline positive, and no publisher-QA adapter or required-binding downgrade may be encoded. PLATFORM-001 and later tasks may rely only on a subsequently completed, passing contract; they must keep raw and derived data distinct and must not treat FHIR conformance, publisher-example status, or fixture status as domain truth.
