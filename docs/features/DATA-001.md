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

## Approved architecture decision package

### 1. Boundary and artifact ownership

DATA-001 defines a versioned ingestion-data contract, not an application API. Its unit of validation is a **declared source set**: one or more JSON documents whose manifest, byte identities, classification, and resources are validated together. This is necessary because the approved seed has a standalone Patient document and separate paged search-result Bundles whose Coverage and ExplanationOfBenefit references resolve across files.

The contract worker must place the machine-readable boundary under `contracts/fhir/data-001/`:

- `boundary.json` — contract version, accepted envelopes/resources/profile canonicals, exact element and extension allowlists, reference rules, terminology policy, project invariants, stable rule registry, and outcome precedence;
- `packages.lock.json` — validator identity/version/digest plus every base/profile/terminology package identity, exact version, digest, authoritative source, dependency graph, license/usage evidence, and approved offline-materialization method;
- `validation-outcome.schema.json` — structured accepted/rejected/unsupported result schema;
- `source-manifest.json` and `data-card.json` — immutable source identities, classification, provenance/license status, intended use, and limitations; and
- `README.md` — the pinned offline invocation and the relationship between the artifacts.

Independent conformance fixtures and the reference harness belong under `tests/fixtures/fhir/data-001/` and `tests/data/`; they must not be placed in or generated into `dataset/`. No OpenAPI endpoint, persistence schema, production ingestion service, normalization implementation, or deployment resource is part of DATA-001.

These artifacts are a contract change because they define the healthcare input accepted by later backend/data-processing components and the stable validation result they may consume. This does not imply an HTTP API change; `contracts/openapi.yaml` remains unchanged unless a later task approves an application API.

### 2. Version and package evidence gate

FHIR R4 is the approved base release family. The observed resources declare these exact, unversioned profile canonicals:

- `http://hl7.org/fhir/us/carin-bb/StructureDefinition/C4BB-Patient`
- `http://hl7.org/fhir/us/carin-bb/StructureDefinition/C4BB-Coverage`
- `http://hl7.org/fhir/us/carin-bb/StructureDefinition/C4BB-ExplanationOfBenefit-Pharmacy`

The repository does not contain authoritative evidence for the exact FHIR core package version, CARIN Blue Button package version, transitive package versions, validator release, package digests, or redistribution/license terms. The architecture therefore does not infer them from the sample date, canonical spelling, memory, or a tool default.

**Contract gate:** before `CONTRACT_READY`, `packages.lock.json` must be completed from authoritative package publications and approved license/usage evidence. The chosen CARIN package must contain all three exact canonicals, declare compatibility with the chosen FHIR R4 core package, and validate the unchanged seed. The validator and packages must be pinned by immutable digest and made available to the test procedure without network access. An incoming version-qualified canonical is accepted only when its version equals the lock; the observed unversioned canonicals resolve only to the one locked version. Missing, ambiguous, mutable, mismatched, or unavailable lock material fails closed with `FHIR-PACKAGE-001` and cannot silently degrade to base-only validation.

This is a required evidence gate for DATA-001 implementation, not permission to choose a package from a non-authoritative source. If authoritative version/license evidence or an approved offline materialization cannot be obtained, the orchestrator must block before `CONTRACT_READY` and request the source-owner or other authorized human decision.

### 3. Minimal supported resource and envelope matrix

