# HARDEN-001 — Harden prompt isolation and dependency reproducibility

## Goal

Close the two accepted non-blocking DEMO-001 security findings without changing the local-demo product behavior: isolate fixed Gemini instructions from untrusted synthetic data at the SDK role boundary, and make Python dependency installation reproducible and subject to a required known-vulnerability audit.

## In scope

- Pass the fixed Gemini safety policy through `GenerateContentConfig.system_instruction` and send only a clearly labeled JSON data document through user `contents`.
- Preserve the existing combined 128 KiB request-input limit across the system instruction and user content.
- Add adversarial fake-client tests proving instruction/data role separation, no tool configuration, no environment-value disclosure, and unchanged zero-or-one-call behavior.
- Keep `requirements-agent.txt` as the human-reviewed direct dependency input and add the audit tool as an exact direct pin.
- Generate and commit one fully resolved Python 3.12-compatible requirements lock with SHA-256 artifact hashes for application, test, agentic, and audit dependencies.
- Make CI install the hash-locked graph and run a required dependency audit that fails on unresolved applicable advisories or audit errors.
- Declare the dependency audit as a required project security check so local verification and CI use the same gate.
- Document the lock regeneration and audit commands in the dependency input manifest.

## Out of scope

- API request/response changes, deterministic-rule changes, additional Gemini calls, tools, retries, fallback models, or model-authority expansion.
- New frontend, database, persistence, authentication, deployment, real-PHI, production, clinical, coding, payment, coverage, fraud, or compliance behavior.
- Automatic dependency upgrades or ignored vulnerability identifiers. Any advisory must be resolved, or a separately approved exception must record applicability, compensating controls, and expiry.
- Implementing the follow-on frontend prototype task.

## Architecture impact

- Refines the existing Gemini adapter boundary and repository dependency/CI security controls only.
- Backend and testing are expected to be impacted; CI/tooling impact must be assessed as infrastructure impact by task architecture.
- Frontend and database remain disabled, and no new runtime component or trust boundary is introduced.

## Contract impact

- No public API contract change is expected. `contracts/openapi.yaml` remains authoritative and must validate unchanged.

## Security considerations

- Untrusted FHIR-derived strings must not share the model instruction role.
- System instructions must contain only fixed project-owned policy; runtime credentials and private configuration must remain absent from both instruction and user content.
- The audit must inspect the committed, fully pinned, hash-bearing graph and fail closed on known applicable advisories or audit errors.
- Hash locking improves artifact integrity and repeatability but does not prove package safety or replace source review.

## Dependencies

- `DEMO-001` (`DONE`) supplies the approved Gemini boundary, tests, direct dependency manifests, and CI workflows being hardened.
- No dependency on cancelled `DATA-001`, its historical FHIR contracts, a frontend, or a database.

## Acceptance criteria

1. The Google Gen AI SDK request places the fixed safety policy in `system_instruction`, while `contents` contains only the labeled serialized synthetic payload and never duplicates the policy.
2. The existing one-call/no-tools, structured-output, evidence-validation, sanitized-failure, deterministic-fallback, timeout, output-token, and response-size guarantees remain unchanged.
3. The 128 KiB input boundary accounts for both the fixed system instruction and user content and still makes zero provider calls when exceeded.
4. Tests include an adversarial instruction-like dataset value and prove it remains user data, the fixed instruction remains project-owned, no environment value is sent, and no tools are configured.
5. A committed lock file pins the complete resolved Python dependency graph and supplies SHA-256 hashes accepted by `pip --require-hashes` on Python 3.12.
6. CI installs from the lock file rather than resolving the ranged/direct manifests during verification.
7. A required project security check runs a pinned dependency-audit tool against the hashed lock, fails on known applicable advisories or audit errors, and requires no application credentials.
8. Project validation, task/report validation, OpenAPI validation, all backend and agentic tests, dependency consistency, hash-enforced clean installation, dependency audit, secret baseline, and source-dataset immutability checks pass.
9. No public API, frontend, database, dataset, or product-scope behavior changes.
