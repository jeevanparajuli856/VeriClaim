# VeriClaim System Architecture

> Status: **Inception draft**. This document defines confirmed architecture constraints, a provider-neutral logical architecture, recommendations, and unresolved decisions. A recommendation is not an approved implementation choice.

## 1. System context

VeriClaim is a governed healthcare payment-integrity research and decision-support platform. It accepts approved synthetic healthcare claims, validates and normalizes supported data, calculates risk signals, gathers evidence, retrieves relevant policy material, synthesizes an investigation, applies governance checks, and presents the result to a human analyst. It also supports controlled experiments comparing single-model, RAG, multi-agent, and governed multi-agent variants.

Primary human actors are payment-integrity analysts and project researchers/evaluators. Governance reviewers, operators, and administrators are recommended roles pending approval of the user and deployment model.

The system is not an adjudication, payment, fraud-determination, diagnosis, or clinical decision system. See `docs/adr/ADR-0001-human-authority-over-claim-outcomes.md`.

## 2. Architecture status and decision classes

### Confirmed constraints

- Human authority over consequential claim and clinical outcomes.
- Synthetic/public data initially; no real PHI or production claims.
- FHIR must be evaluated as the primary healthcare interoperability standard.
- Structured risk output, evidence grounding, citations, governance, traceability, and reproducible evaluation are required.
- Agent and tool autonomy must be explicitly bounded.
- Retrieved content, model output, tool output, and client input are untrusted.
- No vendor or technology is selected merely because it was listed as a candidate.

### Recommended architecture direction

- A narrow vertical slice implemented as a modular monolith with explicit internal component boundaries.
- A deterministic investigation state machine coordinating typed specialist capabilities.
- A shared investigation interface for research variants A–E.
- PostgreSQL plus pgvector and full-text retrieval for initial persistence and hybrid search.
- Local Docker-based development before a cloud provider is selected.
- Standards-based OIDC, deny-by-default RBAC, and per-object authorization.
- OpenTelemetry-compatible traces, metrics, and logs.

### Open architecture decisions

- Enabled deployable components and their technologies.
- Exact FHIR resource/profile and terminology support.
- Dataset and policy corpus selection.
- Model, embedding, and reranking providers/models.
- Identity provider and local authentication approach.
- Database hosting and any future cloud platform.
- Agent framework, if any; tool execution isolation; memory and retry limits.
- Evaluation thresholds, retention, capacity, latency, availability, and cost budgets.

## 3. Safety and authority invariants

These constraints apply regardless of implementation technology:

1. A model score or agent finding can change investigation priority or request evidence, but cannot change claim/payment status.
2. Only authorized human actions can record a consequential disposition; external downstream action is outside the initial system.
3. Policy-dependent claims require traceable source evidence and an applicable source context.
4. Missing evidence, invalid citations, failed authorization, failed schema checks, or governance rejection prevents analyst-ready status.
5. Agents cannot modify system prompts, grant permissions, change budgets, select unapproved providers, or create unrestricted tools.
6. Source facts, normalized values, derived features, retrieved passages, generated synthesis, and human decisions remain distinguishable.
7. All initial healthcare data remains inside the approved synthetic/public boundary.

## 4. Logical component model

The following are logical responsibilities, not approved deployable services.

```text
Human analyst / researcher / operator
                |
                v
      Analyst and research interface
                |
         authenticated API boundary
                |
                v
        Case and access service
                |
                v
   Investigation workflow controller
      |        |        |        |
      v        v        v        v
  FHIR/data   Risk    Retrieval  Governance
  processing analysis  service    gate
      |        |        |        |
      +--------+----+---+--------+
                    |
                    v
        Evidence and trace recorder
                    |
       +------------+-------------+
       v                          v
 operational/evaluation data   policy/vector index
                    |
                    v
      approved external providers/sources
```

### 4.1 Analyst and research interface

Classification: **Recommended; frontend enablement and framework are open.**

Responsibilities:

- Authenticate the user through the approved identity flow.
- Display claim/source data, risk signals, evidence, citations, uncertainty, governance results, agent actions, and audit history without collapsing their provenance.
- Capture human findings, rationale, feedback, and requests for further investigation.
- Provide research/evaluation controls only to authorized roles.
- Avoid storing secrets or enforcing authorization solely in browser state.