| Input level | Accepted boundary | Required project overlay | Explicitly unsupported initially |
|---|---|---|---|
| Declared source set | One bounded manifest plus the files it identifies; all file hashes and resources are evaluated as one reference-resolution unit | Unique source paths and SHA-256 values; explicit approved classification; unique `(resourceType, id)` keys | Undeclared files, archive traversal, remote fetches, streams, or implicit discovery outside the declared set |
| Standalone resource document | `Patient` declaring exactly the accepted Patient canonical | `resourceType`, `id`, `meta.profile`, and at least one identifier required for the scenario | Standalone Coverage/EOB documents and all other standalone resource types |
| Bundle envelope | Base FHIR `Bundle` with `type=searchset`; each Bundle is homogeneous and contains only Coverage entries or only ExplanationOfBenefit entries | Non-empty `entry.resource`; each resource has `id` and the one accepted canonical for its type; `total` may exceed the page entry count | `batch`, `transaction`, `history`, `document`, `message`, or `collection`; mixed-resource searchsets; executable request/response semantics |
| Coverage entry | Coverage declaring the accepted C4BB Coverage canonical | `status`, `beneficiary`, and the locked profile's required elements; beneficiary must resolve to a Patient in the source set | Inference that the coverage is active, applicable, Part D, or payment-authoritative |
| ExplanationOfBenefit entry | ExplanationOfBenefit declaring the accepted C4BB pharmacy EOB canonical | `status`, `type`, `use`, `patient`, `insurance`, and the locked profile's required elements; Patient and Coverage string references must resolve in the source set | Other EOB profiles/claim types and any inference of coverage, coding, payment, clinical, fraud, or policy correctness |

`Claim`, `Encounter`, `Organization`, `Practitioner`, `PractitionerRole`, `Medication`, `MedicationRequest`, `DocumentReference`, `Provenance`, `AuditEvent`, and every unlisted resource/profile remain explicitly unsupported. Identifier-only Reference values already allowed by the locked profile may be preserved, but DATA-001 does not assert that they resolve to an authoritative party. Provenance/AuditEvent export and DocumentReference evidence support remain deferred to later architecture/contract work.

### 4. Elements, extensions, references, and terminology

The exact machine-readable path registry must use these categories:

- **Required:** elements required by the locked base/profile definitions plus the project overlays in the matrix above.
- **Supported and preserved:** the observed scenario surface. Patient includes identifier, name, birth/death, gender, address, and the observed US Core race extension. Coverage includes status, type, beneficiary, period, relationship, subscriber identifier, payor, class, and the observed CMS extensions. Pharmacy EOB includes identifier, status/type/use, patient, billable period, created time, insurer/provider/facility, outcome, care team, supporting information, insurance, item, and optional payment.
- **Preserved but not normalized:** raw JSON bytes; profile-valid `meta.lastUpdated`; coding display text; Bundle paging metadata (`id`, `link`, `total`, entry `fullUrl`/`search` when present); profile-valid narrative; and allowed CMS extension/code values whose domain meaning has not been approved. Preservation does not confer trust or semantic support.
- **Unsupported:** paths or extension URLs absent from the versioned allowlist, `modifierExtension`, contained resources, embedded/remote attachments, executable Bundle request/response content, and any non-JSON representation. A profile-valid but unlisted element is still unsupported at the project layer; the profile alone cannot broaden this contract.

The extension registry must enumerate exact observed URLs in `boundary.json`; it may not accept a URL merely because it shares a CMS prefix. The observed families include the US Core race extension, CMS Blue Button variable extensions on Patient/Coverage/EOB, and the identifier-currency extension. Extension values are data, never instructions. Unknown extensions are `unsupported`; modifier extensions are `rejected` because their ignored meaning can alter interpretation.

String references are limited to same-source-set relative `Patient/{id}` and `Coverage/{id}` references. They must match the declared target type, resolve exactly once, and may not escape by URL, fragment, path traversal, logical indirection, or remote lookup. The observed Coverage-to-Patient and EOB-to-Patient/Coverage links are therefore checked across the declared source set, not only within one Bundle. Bundle link/fullUrl values and identifier systems are never dereferenced.

Terminology validation is offline and layered:

1. validate Coding/CodeableConcept shape and required bindings using only the locked packages;
2. reject a code that violates a required binding resolvable from the lock;
3. record warnings for extensible/preferred/example bindings according to the locked definitions without strengthening them into new requirements;
4. preserve exact system/code values for the enumerated observed HL7, NDC, CARIN, and CMS systems; and
5. mark CMS values not backed by a locked authoritative CodeSystem/ValueSet as `TERM-UNVERIFIED-001`, with no membership, display, benefit, or payer-semantics claim.

No canonical URI, code-system URI, Bundle URL, attachment URL, or reference may trigger network access. Display strings and narratives are never authoritative terminology.

### 5. Deterministic validation layers and outcomes

Validation runs in this order and records every completed layer without allowing a later layer to erase an earlier finding:

