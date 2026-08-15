# DATA-001 — Define and validate the minimal FHIR R4 compatibility boundary

## Historical disposition — cancelled 2026-08-15

DATA-001 is preserved as completed work-in-progress and review evidence, but it is no longer an active project dependency. The approved one-day project scope reset removed strict CARIN diagnostics, offline terminology packages, and comprehensive FHIR compatibility work from the milestone, so the orchestrator changed the task from `BLOCKED` to `CANCELLED` through `python3 scripts/agentctl.py task status DATA-001 CANCELLED`.

The cancellation does not imply that final review passed. `review-report.json` remains `CHANGES_REQUIRED` and records four unresolved blockers: CARIN evidence was not bound to each validated source set, the validation schema allowed contradictory CARIN states/evidence, a very large JSON integer could escape fail-closed handling, and Bundle `id`/`total` requirements conflicted across the feature/architecture/executable contract. All reports, tests, and `contracts/fhir/data-001/` artifacts remain intact so this history is not hidden or rewritten.

The material below is the historical DATA-001 specification. It is not an active CARIN-conformance requirement for DEMO-001.

## Goal

Define the smallest project-owned FHIR R4 compatibility boundary needed to ingest VeriClaim's approved synthetic Blue Button seed reproducibly. The boundary accepts only the observed Patient, Coverage, pharmacy ExplanationOfBenefit, and searchset shapes after deterministic source, JSON, required-field, reference, and content-isolation checks. CARIN Blue Button 2.2.0 validation remains a pinned diagnostic and does not decide project acceptance.

This is a compatibility contract, not a claim of base FHIR or CARIN conformance, payer correctness, terminology membership, or domain truth.

## Approved scope decision

- The repository-root `dataset/` is the approved synthetic local-development source established by `docs/PROJECT.md`, `docs/architecture/SYSTEM.md`, and ADR-0002. Its acquisition/license gaps continue to block benchmark freeze or redistribution, but do not block the approved local compatibility boundary.
- The seed remains byte-identical, read-only, and untrusted. It may pass the project-defined minimal profile even when pinned CARIN 2.2.0 diagnostics report errors.
- FHIR R4 is the representation family. The project does not silently claim full base FHIR conformance where the seed intentionally falls outside a base/profile invariant, such as missing `Bundle.entry.fullUrl`.
- CARIN 2.2.0, its package closure, publisher QA, and HL7 Validator CLI 6.10.2 are diagnostic evidence only. Every finding is preserved; none changes the minimal-profile acceptance decision.
- CMS, NCPDP, CARIN, HL7, NDC, and other coding/extension values are untrusted data. When membership or meaning is not established by approved offline evidence, they are opaque and produce `terminology-unverified`; the project never invents concepts, rewrites codes, or asserts display/domain meaning.
- Synthetic-only classification, source provenance, content isolation, evidence separation, and human authority remain mandatory gates. No real PHI, production claim, autonomous adjudication, payment decision, fraud determination, diagnosis, or clinical conclusion is permitted.

## In scope

- Versioned machine-readable compatibility rules for the exact supported resources, envelopes, required anchor fields, references, preserved paths/extensions, rejected content, rule identifiers, and outcome states.
- A declared source-set manifest covering one standalone Patient document, homogeneous Coverage and ExplanationOfBenefit searchset documents, and the immutable provenance readme.
- Strict UTF-8 JSON parsing with duplicate-key rejection and no repair/coercion.
- Exact source classification, hash, resource identity, and cross-file reference checks.
- Pinned, offline CARIN 2.2.0 diagnostics whose raw evidence is retained by digest and whose normalized findings remain distinct from project findings.
- Deterministic tests for the unchanged seed plus project-authored synthetic negative, boundary, and adversarial fixtures outside `dataset/`.
- A structured result that can accept a minimal-profile-valid source set while simultaneously reporting CARIN nonconformance and unverified terminology.

## Out of scope

- Full base FHIR R4 or CARIN conformance as an ingestion prerequisite.
- Payer-specific adjudication, benefit, coverage, medical-necessity, coding, fraud, payment, clinical, or policy semantics.
- Terminology expansion, inferred code membership, display validation, NCPDP content acquisition, live terminology/FHIR services, or network lookup.
- Normalization models, application APIs, persistence/quarantine, backend/frontend implementation, identity, hosted services, Docker topology, or deployment; PLATFORM-001 owns those concerns.
- Support for additional resources, profiles, Bundle types, narrative rendering, contained resources, attachments, modifier extensions, executable Bundle request/response content, or non-JSON formats.
- Editing `dataset/`, converting it into CARIN-conformant data, or using validator output to change source classification or domain meaning.

## Versioned contract artifacts