Recommendation: a minimal TypeScript/Next.js interface for the first vertical slice, with WCAG 2.2 AA as the target. Neither choice is approved.

### 4.2 Case and access service

Classification: **Logical capability confirmed; backend technology open.**

Responsibilities:

- Expose versioned, explicitly contracted interfaces.
- Authenticate requests and enforce role, action, and object-level authorization server-side.
- Manage case state without treating agent/model output as authority.
- Validate request/output schemas and mediate access to data, investigations, reviews, and exports.
- Apply idempotency, concurrency control, rate limits, and safe error handling where required.

Recommendation: Python with FastAPI and Pydantic in a modular monolith. No API contract exists yet and none should be inferred from this document.

### 4.3 FHIR/data processing

Classification: **Capability confirmed; exact profile open.**

Responsibilities:

- Register source, license, generator, dataset version, and synthetic/public classification.
- Preserve the original accepted payload and validate it against the approved FHIR R4/profile rules.
- Normalize only explicitly mapped fields and record transformations/errors.
- Produce versioned features and evidence references for risk and investigation components.
- Reject unsupported resources, ambiguous semantics, invalid references, and prohibited data classes safely.

Recommendation: initially profile a minimal set selected from Patient, Coverage, Claim, ExplanationOfBenefit, Organization, and Practitioner. Evaluate DocumentReference for evidence and Provenance/AuditEvent for interoperable trace summaries. Do not assume every listed resource is required.

### 4.4 Risk analysis

Classification: **Capability confirmed; algorithms and labels open.**

Responsibilities:

- Compute deterministic validation and anomaly signals.
- Run an approved, pinned model on an approved versioned feature set.
- Return a structured risk score/level, named signals, feature/model version, confidence/limitations, and supporting evidence references.
- Never return or imply a final coverage, fraud, payment, clinical, or coding decision.
- Support repeatable offline evaluation and drift/error analysis.

Recommendation: start with transparent rules/statistical baselines and interpretable scikit-learn models. Treat duplicate, temporal, amount, frequency, provider, diagnosis/procedure, specialty, and reimbursement signals as hypotheses until the benchmark defines their semantics.

### 4.5 Policy ingestion and retrieval

Classification: **Capability confirmed; sources, storage, and models open.**

Responsibilities:

- Acquire only approved documents and preserve source URI/identifier, publisher, jurisdiction, document type, version, effective dates, retrieval time, content hash, and license/usage metadata.
- Treat documents as untrusted; separate content from instructions and scan/test for injection and poisoning conditions.
- Apply versioned parsing/chunking and retain a path from a chunk to its source context.
- Support metadata filters and evaluate lexical, semantic, hybrid, and reranked retrieval under the same corpus/version.
- Return evidence with stable citations and applicability metadata; retrieval does not establish policy interpretation by itself.

Recommendation: PostgreSQL full-text search plus pgvector for the first hybrid baseline. Dedicated vector infrastructure is not justified until measured scale or retrieval requirements demand it.

### 4.6 Investigation workflow controller

Classification: **Agentic capability confirmed; orchestration design open.**

Responsibilities:

- Create an explicit plan/state transition record for the selected experimental variant.
- Invoke only registered, typed, authorized tools with bounded retries, time, tokens, cost, and result sizes.
- Correlate risk signals, claim/provider history exposed through approved tools, and policy evidence.
- Produce a structured report that distinguishes evidence from synthesis and includes uncertainty and missing evidence.
- Route failed, incomplete, contradictory, or unsafe work to an explicit stopped/escalated state.

Recommendation: use a deterministic state machine with a coordinator and logical specialist roles (data intake, risk, policy retrieval, investigation, governance, audit). Start with logical roles inside one security boundary; split services or processes only for proven isolation or scaling needs.

No framework is approved. Framework selection must be based on resumability, state persistence, typed tools, testability, observability, failure handling, provider portability, and permission enforcement—not on the ability to produce more autonomous dialogue.

### 4.7 Governance gate

Classification: **Confirmed architecture boundary; detailed policy open.**

Responsibilities:

- Verify report schema, required evidence, citation resolution/applicability, source-to-claim attribution, and confidence/escalation rules.
- Detect or limit unsupported claims, prompt injection, indirect injection, retrieval poisoning, sensitive-data leakage, unauthorized tool use, excessive loops, and budget violations.
- Record prompt/model/tool/corpus/governance-policy versions and the reasons for pass, reject, or escalate.
- Prevent failed output from becoming analyst-ready.
- Keep deterministic safety controls separate from model-based judges and record which type produced each result.