1. **Source/provenance gate:** manifest schema, exact bytes/hash, size/count limits, declared classification, acquisition/license evidence state, and prohibited-source policy.
2. **JSON/syntax gate:** UTF-8 JSON, duplicate-key rejection, maximum depth/size, one top-level object, and no permissive repair/coercion.
3. **Envelope/support gate:** accepted top-level form, Bundle type and homogeneity, resource type, exact profile declaration, and path/extension allowlists.
4. **Base FHIR gate:** offline validation against the locked R4 base definitions.
5. **Profile/terminology gate:** offline validation against the locked CARIN/terminology dependency graph and the terminology policy above.
6. **Reference/project gate:** unique identities, source-set reference resolution/type checks, paging-safe Bundle rules, and declared project invariants.
7. **Content-isolation gate:** narrative, display, URL, identifier, extension, and source content remain inert data and are excluded from instructions, dynamic configuration, file/network access, or trusted rendering.

The overall result is exactly `accepted`, `rejected`, or `unsupported`. `rejected` takes precedence for malformed, unsafe, prohibited-classification, or invalid supported content. `unsupported` applies to structurally recognizable content outside the declared resource/profile/envelope/element surface when no rejection condition exists. `accepted` may carry warnings such as preserved-untrusted narrative or unverified external terminology.

Each result must include contract version, validator/package-lock digest, source-set/manifest digest, source file SHA-256, resource pointer/type/id when available, layer outcomes, and ordered findings. Each finding contains a stable `rule_id`, severity, layer, machine code, sanitized message template, and JSON pointer; it must not echo narrative, identifiers, names, URLs, or other untrusted values. At minimum the registry defines and tests `SOURCE-MANIFEST-001`, `DATA-CLASS-001`, `JSON-SYNTAX-001`, `FHIR-PACKAGE-001`, `FHIR-BASE-001`, `FHIR-PROFILE-001`, `FHIR-RESOURCE-UNSUPPORTED-001`, `FHIR-ENVELOPE-UNSUPPORTED-001`, `FHIR-ELEMENT-UNSUPPORTED-001`, `FHIR-EXTENSION-UNSUPPORTED-001`, `FHIR-MODIFIER-001`, `FHIR-REF-001`, `FHIR-ID-001`, `TERM-UNVERIFIED-001`, and `FHIR-NARRATIVE-UNTRUSTED-001`.

FHIR conformance means only that the input passed these recorded structural rules. It does not establish whether a person, coverage, drug, provider, service, amount, claim, or policy statement is true, applicable, correct, payable, anomalous, fraudulent, clinically appropriate, or legally meaningful.

### 6. Provenance, source data card, and fixtures

The source manifest must reproduce this unchanged inventory:

| Path | Bytes | Raw SHA-256 | Git blob | Observed content |
|---|---:|---|---|---|
| `dataset/patient_bbuser29999.json` | 6,196 | `6fb43e72120e3a3cfb7bc756d0661eebcc0925a2bc994f60ecbf573813e3f58a` | `7ffe93441490616e32bd917774c4c5d86cc009d0` | One Patient with the accepted Patient canonical |
| `dataset/coverage_bundle_bbuser29999.json` | 83,096 | `fef088d7c6df3fb33bc02a1e32be53a67db0815046b1e2d998d44cb1536ec33c` | `dd33f5708a9ff2c1286417b50b27544d36232f6b` | Searchset page with four Coverage entries |
| `dataset/eob_bundle_bbuser29999.json` | 288,342 | `d48c12a8d94e331c786f3876ea94df4356209c216c54392346dae87f84fc34f0` | `2d6544059ea695946849199c1ec2daa9b28517d2` | Searchset page with ten pharmacy EOB entries; `total=146` is page metadata, not entry-count equality |
| `dataset/readme.txt` | 335 | `5c5c7641a7dbb1c5c21864e429390f7021d303fef5ad8eabacd01b805e205fe8` | `e123e526d2c29925c6faf175b0b9e24e7965919a` | Local description of the three example resource groups |