DATA-001 is a cross-component data contract under `contracts/fhir/data-001/`, not an HTTP API. Contract work must provide:

- `boundary.json` — compatibility version; exact resource/envelope rules; accepted profile markers; required and preserve-only path registries; exact observed extension/system registries; rejected content; reference rules; state/rule registries; precedence and canonical ordering;
- `packages.lock.json` — pinned CARIN diagnostic tooling/packages, checksums, publisher evidence, terminology limitations, and offline materialization;
- `validation-outcome.schema.json` — the exact result structure below;
- `source-manifest.json` and `data-card.json` — immutable source identities, approved synthetic local classification, provenance/license limitations, use restrictions, and benchmark-freeze status; and
- `README.md` — deterministic offline invocation, diagnostic/acceptance separation, and artifact relationships.

Independent fixtures and the reference harness remain under `tests/fixtures/fhir/data-001/` and `tests/data/`. `contracts/openapi.yaml` remains unchanged.

## Declared source set and immutable inventory

The validation unit is the complete declared source set, so required references can resolve across files. The initial manifest contains these unchanged artifacts and source-lineage commit `3fda38143e95c58a91b54781b15c84bc8436a1fa`:

| Path | Bytes | SHA-256 | Git blob | Role |
|---|---:|---|---|---|
| `dataset/patient_bbuser29999.json` | 6,196 | `6fb43e72120e3a3cfb7bc756d0661eebcc0925a2bc994f60ecbf573813e3f58a` | `7ffe93441490616e32bd917774c4c5d86cc009d0` | standalone Patient |
| `dataset/coverage_bundle_bbuser29999.json` | 83,096 | `fef088d7c6df3fb33bc02a1e32be53a67db0815046b1e2d998d44cb1536ec33c` | `dd33f5708a9ff2c1286417b50b27544d36232f6b` | Coverage searchset, four entries |
| `dataset/eob_bundle_bbuser29999.json` | 288,342 | `d48c12a8d94e331c786f3876ea94df4356209c216c54392346dae87f84fc34f0` | `2d6544059ea695946849199c1ec2daa9b28517d2` | pharmacy EOB searchset, ten of reported total 146 |
| `dataset/readme.txt` | 335 | `5c5c7641a7dbb1c5c21864e429390f7021d303fef5ad8eabacd01b805e205fe8` | `e123e526d2c29925c6faf175b0b9e24e7965919a` | provenance description; not parsed as FHIR |

Source paths must be unique, normalized repository-relative paths with no traversal; hashes and byte counts must match the manifest. No implicit file discovery or remote fetch is allowed. The source classification gate accepts only explicitly registered `approved-synthetic-local` or `project-authored-synthetic` input. Missing, unknown, prohibited, real-PHI, production, or merely content-inferred classification is rejected.

## Minimal support matrix

| Input | Required project fields/rules | Preserved but not semantically interpreted | Rejected initially |
|---|---|---|---|
| Declared source set | manifest/version/classification; unique paths, hashes, and `(resourceType,id)` identities; the required Patient/Coverage/EOB reference graph resolves exactly once | provenance/license limitations and CARIN diagnostic evidence | undeclared files, traversal, duplicate identities, prohibited/unknown classification, remote discovery |
| Standalone Patient | `resourceType=Patient`; non-empty `id`; exactly one supported Patient profile marker; non-empty `identifier`; non-empty `name`; valid JSON types | birth/death, gender, address, observed non-modifier extensions and codings | other standalone resource types; missing anchor fields; unknown extra profile marker; modifier/contained/narrative/attachment content |
| Coverage Bundle | `resourceType=Bundle`; `type=searchset`; non-empty homogeneous entries; each entry contains Coverage with non-empty `id`, supported profile marker, `status`, `type`, and `beneficiary.reference`; `total` is a non-negative integer not smaller than entry count | Bundle `id`, `link`, `total`, entry search metadata; missing `entry.fullUrl`; Coverage identifier, period, relationship, subscriber, payor/class, observed extensions/codings | mixed/empty Bundle; other Bundle type; request/response; unsupported entry resource; invalid required reference |
| Pharmacy EOB Bundle | same searchset rules; each entry contains ExplanationOfBenefit with non-empty `id`, supported pharmacy marker, `status`, `type`, `use`, `patient.reference`, non-empty `insurance` with `coverage.reference`, and non-empty `item` | identifier, dates/period, insurer/provider/facility, outcome, care team, supporting info, payment/adjudication amounts, observed extensions/codings | mixed/empty Bundle; other EOB/profile; missing anchors; invalid required Patient/Coverage reference; executable or active content |

Supported profile markers are routing assertions only, not conformance claims. For each resource type, `meta.profile` must contain exactly one of the observed unversioned canonical or the same canonical qualified with `|2.2.0`:

- `http://hl7.org/fhir/us/carin-bb/StructureDefinition/C4BB-Patient`
- `http://hl7.org/fhir/us/carin-bb/StructureDefinition/C4BB-Coverage`
- `http://hl7.org/fhir/us/carin-bb/StructureDefinition/C4BB-ExplanationOfBenefit-Pharmacy`

`Bundle.entry.fullUrl` is optional in the compatibility profile. If present, it is inert, must be syntactically a string, and is never dereferenced. `Bundle.total` is paging metadata and need not equal the page entry count.

## Paths, extensions, references, and content isolation

`boundary.json` must enumerate every accepted path and every exact extension/system URI observed in the immutable seed; prefix or wildcard acceptance is prohibited. Paths are classified as `required`, `preserve-opaque`, or `rejected`. A new path, extension, system, resource, or profile is rejected until a reviewed contract version adds it.

Observed non-modifier extensions and coding values are preserved byte-for-byte as opaque data. Their URLs, systems, codes, displays, and values do not configure the application and do not establish meaning. `modifierExtension`, `contained`, narrative `text`, attachments/base64 payloads, Bundle request/response, and any undeclared active-content surface are rejected.

Required reference rules are exact:

- every Coverage `beneficiary.reference` resolves to exactly one declared `Patient/{id}`;
- every EOB `patient.reference` resolves to exactly one declared `Patient/{id}`;
- every EOB `insurance[*].coverage.reference` resolves to exactly one declared `Coverage/{id}`;
- required references must be same-source-set relative references of the expected type and cannot be absolute, remote, fragment, identifier-only, traversal, or ambiguous; and
- all other profile-shaped references are preserve-opaque only and are never resolved, fetched, or treated as authoritative evidence.

Narratives, displays, identifiers, extensions, source text, profile markers, URLs, and validator messages are untrusted. The harness must not render, execute, follow, interpolate into commands, or include their raw values in normalized log messages. Lossless raw diagnostic output may be retained only as a separately identified untrusted artifact referenced by digest; normalized findings use sanitized templates and JSON pointers.

## Validation layers and exact outcomes

Project validation runs before advisory diagnostics:

1. source manifest, immutable identity, classification, and use boundary;
2. strict UTF-8 JSON syntax, duplicate-key rejection, top-level object, and no repair/coercion;
3. supported envelope/resource/profile-marker and exact path/extension/system registry;
4. required anchor fields and primitive/container types;
5. unique identities and required cross-file references; and
6. content-isolation/rejected-surface checks.

The machine result contains `decision`, an ordered unique `states` array, completed layer results, ordered project findings, CARIN diagnostic evidence, terminology evidence, and all relevant contract/source/tool digests.

Allowed states and semantics are exact:

- `minimal-profile-valid` — all six project layers passed. This is the only state that authorizes `decision=accepted`.
- `carin-no-errors-reported` — additive diagnostic state: the pinned CARIN run completed with no `error`/`fatal`. The wording deliberately does not claim conformance.
- `carin-nonconformant` — additive diagnostic state: the pinned CARIN run completed with at least one `error`/`fatal`. It never changes an accepted minimal decision.
- `carin-diagnostic-unavailable` — additive diagnostic state: pinned diagnostic evidence could not run or its digest/control failed. It does not change an input decision, but it fails the DATA-001 verification procedure until restored.
- `terminology-unverified` — additive diagnostic state: at least one accepted opaque code/extension system lacks approved offline membership/meaning evidence. It never changes minimal acceptance and must carry the affected JSON pointers and system identifiers without asserting meaning.
- `rejected` — one or more project layers failed. It is mutually exclusive with every other state; CARIN diagnostics are not run for rejected input.

Canonical ordering is `minimal-profile-valid`, then exactly one CARIN diagnostic state, then optional `terminology-unverified`. Accepted results have `decision=accepted`, begin with `minimal-profile-valid`, and never contain `rejected`. Rejected results have `decision=rejected` and `states=["rejected"]` exactly. The unchanged seed is expected to produce:

```json
{
  "decision": "accepted",
  "states": [
    "minimal-profile-valid",
    "carin-nonconformant",
    "terminology-unverified"
  ]
}
```

Each finding includes a stable `rule_id`, layer/source (`project`, `carin`, or `terminology`), original severity when applicable, sanitized machine code/message, source path, and JSON pointer. Required project rule families include `SOURCE-MANIFEST-001`, `DATA-CLASS-001`, `JSON-SYNTAX-001`, `FHIR-COMPAT-ENVELOPE-001`, `FHIR-COMPAT-RESOURCE-001`, `FHIR-COMPAT-PROFILE-MARKER-001`, `FHIR-COMPAT-REQUIRED-001`, `FHIR-COMPAT-ID-001`, `FHIR-COMPAT-REF-001`, `FHIR-COMPAT-CONTENT-001`, `CARIN-DIAGNOSTIC-001`, and `TERM-UNVERIFIED-001`. Rule identifiers are never reused with changed meanings.