Recommendation: use NIST AI RMF as organizing vocabulary and OWASP guidance as threat input without claiming certification. Governance thresholds require benchmark evidence and human approval.

### 4.8 Evidence, audit, and evaluation

Classification: **Confirmed capability; physical schema and storage open.**

Responsibilities:

- Assign trace, case, execution, model invocation, tool call, retrieval, evidence, governance result, and human-review identifiers.
- Record timestamps, actor/role, model and prompt versions, tool name/version, authorized typed input (redacted as required), result reference/hash/status, retrieved documents/chunks, confidence, budgets, state transitions, and human disposition.
- Prefer append-only event semantics and make corrections explicit rather than silently rewriting history.
- Store experiment configuration, corpus/fixture versions, random seeds where applicable, metrics, failures, latency, token use, and estimated cost.
- Enforce role-based access, retention, minimization, and export policy for detailed traces.

FHIR Provenance and AuditEvent should be evaluated as healthcare-facing representations. They are not assumed to capture all AI trajectory or evaluation details, so the canonical internal trace model remains an open design.

## 5. Investigation lifecycle

Recommended state model (not an approved API or persistence schema):

```text
RECEIVED
   |
   v
VALIDATING --invalid/prohibited--> REJECTED
   |
   v
RISK_ASSESSED
   |
   v
INVESTIGATING --insufficient/tool failure--> ESCALATED
   |
   v
GOVERNANCE_CHECK
   | pass                         | fail/uncertain
   v                              v
READY_FOR_HUMAN_REVIEW         ESCALATED
   |
   +--> HUMAN_FINDING_RECORDED
   +--> MORE_RESEARCH_REQUESTED --> INVESTIGATING
```

The state names and transitions are recommendations. A human finding does not imply a claim-system adjudication.

## 6. Principal data flow

```text
Approved synthetic/public source
        |
        v
source registration + data classification
        |
        v
FHIR/profile validation --failure--> quarantined/rejected record + trace
        |
        v
immutable source reference + normalized representation
        |
        +--> versioned feature extraction --> structured risk assessment
        |
        +--> authorized evidence queries
        |
        +--> policy retrieval --> cited passages + applicability metadata
                                  |
                                  v
                         structured synthesis
                                  |
                                  v
                    deterministic/model governance checks
                           | pass            | fail
                           v                 v
                    analyst-ready case    escalation record
                           |
                           v
                   human finding/feedback
                           |
                           v
                  audit + evaluation records
```

Every derived artifact should reference its input/source and transformation or model version. The detailed schema belongs in later approved contracts and database design.

## 7. Data strategy

### Confirmed

- Synthetic, project-authored, or approved public data only during the initial project phase.
- No real PHI or production claims.
- Original, normalized, derived, retrieved, generated, and human-authored data remain distinguishable.
- Dataset, transformation, benchmark, and corpus versions must be recorded.

### Recommended

- Use Synthea as the first clinical-record generator candidate and evaluate whether its claim/EOB output supports chosen scenarios.
- Add controlled, documented perturbations for known anomaly scenarios rather than pretending naturally occurring synthetic labels are ground truth.
- Evaluate CMS Blue Button sandbox/synthetic data as a supplemental compatibility dataset.
- Maintain an explicit data card for each dataset and benchmark covering origin, license, schema/profile, generation, perturbations, limitations, splits, leakage controls, and intended use.
- Keep test, development, and benchmark data logically separated; freeze evaluation sets and prevent retrieval/training leakage.

### Open

- Initial line of business, claim scenarios, FHIR packages/profiles, terminology services, volume, and refresh policy.
- Whether attachments or DocumentReference content are in the first milestone.
- Retention/deletion policy and whether reviewer identifiers are pseudonymous in research exports.

## 8. Trust boundaries and threat assumptions

