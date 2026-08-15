# DATA-001 minimal FHIR R4 compatibility contract

This directory defines VeriClaim's initial project-owned FHIR R4 compatibility boundary. Passing it means only `minimal-profile-valid`; it does not mean full base FHIR R4 or CARIN Blue Button conformance.

## Acceptance and diagnostics

`boundary.json` is the acceptance authority. The validator first validates and sanitizes every source path against classification-specific roots, then checks the declared synthetic source set, strict finite-number JSON, supported Patient/Coverage/pharmacy-EOB shapes, required anchor fields, exact nested paths and JSON types from `shape-registry.json`, bounded input complexity, exact source registries, cross-file references, and rejected active-content surfaces. Approved local seed paths must match the manifest exactly; project-authored fixtures remain confined beneath `tests/fixtures/fhir/data-001/`.

CARIN Blue Button 2.2.0 is a separate advisory diagnostic. Its original errors and warnings are preserved as structured evidence and never override project acceptance or rejection. A minimal-profile-valid source with CARIN errors has these ordered states:

```json
[
  "minimal-profile-valid",
  "carin-nonconformant",
  "terminology-unverified"
]
```

Do not describe that result as CARIN-conformant. A no-error CARIN diagnostic is reported only as `carin-no-errors-reported`, which is intentionally not a conformance claim.

Terminology without usage-approved offline definitions remains opaque. The validator preserves each system URI and whether a code was present, marks it `terminology-unverified`, and performs no live lookup, substitution, inferred membership, or display inference. Such values can be displayed as untrusted source data and investigated by a human, but they cannot independently support coverage, payment, coding, fraud, clinical, or policy conclusions.

## Artifacts

- `boundary.json` — accepted source-set/resource/envelope rules, registry digests, reference policy, state ordering, stable rule IDs, and security invariants.
- `shape-registry.json` — exact role/path/type allowlist plus document, collection, string, key, and nesting limits.
- `packages.lock.json` — exact offline CARIN diagnostic package/tool closure, checksums, sources, licenses, and limitations.
- `validation-outcome.schema.json` — machine result contract separating the acceptance decision from CARIN and terminology evidence.
- `source-manifest.json` — exact paths, byte lengths, hashes, Git identities, classification, and expected result for the immutable seed.
- `data-card.json` — approved local use, provenance/license limitations, prohibited uses, and non-conformance statements.
- `tests/data/` and `tests/fixtures/fhir/data-001/` — independent reference validator, synthetic negative fixtures, expected diagnostics, and tests.

`contracts/openapi.yaml` is unchanged: DATA-001 defines no application API.

## Deterministic offline procedure

The independent test harness is the executable reference for this contract:

```bash
python -m pytest -q tests/data
```

It must run without network, cloud/model credentials, a FHIR server, production access, or a live terminology service. It re-hashes every root seed file before and after validation and rejects any mutation.

The advisory CARIN evidence uses the task-local ignored artifacts pinned in `packages.lock.json`:

```bash
contracts/fhir/data-001/.offline/tooling/jre-21.0.12+8/bin/java \
  -Duser.home=<isolated-task-cache> \
  -jar contracts/fhir/data-001/.offline/tooling/validator_cli-6.10.2.jar \
  dataset/patient_bbuser29999.json \
  dataset/coverage_bundle_bbuser29999.json \
  dataset/eob_bundle_bbuser29999.json \
  -version 4.0 \
  -ig hl7.fhir.us.carin-bb#2.2.0 \
  -no-http-access \
  -tx n/a \
  -output <untrusted-operation-outcome.json>
```

Before use, materialize every exact archive into the isolated cache and verify every checksum from `packages.lock.json`. The diagnostic must fail visibly as `carin-diagnostic-unavailable` if the validator, package cache, checksum, or network-denial control is unavailable. Never fall back to `latest`, a live terminology service, another CARIN version, or an unapproved terminology package.

Raw OperationOutcome content is untrusted. Retain it by digest outside normalized logs; normalized findings are derived issue-by-issue from the checksum-verified raw evidence and use stable rule IDs, sanitized machine codes, source paths, JSON pointers where safely derivable, and a digest of each complete source issue. Tool, runtime, and every locked package archive must also be checksum-verified. Missing or mismatched evidence is reported as `carin-diagnostic-unavailable`. The task verification gate requires the diagnostic to be available even though its findings do not decide input acceptance.

Every outcome carries both the declared source-set digest and a separately calculated digest of the bytes actually observed. Rejected or tampered input therefore retains distinct observed provenance even when its declared identity is unchanged.

## Change control

A new resource/profile/envelope, weaker rejection/classification/reference/content rule, changed required field, changed state meaning, or diagnostic-to-acceptance promotion requires a major contract version plus architecture, contract, test, security, and final review. A new preserve-only path or registry entry requires a reviewed minor version. Documentation-only clarification with identical behavior may be a patch.

Never edit `dataset/`, invent missing healthcare semantics, upload FHIR records, access production, or transfer consequential authority away from a human.