## CARIN and terminology diagnostic policy

CARIN diagnostics use the exact checksum-pinned 2.2.0 package, dependency closure, Validator CLI 6.10.2, `-no-http-access`, and `-tx n/a`. Validator/package availability remains required verification evidence even though its findings are advisory for ingestion. The result records the tool/package-lock digest, raw OperationOutcome digest, counts by original severity, and normalized lossless finding references.

CARIN diagnostics may identify missing version-qualified profiles, member-id slices, unknown CMS extensions, missing Bundle fullUrls, EOB slices, or terminology issues. Those findings are never hidden, rewritten, or converted into project semantics. UI/API wording in later tasks must call them diagnostics and must not label a minimal-profile-valid resource CARIN-conformant.

NCPDP and other unavailable terminology remains opaque/unverified. No live terminology call, substitute package, guessed code list, display-text inference, or publisher-QA severity override is permitted. Even a CARIN diagnostic with no errors does not establish project-approved terminology or domain correctness.

## Provenance, testing, and trust gates

- Re-hash all four seed artifacts before and after every test run and require zero byte changes.
- Keep original, diagnostic, normalized, derived, and human-authored artifacts distinguishable by source/digest/version.
- Retain the seed's approved synthetic local-development classification, while acquisition, generator, upstream release, chain of custody, license/redistribution, and benchmark fitness remain explicitly limited/unverified as already recorded.
- Store every project-authored fixture outside `dataset/` with `project-authored-synthetic` classification, parent hashes, deterministic recipe/version, expected states/rule IDs, author/reviewer state, intended use, and limitations.
- Test accepted seed behavior; every rejected layer; broken/cross-type/remote/ambiguous references; duplicate keys/IDs; wrong resources/profiles/Bundle types; unknown paths/extensions; modifier/narrative/attachment/instruction content; terminology-unverified behavior; CARIN error preservation; diagnostic unavailability; outcome ordering/exclusivity; sanitized logging; and dataset byte identity.
- Run without network, cloud/model credentials, production access, a FHIR server, or a live terminology service.

No validation outcome establishes coverage, payment, coding, fraud, clinical, policy, provider, beneficiary, amount, or real-world correctness. Human authority and downstream governance remain unchanged.

## Acceptance criteria

- `boundary.json` and the human-readable matrix consistently define the project compatibility profile, exact registries, required references, rejected surfaces, stable rules, and ordered state model.
- The unchanged seed passes the project layers and produces `minimal-profile-valid`, `carin-nonconformant`, and `terminology-unverified` while preserving all CARIN findings and opaque terminology evidence.
- Project-rule failure always produces only `decision=rejected` and `states=["rejected"]`; no CARIN diagnostic can override it.
- CARIN diagnostics never decide project acceptance and never produce a CARIN-conformance claim; unavailable diagnostic tooling fails verification rather than silently disappearing.
- Synthetic classification and prohibited-data gates remain fail-closed. Provenance/license gaps remain benchmark-freeze/distribution limitations without rewriting the approved local synthetic classification.
- The independent offline harness covers all positive/negative/adversarial behavior and proves the four root artifacts remain byte-identical.
- No application API, persistence schema, backend/frontend feature, deployment resource, live service, invented terminology, or domain semantics are introduced.

## Change control and downstream handoff

The compatibility boundary uses semantic versioning. Adding a resource/profile/envelope, weakening a rejection/classification/reference/content rule, changing required fields, changing state semantics, or treating a diagnostic as acceptance requires a major version plus architecture/contract/security review. Backward-compatible preserve-only registry additions require a minor version. Documentation-only clarification with identical machine behavior may be a patch.

Any source byte, manifest/classification, boundary, package/tool, diagnostic normalization, fixture, or recipe change updates its digest and reruns the full suite. PLATFORM-001 may later consume only the completed contract and must choose runtime parsing, normalized models, API behavior, size limits, quarantine persistence, authorization, and storage without collapsing minimal acceptance, CARIN diagnostics, terminology uncertainty, or raw provenance.

Architecture impact is limited to `contract_change=true` and `testing=true`; `database=false`, `backend=false`, `frontend=false`, and `infrastructure=false`. The orchestrator must reconcile stale strict-CARIN/negative-seed wording in task state before advancing, but the newly approved compatibility decision resolves the prior architecture blockers.