| Boundary | Untrusted input / risk | Required control direction |
|---|---|---|
| Browser to API | Tampered requests, XSS/CSRF, token theft, object access | Authenticated transport, server-side schema/authz, secure sessions, output encoding, object-level checks |
| Identity provider to application | Forged/mis-scoped claims, stale roles | Validate issuer/audience/signature/time; map roles explicitly; audit changes |
| Data ingestion | Malformed FHIR, prohibited data, oversized files, malicious narrative/attachments | Source allowlist, size/type limits, profile validation, classification gate, quarantine, content isolation |
| Workflow to tool broker | Prompt-directed unauthorized calls, excessive loops, unsafe parameters | Registered typed tools, per-call authorization, allowlists, budgets, idempotency, audit, cancellation |
| Retrieval corpus to model | Direct/indirect injection, poisoning, stale/inapplicable policy | Origin labels, instruction/data separation, corpus approval, version/date filters, adversarial testing, citation validation |
| Application to AI provider | Data leakage, retention/training, version drift, outage, cost | Minimize/redact context, approved endpoints/models/terms, pinned versions where possible, timeouts, budgets, fallback/escalation |
| Application to data store | Cross-user/tenant leakage, injection, tampering, trace rewriting | Parameterized access, encryption, least privilege, row/object policy as needed, integrity constraints, append-only semantics |
| Observability/export | Secret/PHI/prompt leakage, excessive retention | Structured redaction, access control, sampling policy, retention/deletion, export review |
| CI/supply chain | Malicious dependency/action/image | Pinning, lockfiles, provenance/scanning, least-privilege CI tokens, protected changes |

Tenant isolation is not yet a confirmed requirement. If multi-tenancy is approved, it becomes a first-class boundary requiring a specific authorization and data-isolation design.

## 9. Authentication and authorization

### Confirmed requirements

- Any multi-user analyst system requires authenticated identities and server-side authorization.
- Model reasoning cannot authorize an action.
- Tool use, source access, case access, review actions, configuration changes, and exports require explicit permissions.

### Recommendation

- Standards-based OIDC rather than custom password/authentication implementation.
- Deny-by-default roles initially scoped as analyst, governance reviewer, researcher, operator, and administrator, with combined roles only when explicitly granted.
- Object-level authorization for cases, datasets, corpora, experiments, and traces.
- Separate service credentials for workflow, retrieval, database, and provider access; no shared all-powerful agent credential.
- A local/test identity provider for development and an approved managed provider only when deployment context is known.

### Open decisions

- User population, organization/tenant model, identity provider, MFA/session requirements, role combinations, administrative workflow, and emergency access.

## 10. Agent and tool security architecture

### Permission model

- Agents receive capabilities for the current case and step, not ambient application credentials.
- Read-only data and retrieval operations are preferred.
- Initial agents have no external payment, messaging, case-management, or arbitrary network/file/shell tools.
- Each tool has a typed schema, maximum input/output size, timeout, retry/idempotency policy, authorized data classes, destination allowlist, and audit event.
- The workflow controller—not model text—selects permitted transitions and enforces cumulative budgets.

### Memory

- Case-scoped state and trace records are recommended.
- Cross-case agent memory is not approved.
- Reviewer feedback cannot automatically become trusted memory, policy, labels, or prompts without curation and versioning.

### Failure behavior

- Timeouts, provider errors, malformed tool results, citation mismatch, contradictory evidence, or exhausted budgets lead to retry within approved limits or escalation.
- No silent provider/model substitution in an evaluation run.
- Resumption must preserve the original execution configuration and avoid duplicating side effects.

## 11. Policy-grounded retrieval strategy

### Candidate pipeline

```text
approved source register
  -> fetch/import
  -> content hash + version/effective-date metadata
  -> parse and preserve structure
  -> injection/content checks
  -> versioned chunks
  -> lexical + semantic indexes
  -> metadata-filtered retrieval
  -> optional reranking
  -> citation/applicability validation
  -> evidence package
```

### Required evaluation separation

- Retrieval quality (whether relevant passages were found).
- Citation resolution (whether a citation maps to the exact source/version/passage).
- Citation entailment/groundedness (whether evidence supports the generated statement).
- Policy applicability (whether jurisdiction, effective date, benefit context, and surrounding policy make the passage relevant).

No model should be described as determining policy merely because retrieval returned similar text.

## 12. ML strategy

### Confirmed output boundary

Risk analysis produces structured research signals and uncertainty, not an adjudication or fraud conclusion.

### Recommended staged approach