The recorded source-lineage commit remains `3fda38143e95c58a91b54781b15c84bc8436a1fa`. Repository evidence plus sponsor approval classifies the files as synthetic CMS Blue Button sample input for local development. It does not establish an upstream release identifier, acquisition timestamp, complete chain of custody, generation method, or license/redistribution approval. The data card must keep those fields `unverified` and block benchmark freeze/distribution beyond the approved boundary until an authorized source/license review resolves them. A validator must not infer classification or consent from FHIR content.

Every project-authored fixture must be stored outside `dataset/`, declare `project-authored-synthetic`, and record its own raw hash, parent hashes, deterministic recipe/version and seed or deterministic alternative, author, reviewer state, expected structural outcome/rule IDs, intended use, and limitations. Required classes are positive, negative, boundary, and adversarial, including malformed JSON, duplicate keys, wrong/missing profiles, unsupported resource/envelope/extension, duplicate IDs, broken/cross-type/external references, invalid required binding, source-classification failure, narrative instructions, URL/identifier instructions, and valid paging metadata. Fixture labels describe injected structure and expected validator behavior only; they are not payer, fraud, coverage, coding, clinical, or payment labels.

### 7. Offline verification and trust/failure behavior

The reference procedure must start with network disabled, verify validator and package digests before use, validate the contract artifacts, re-hash all four source files before and after the run, validate the source set and every fixture, compare ordered structured outcomes with expected rule IDs, and finish with a zero-diff dataset identity check. It must be reproducible in CI and local development without Vertex AI, cloud credentials, production access, a FHIR server, a terminology server, or any network fetch.

FHIR narratives (`text.div`), coding displays, extensions, identifiers, URLs, and all other source content are untrusted. The validator may parse narrative only as required for structural validation; it must not render active content, execute markup, follow links, import instructions, interpolate it into commands, or include it verbatim in logs. Raw bytes remain separately preserved by hash/path; any later normalized representation must omit or explicitly mark preserve-only untrusted content.

An unavailable validator/package, checksum mismatch, ambiguous version, malformed input, prohibited/unknown classification, invalid required reference, duplicate identity, or modifier extension fails closed. Unsupported content never falls through as accepted. Failures produce the structured result and stop downstream ingestion; DATA-001 does not create a quarantine store. No validator success can promote the data card's license/provenance status or make a domain claim.

### 8. Change control and downstream handoff

The boundary uses semantic versioning. A major version is required for an accepted resource/profile/envelope change, a package/profile version change, weakened rejection/classification/reference behavior, changed rule meaning, or removal of a supported path. A minor version may add a backward-compatible allowed path, terminology artifact, or rule while preserving existing outcomes. A patch may clarify documentation or messages without changing machine behavior. Rule identifiers are never reused with different meanings; retired identifiers remain reserved.

Any package, validator, boundary, fixture recipe, source byte, classification, or evidence change updates its digest and reruns the full offline suite. A source-byte change creates a new source/benchmark version and never authorizes editing `dataset/`. A new payer, profile, claim type, resource, remote terminology dependency, narrative rendering path, attachment, or cross-component runtime interface requires upstream feature/architecture review and, where applicable, contract/security review.

Architecture impact is deliberately limited:

- `contract_change=true`: the versioned FHIR input and validation-result contract must be created and validated.
- `testing=true`: an independent tester must implement/review the offline conformance harness and fixtures and record durable evidence.
- `database=false`, `backend=false`, `frontend=false`, and `infrastructure=false`: DATA-001 must not pre-implement PLATFORM-001's persistence, API, UI, runtime service, Docker topology, or deployment. Pinned task-local validation tooling is verification tooling, not application infrastructure.

PLATFORM-001 may rely on the accepted envelope/resource/profile matrix, package lock, exact rule registry, structured outcome schema, source/data-card identity, and raw-versus-derived boundary. It must choose physical storage, normalization models, API behavior, size limits for an actual endpoint, quarantine persistence, authorization, and runtime integration without weakening this contract. RISK-001 may consume only validated/normalized fields and must separately approve domain feature semantics. POLICY-001, RETRIEVAL-001, INVESTIGATION-001, GOVERNANCE-001, and EVALUATION-001 may not treat FHIR conformance, narrative, terminology display, or synthetic fixture outcomes as domain truth.