1. Data-quality and deterministic baselines: duplicates, thresholds, temporal/frequency patterns, and cohort comparisons defined by the benchmark.
2. Interpretable statistical/ML baselines with strict train/validation/test separation.
3. Calibration, subgroup/error analysis, ablation, drift sensitivity, and false-positive investigation.
4. More complex boosted/deep/anomaly models only when they outperform meaningful baselines under approved metrics and remain explainable enough for the use case.

### Open decisions

- Labels and who validates them; supervised versus unsupervised/semi-supervised framing; feature windows; leakage prevention; cohort definitions; calibration; fairness/subgroup dimensions; thresholds; retraining and model registry.

Synthetic benchmark results must not be represented as real-world clinical, fraud, coverage, or payment accuracy.

## 13. Governance strategy

### Control layers

1. **Design-time:** threat model, approved data/providers/tools, prompt and policy versioning, least privilege, test corpus.
2. **Input-time:** identity, authorization, data classification, schema validation, source allowlists, injection/content checks.
3. **Execution-time:** state-machine control, typed tools, budgets, context minimization, network/destination restrictions, trace capture.
4. **Output-time:** schema validation, evidence/citation checks, applicability checks, confidence/uncertainty requirements, sensitive-output scanning, pass/reject/escalate decision.
5. **Human-time:** clear provenance and limitations, authorized review, rationale, conflict/escalation path.
6. **Evaluation/operations:** versioned metrics, adversarial suites, monitoring, audit review, provider/model change control, incident response.

### Governance outcome

Each investigation should result in a structured governance outcome such as pass, reject, or human escalation, with rule/model versions and machine-readable reasons. The exact schema and thresholds are open.

### Frameworks

Recommendation: use NIST AI RMF as a non-certifying risk vocabulary and relevant OWASP LLM/GenAI guidance as threat input. Map concrete controls and evidence; do not equate framework use with compliance.

## 14. Evaluation and research architecture

### Required variants

- A: Single LLM.
- B: Single LLM plus RAG.
- C: Multi-agent.
- D: Multi-agent plus RAG.
- E: Multi-agent plus RAG plus governance.

The exact definition of “multi-agent,” prompts, models, available tools, and governance interventions must be frozen before a comparative run. Variants should use the same approved cases, evidence availability, output schema, and scoring rubric where scientifically appropriate.

### Metric families

- ML: precision, recall, F1, AUROC, false-positive rate, calibration, and subgroup/error analysis where justified.
- Retrieval: Recall@K, Precision@K, MRR, source relevance, citation resolution, and applicability.
- LLM/RAG: groundedness, unsupported-claim rate, factual consistency, and citation correctness.
- Agentic: task completion, tool-call correctness, unnecessary calls, trajectory conformance, recovery, latency, tokens, and estimated cost.
- Governance: unsafe-output detection, unsupported-output block rate, injection resistance, leakage/permission violations, and escalation rate.
- Human: reviewer agreement, false escalation, acceptance/rejection, time-on-case, and qualitative usability.

Metric definitions, gold labels, thresholds, confidence intervals, sample size, randomization, reviewer blinding, and model-judge use are open research-design decisions. Model-based evaluators must not be the sole source of truth for safety claims.

## 15. Persistence architecture

### Logical data domains

- Source registry and immutable source references.
- Normalized healthcare records and validation results.
- Feature/model registry and risk assessments.
- Policy documents, chunks, index metadata, and citations.
- Cases, workflow executions, evidence links, and structured reports.
- Governance policies/results and human reviews.
- Audit events, experiments, metrics, cost, and operational telemetry references.

### Recommendation

Use PostgreSQL as the primary transactional/research store, pgvector for semantic vectors, native full-text search for lexical retrieval, and Git-tracked migrations. Store large immutable document bodies in filesystem/object storage only if size and lifecycle requirements justify it, with hashes and metadata in the database.

### Open decisions

- Provider/hosting, migration path, row-level security versus service authorization split, tenant model, encryption/key ownership, object storage, backup/recovery, retention/deletion, vector dimension/model migrations, and audit immutability mechanism.

No live database configuration is authorized by this document.

## 16. Deployment and platform considerations

### Recommended initial topology

```text
local developer machine / isolated development host
  -> containerized UI (if approved)
  -> containerized application/workflow process
  -> local PostgreSQL/vector extension (if approved)
  -> approved external model endpoint only when configured
  -> local structured telemetry by default
```

This recommendation defers AWS/Azure and managed-service selection. It does not make Docker, a cloud, or a particular hosting provider an approved choice.

### Cloud-selection criteria for later approval

- Data classification, residency, provider contractual terms, and identity integration.
- Required isolation, network egress controls, encryption/key management, audit, backups, and recovery.
- Model availability and private-connectivity options.
- Team expertise, infrastructure-as-code support, observability, supply-chain controls, and CI/CD protections.
- Expected load and total cost, including database, vector search, object storage, telemetry, model tokens, embeddings, reranking, and network egress.

Production deployment is not in the initial approved scope.

## 17. Observability and audit

### Recommendation

Use OpenTelemetry-compatible identifiers and instrumentation so an investigation can be correlated across API, workflow, retrieval, model, tool, governance, and review operations. Keep operational telemetry distinct from the durable decision/audit record.

### Required dimensions

- Trace/case/execution identifiers and state transitions.
- Latency and failure counts by component, tool, model, retrieval stage, and governance rule.
- Token/input/output usage and estimated cost by case/variant/model.
- Dataset, corpus, model, prompt, tool, policy, and application versions.
- Authorization failures, injection detections, governance rejections/escalations, and provider outages.

### Privacy direction

- Default to metadata and references rather than full claim, document, prompt, or tool bodies in operational logs.
- Apply centralized redaction, access controls, retention, deletion, and export review.
- Do not send telemetry to an external backend until its provider and data terms are approved.

## 18. Security and privacy verification direction

Project-specific commands cannot be declared until technologies are approved. The eventual verification plan should include, where applicable:

- FHIR/profile fixture validation and prohibited-data checks.
- Unit, integration, contract, end-to-end, and benchmark reproducibility tests.
- Authorization/object-access tests for every role and tool.
- Prompt-injection, indirect-injection, retrieval-poisoning, citation, leakage, budget, and unsafe-tool test suites.
- Dependency, secret, static-analysis, container, and infrastructure scanning for the selected stack.
- Migration/reset tests, backup/restore evidence, and database policy/advisor checks for the selected provider.
- Accessibility testing for the analyst workflow.

These are requirements for later verification design, not invented commands in `.ai/project.json`.

## 19. Key failure modes and required response

| Failure mode | Required architecture response |
|---|---|
| Invalid/unsupported FHIR or prohibited data | Reject/quarantine, record validation result, do not continue investigation |
| Missing, stale, conflicting, or inapplicable policy | Mark uncertainty and escalate; never invent resolution |
| Citation does not support a statement | Fail governance for that statement/report until corrected or escalated |
| Prompt injection in source or tool output | Keep source as data, deny instruction effect, record detection, continue only if safe |
| Unauthorized tool or case access | Deny, audit, alert according to severity |
| Model/provider outage or malformed output | Bounded retry or explicit failure/escalation; no silent experimental substitution |
| Budget/time/recursion exhaustion | Stop execution and preserve partial evidence/trace for review |
| Model or corpus version drift | Block controlled comparison or start a newly versioned experiment |
| Human disagreement | Preserve each review and follow an approved adjudication/research protocol; do not auto-label |
| Suspected real PHI | Stop processing, quarantine access, follow an approved incident/data review process |

## 20. Architecture decisions requiring approval

The material approval package is maintained in `docs/PROJECT.md` section 17. The following groupings must be reconciled before `INCEPTION_READY`:

1. First-milestone scope and user workflow.
2. Backend/frontend/database enablement and technologies.
3. FHIR profiles and synthetic/public data sources.
4. Authentication, roles, tenant assumptions, and administrative authority.
5. Model/embedding/reranking provider, data terms, credentials, and budgets.
6. Agent orchestration, tool isolation, memory, and autonomous execution limits.
7. Policy sources, RAG/vector storage, and citation/applicability model.
8. ML framing, labels, validation claims, and thresholds.
9. Governance framework, fail-closed thresholds, retention, and escalation.
10. Initial deployment, observability, cloud deferral/selection, and cost ceilings.

No contracts or implementation tasks should be created until the operational project configuration can truthfully be marked `INCEPTION_READY`.

## 21. Approved decision records

- `docs/adr/ADR-0001-human-authority-over-claim-outcomes.md`
- `docs/adr/ADR-0002-synthetic-data-initial-boundary.md`
