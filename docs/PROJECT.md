# VeriClaim Project Definition

> This document is the product source of truth for project purpose, users, scope, constraints, assumptions, recommendations, unresolved decisions, and the proposed backlog.
>
> Classification labels:
> - **Confirmed** — explicitly established by the project sponsor
> - **Assumption** — a temporary belief that must be validated
> - **Recommendation** — a proposed choice awaiting approval where material
> - **Open question** — an unresolved choice that must not be treated as decided

## 1. Project Summary

### Working name

VeriClaim

### One-sentence description

VeriClaim is a governed Agentic AI research and decision-support platform that helps human healthcare payment-integrity analysts investigate synthetic claims by combining structured healthcare data, risk signals, policy-grounded evidence, bounded AI workflows, governance checks, and auditable human review.

### Status

Inception draft. The product and safety boundaries are established, but material scope, stack, provider, data, security, and deployment choices remain subject to approval.

---

## 2. Problem Statement

### Confirmed

- Healthcare payment-integrity investigation requires analysts to correlate structured claim data, historical patterns, policy material, and supporting evidence.
- The project will explore whether AI agents can assist that research while keeping conclusions grounded, traceable, governed, and subject to human judgment.
- The system is decision support, not an autonomous claims adjudicator, denial engine, clinical system, or diagnostic tool.
- Initial development should use synthetic or appropriate public data and should not require real protected health information (PHI).

### Assumptions

- A focused demonstration using synthetic claims can provide meaningful evidence about the comparative value and risk of agentic workflows.
- Human analysts benefit from a consolidated case view containing risk signals, evidence, citations, AI actions, and governance results.
- Public policy documents can be used for research if their source, jurisdiction, version/effective date, and retrieval time are preserved.
- Useful research can begin without production payer integrations, real payment actions, or real patient data.

---

## 3. Goals and Intended Outcomes

### Primary goal

Evaluate and demonstrate how governed Agentic AI can safely support healthcare payment-integrity research without transferring consequential claim decisions away from humans.

### Secondary goals

- Produce structured, explainable claim-risk assessments that are clearly separated from final decisions.
- Retrieve and cite policy evidence before presenting policy-dependent findings.
- Make significant model, agent, retrieval, tool, governance, and reviewer actions traceable.
- Support reproducible comparison of non-agentic, RAG, agentic, and governed-agentic approaches.
- Demonstrate sound healthcare interoperability, ML, retrieval, security, privacy, observability, and software-engineering practices.
- Capture analyst feedback and outcomes for evaluation without treating feedback as an automatically trusted label.

### Non-goals

- Autonomous approval, denial, adjudication, payment modification, recoupment, or provider sanction.
- Medical diagnosis, treatment recommendation, prescribing, or autonomous clinical decision-making.
- Representing the project as HIPAA compliant or production-ready without independent evidence and an explicitly approved regulated-data program.
- Initial use of real PHI, production claims, or production payer/provider systems.
- Treating an anomaly score, language-model output, or retrieved policy passage as proof of fraud, abuse, waste, or non-coverage.
- Replacing legal, clinical, coding, policy, or payment-integrity expertise.

---

## 4. Intended Users and Actors

| Classification | Actor / user | Need | Expected interaction |
|---|---|---|---|
| Confirmed | Human payment-integrity analyst | Efficiently inspect a flagged claim and supporting evidence | Reviews the case, evidence, citations, confidence, and trace; confirms or rejects a finding, requests more research, and records rationale |
| Confirmed | Project researcher/evaluator | Compare system architectures reproducibly | Runs controlled experiments and analyzes quality, safety, latency, token, and cost metrics |
| Recommended | Governance reviewer | Assess unsafe, unsupported, or policy-nonconforming output | Reviews escalations, governance results, versions, and aggregate safety metrics |
| Recommended | System operator | Run and observe the research platform | Manages approved configuration, synthetic datasets, policy corpora, models, and operational health |
| Open question | Administrator | Manage identities, roles, sources, and configuration | Exact administrative authority and workflow depend on the approved authentication and deployment model |

AI agents, ML models, and external providers are system actors, not accountable decision-makers.

---

## 5. Core Use Cases

### Confirmed

1. **Investigate a synthetic claim** — validate and normalize supported data, calculate structured risk signals, gather relevant evidence, retrieve policy material, run governance checks, and present a case to a human analyst.
2. **Review a case** — inspect original data, transformations, risk signals, cited sources, AI-generated findings, governance status, and action history before recording a human disposition.
3. **Audit an investigation** — reconstruct significant model, prompt, retrieval, tool, governance, and human-review activity using a stable trace identifier.
4. **Evaluate system variants** — compare at least the conceptual variants: single LLM, single LLM plus RAG, multi-agent, multi-agent plus RAG, and multi-agent plus RAG plus governance.

### Recommended for the first demonstration

1. **Ingest a bounded synthetic corpus** — import a deliberately small, versioned FHIR R4 dataset and reject malformed or unsupported inputs.
2. **Score transparent risk signals** — combine deterministic/heuristic baselines with an interpretable ML baseline and retain feature-level explanations.
3. **Research a bounded policy corpus** — retrieve versioned public or project-authored policy passages through lexical and semantic search and preserve citations.
4. **Escalate ungrounded output** — block a report from analyst-ready status when required citations, provenance, confidence, or safety checks fail.

---

## 6. Core Capabilities

### Confirmed

- Synthetic healthcare claim and related-data handling, with FHIR evaluated as the primary interoperability standard.
- Structured risk assessment that recommends investigation priority but does not decide claim outcomes.
- Evidence and policy retrieval with source citations and traceability.
- Bounded AI-assisted investigation with human oversight.
- Governance controls for unsupported conclusions, injection, leakage, excessive autonomy, tool permissions, versioning, escalation, and auditability.
- Human review and recorded feedback.
- Reproducible evaluation across ML, retrieval, LLM/RAG, agentic, governance, human-review, latency, and cost dimensions.

### Recommended / proposed

- A narrow end-to-end vertical slice before broader payer, policy, FHIR, model, or deployment coverage.
- A single deployable application with clearly separated modules before considering independently deployed microservices.
- A deterministic workflow/state machine that invokes bounded specialist capabilities rather than unconstrained agent-to-agent delegation.
- A common investigation contract and evaluation harness shared by all research variants.
- Hybrid lexical and semantic retrieval with source/version metadata and a post-retrieval evidence-validation stage.
- An explicit governance gate between generated investigation findings and analyst-ready presentation.

---

## 7. Scope

### Confirmed inception scope

- Define product, safety, privacy, traceability, research, and human-authority boundaries.
- Evaluate synthetic/public healthcare data sources and a minimal FHIR R4 resource profile.
- Define a research path for risk analysis, policy retrieval, AI-assisted investigation, governance, audit, and human review.
- Identify material decisions without selecting technologies or vendors by implication.

### Recommended first-demonstration scope (approval required)

- One synthetic line of business and one bounded claim scenario family.
- Batch or controlled submission of synthetic FHIR R4 claim bundles; no live production feed.
- A versioned public/synthetic policy corpus with jurisdiction and effective-date metadata.
- Transparent anomaly/duplicate/baseline signals plus one interpretable supervised or semi-supervised ML baseline if labels justify it.
- Bounded investigation workflows, a governance gate, an analyst case view, and immutable-style audit records.
- Research execution in a local/containerized or isolated development environment.

### Out of scope for the first demonstration

- Real PHI or production healthcare transactions.
- Production claims adjudication or payment-system connectivity.
- Automatic external side effects beyond read-only research tools and controlled internal writes.
- Broad support for all FHIR resources, payers, benefit designs, jurisdictions, or policy types.
- General-purpose autonomous agents, internet-wide browsing by agents, self-modifying prompts, or self-granted tool permissions.
- Claims of regulatory certification, clinical validity, fraud determination, or production-grade accuracy.

### Future / possible scope

- Additional FHIR profiles, payer policy sources, and synthetic claim domains.
- Federated or tenant-isolated deployments.
- Production-grade identity, deployment, resiliency, and compliance controls.
- Human-approved integrations with payer case-management or claims platforms.
- Longitudinal evaluation with qualified analyst feedback.
- Cloud deployment after data, threat, cost, and operational reviews.

---

## 8. Functional Requirements

### Confirmed

- The system must keep original synthetic inputs distinguishable from normalized and derived data.
- Unsupported or invalid healthcare data must fail safely and produce actionable validation information.
- Risk analysis must return a structured score/level and named signals; it must not return a final payment or coverage decision.
- Policy-dependent factual statements must be supported by retrieved evidence and citations before presentation as grounded findings.
- Investigation output must separate source facts, derived signals, model-generated synthesis, uncertainty, and human disposition.
- Agents may use only explicitly granted, scoped tools and must not expand their own privileges.
- Governance must be able to reject or escalate outputs that fail defined safety or quality conditions.
- A human must remain responsible for any consequential interpretation or downstream action.
- Significant AI/tool/retrieval/reviewer actions must be attributable to a trace and relevant version identifiers.
- Experimental variants must use controlled inputs and record sufficient configuration to support reproducibility.

### Assumptions requiring validation

- FHIR R4 is sufficient for the initial synthetic workflow.
- A minimal subset of Patient, Coverage, Claim, ExplanationOfBenefit, Organization, and Practitioner can represent the first research scenarios.
- FHIR Provenance and AuditEvent are useful interoperability/export representations, while an internal trace model may still be needed for detailed agent telemetry.
- Public CMS material is legally and operationally suitable for the first bounded policy corpus.
- Synthetic anomalies and controlled perturbations can provide defensible initial labels, while clearly limiting conclusions about real-world performance.

---

## 9. Non-Functional Requirements

### Confirmed

- **Safety:** fail closed at the analyst-readiness boundary when mandatory evidence, citation, authorization, or governance checks fail.
- **Security:** least privilege, server-side authorization, secret isolation, secure defaults, dependency review, and explicit trust boundaries are required from the first implementation.
- **Privacy:** initial datasets must be synthetic, public, de-identified as independently verified, or project-authored; no real PHI may be introduced without a new explicit approval and control review.
- **Auditability:** material transformations, retrievals, prompts, model/tool calls, governance outcomes, and human actions must be traceable and version-aware.
- **Reproducibility:** evaluation inputs, corpus versions, model/configuration versions, and metric definitions must be recorded.
- **Accessibility:** any analyst-facing UI must support keyboard operation and established accessibility practices; the target standard remains to be approved.
- **Maintainability:** component interfaces and responsibilities must remain explicit, testable, and provider-portable where practical.
- **Cost awareness:** model calls, tokens, retrieval operations, latency, and estimated per-investigation cost must be measurable.

### Recommended targets to define before implementation

- Maximum end-to-end latency and cost budget per investigation and per evaluation run.
- Required availability and recovery objectives for the demonstration environment.
- Minimum citation coverage and groundedness thresholds for analyst-ready reports.
- Security logging retention and research-data retention periods.
- Accessibility target, recommended as WCAG 2.2 AA for analyst-facing workflows.
- Performance and quality thresholds based on a versioned benchmark rather than arbitrary production claims.

---

## 10. Data and Privacy

### Data involved

- Synthetic patient, coverage, claim, explanation-of-benefit, provider, practitioner, and organization records.
- Public or project-authored policy documents and their source/version metadata.
- Derived features, risk scores, evidence links, embeddings, model output, governance results, and evaluation metrics.
- Agent/tool traces, prompt/model versions, and human-review actions.

### Sensitive / regulated data

- **Confirmed initial boundary:** no real PHI and no production claims.
- Synthetic healthcare-shaped data should still be handled conservatively because it can be confused with real data and may contain operational metadata.
- Public source licensing, usage restrictions, and document retention requirements must be recorded.
- Human reviewer identities and activity logs may be personal data even when the claim corpus is synthetic.

### Data boundaries

- Approved synthetic/public sources enter through controlled ingestion.
- Original source payloads remain logically separated from validated normalized records and derived features.
- Only the minimum necessary context may be sent to model, embedding, or reranking providers.
- Retrieval content is untrusted input and cannot directly alter instructions, permissions, or tool policy.
- Exports must preserve source attribution while excluding secrets, hidden prompts, and unnecessary identity data.

### Open privacy/compliance questions

- Which exact synthetic/public datasets and licenses are approved?
- Are any external model/embedding providers allowed to receive synthetic healthcare-shaped data, and under what retention/training terms?
- What identity, audit, and evaluation-data retention periods apply?
- What proof would be required before accepting a dataset described as de-identified rather than fully synthetic?
- Which geographic or contractual data-residency constraints apply to any future cloud deployment?

No document in this repository should describe VeriClaim as HIPAA compliant unless that claim is independently established for a specific deployed system and operating context.

---

## 11. Security and Trust Boundaries

### Confirmed requirements

- Authentication and authorization must protect analyst, governance, operator, and administrative capabilities if those roles are enabled.
- Authorization must be enforced server-side and at tool/data boundaries, not inferred from UI state or model instructions.
- Models and agents are untrusted decision-support components and may not grant themselves permissions.
- Retrieved documents, FHIR narrative fields, attachments, and tool output are untrusted and may contain direct or indirect prompt injection.
- Secrets must not be embedded in code, prompts, traces, browser bundles, datasets, or committed environment files.
- Consequential claim actions and regulated-data introduction require explicit human authority outside agent control.

### Recommended controls

- Standards-based identity, deny-by-default role permissions, object-level authorization, session controls, and auditable role changes.
- A tool broker that validates typed inputs, authorizes each operation, limits destinations, applies time/size/rate budgets, and records results.
- Content-origin labels, prompt/data separation, retrieval allowlists, output schema validation, citation entailment checks, and injection-focused tests.
- Encryption in transit and at rest, key separation, secret rotation, sanitized logs, software composition analysis, and signed/reproducible build practices where feasible.
- Threat modeling before implementation and before any new external integration, data classification, or deployment boundary.

### Human approval boundaries

- Only a human may approve/deny a claim, change payment, initiate recoupment, contact a provider as an official determination, or make a clinical/coding/legal conclusion.
- A human must approve introducing PHI, production credentials, write-capable external integrations, new model/data providers, and production deployment.
- Governance failures and low-confidence/insufficient-evidence cases must be escalated rather than silently passed.

---

## 12. External Systems and Integrations

| System / provider | Purpose | Status |
|---|---|---|
| HL7 FHIR R4 | Healthcare interoperability representation | Candidate standard; exact profiles/resources open |
| Synthea | Synthetic clinical record generation | Recommended initial source; approval and claim-fit validation required |
| CMS Blue Button sandbox/synthetic data | Synthetic Medicare-like data/API evaluation | Candidate; exact use and access requirements open |
| CMS coverage/policy sources | Public policy research corpus | Recommended bounded source; licensing, versioning, and ingestion method open |
| Model provider | LLM reasoning and/or embeddings/reranking | Unknown; data terms, quality, cost, residency, and credentials require approval |
| Identity provider | Authentication and identity lifecycle | Unknown; depends on deployment and user model |
| Database/vector storage provider | Operational records, policy index, traces, and evaluation data | Unknown; PostgreSQL/pgvector is recommended but not approved |
| Cloud provider | Hosted deployment, storage, networking, and observability | Unknown; local isolated development is recommended first |

No external integration is approved for production or write-capable use by this inception draft.

---

## 13. Known Constraints

### Technical

- FHIR resources do not by themselves define payer-specific adjudication semantics or a complete research label set.
- Public policies are jurisdictional, versioned, date-sensitive, and not safely reducible to isolated passages without context.
- Synthetic data may not reproduce real-world distributions, coding behavior, drift, bias, or adversarial activity.
- LLM and embedding behavior can change by model/version; provider adapters do not eliminate behavioral differences.
- Detailed agent traces may contain sensitive prompts, source excerpts, or identifiers and require minimization and access controls.

### Business / operational

- The platform cannot make or represent authoritative coverage, fraud, coding, clinical, or payment decisions.
- Qualified human expertise is required to define credible scenarios, policy interpretations, and review outcomes.
- Production use would require a separate compliance, privacy, security, clinical/payment-policy, validation, and operating-model program.

### Time / resource

- Budget, delivery timeline, team size, expected case volume, and cloud/provider spending authority are not yet provided.
- Model/provider credentials and access are not approved.

---

## 14. Success Criteria

### Confirmed qualitative criteria

The project is successful when it can demonstrate, on an approved versioned synthetic benchmark, that:

- A synthetic claim is validated, analyzed, investigated against traceable policy evidence, governed, and presented for human review without autonomous adjudication.
- An analyst can distinguish source data, risk signals, cited evidence, AI synthesis, uncertainty, governance status, and recorded human disposition.
- An auditor can reconstruct material system actions and the model, prompt, corpus, tool, and configuration versions used.
- The research harness can compare the five named architecture variants under controlled conditions.
- Unsafe, injected, unsupported, or insufficiently cited outputs are detected and blocked/escalated according to approved rules.

### Open measurable criteria

- Benchmark size and scenario coverage.
- ML, retrieval, groundedness, citation, injection-resistance, and human-agreement thresholds.
- Acceptable false-positive and false-escalation rates.
- Maximum latency, token use, and estimated cost per case and per experiment.
- Required inter-rater process and domain-expert validation.

---

## 15. Assumptions Register

| ID | Assumption | Why needed | Validation needed |
|---|---|---|---|
| A-001 | The first release is a research demonstration, not an operational payer product | Narrows safety, compliance, and integration scope | Sponsor approval of the first-demonstration scope |
| A-002 | FHIR R4 is the initial interoperability baseline | Provides a stable healthcare representation | Dataset fit assessment and approved minimal resource/profile list |
| A-003 | Synthea plus controlled claim perturbations can seed the benchmark | Avoids PHI while enabling reproducibility | Data-quality, licensing, representativeness, and scenario review |
| A-004 | A bounded public CMS policy corpus is sufficient for initial retrieval research | Enables source-grounded experiments | Source/license/version review and domain-expert relevance check |
| A-005 | A modular monolith is sufficient for the first demonstration | Reduces distributed-system complexity | Workload, isolation, and deployment review |
| A-006 | Human reviewers can provide meaningful structured feedback | Supports evaluation and escalation | Define reviewer qualifications, rubric, and agreement process |
| A-007 | External AI services may be usable with approved synthetic inputs | Enables rapid research | Approve provider terms, retention/training settings, cost, and credentials |
| A-008 | FHIR Provenance/AuditEvent supplement rather than replace detailed internal traces | Healthcare interoperability records differ from AI telemetry | Prototype mapping and audit-requirement review |

---

## 16. Recommended Decisions

| ID | Recommendation | Rationale | Human approval needed? |
|---|---|---|---|
| R-001 | Make the first milestone a narrow, end-to-end research vertical slice using only synthetic data | Tests the core safety/research thesis without premature breadth | Yes |
| R-002 | Use FHIR R4 with a project-defined minimal profile; evaluate Synthea first and Blue Button sandbox as a supplemental source | Keeps interoperability explicit while limiting the initial surface | Yes |
| R-003 | Start with a Python modular-monolith backend using FastAPI and Pydantic | Fits healthcare parsing, ML, evaluation, and explicit typed boundaries | Yes |
| R-004 | Include a minimal TypeScript/Next.js analyst UI in the first vertical slice | Human review is easier to validate through an actual review workflow | Yes |
| R-005 | Use PostgreSQL with pgvector and native full-text search, with Git-tracked migrations; choose hosting separately | Supports structured data, audit relationships, and hybrid retrieval without an extra vector vendor initially | Yes |
| R-006 | Use local Docker-based development first; defer AWS/Azure selection until a hosted demonstration is justified | Avoids early cloud cost, credentials, and residency commitments | Yes |
| R-007 | Use standards-based OIDC and deny-by-default RBAC; select the identity provider based on the approved deployment | Avoids custom authentication and preserves a clear authorization boundary | Yes |
| R-008 | Implement bounded orchestration as a deterministic state machine with a coordinator and typed specialist tools; represent research variants behind a common interface | Makes autonomy limits and comparative evaluation testable | Yes |
| R-009 | Use provider adapters for LLM, embeddings, and reranking, but approve one initial provider/model set with explicit data-use and cost controls | Portability is useful, while reproducibility requires a pinned starting configuration | Yes |
| R-010 | Begin risk research with deterministic baselines and interpretable scikit-learn models; add boosted/deep models only when data and metrics justify them | Produces transparent baselines and avoids overstating synthetic labels | Yes |
| R-011 | Adopt NIST AI RMF as a governance vocabulary and OWASP guidance as threat input, without claiming certification or compliance | Supplies useful structure while keeping project-specific controls evidence-based | Yes |
| R-012 | Use OpenTelemetry-compatible traces/metrics/logs and keep the first backend, worker, and UI in one deployment boundary unless isolation needs prove otherwise | Enables cross-component evaluation without premature infrastructure | Yes |
| R-013 | Establish hard per-case tool, token, time, recursion, and cost budgets before enabling autonomous tool loops | Limits runaway behavior and makes cost a testable governance property | Yes |
| R-014 | Treat all retrieved content and model/tool output as untrusted; require origin metadata and governance checks before analyst-ready status | Directly addresses injection, poisoning, and unsupported-output risk | No; this follows confirmed safety requirements |

---

## 17. Open Questions

### Approval package blocking `INCEPTION_READY`

| ID | Question | Why it matters | Blocks first task? |
|---|---|---|---|
| Q-001 | Approve the narrow synthetic end-to-end vertical slice in R-001 as the first milestone, or prioritize a different milestone? | Determines product scope and backlog ordering | Yes |
| Q-002 | Approve backend, frontend, and database as enabled components with the technologies in R-003 through R-005? | Required by `.ai/project.json` and verification planning | Yes |
| Q-003 | Approve the initial FHIR/data direction in R-002, including the initial synthetic-only boundary and a later profile-design task? | Determines dataset acquisition and interoperability work | Yes |
| Q-004 | Approve local Docker development first, with no cloud provider selected yet, as in R-006? | Establishes the initial platform, credential, cost, and data boundary | Yes |
| Q-005 | Is standards-based OIDC plus analyst/governance/operator/admin RBAC the right target, and may the first local demo use a local/test identity provider? | Defines identity and authorization trust boundaries | Yes |
| Q-006 | Approve bounded deterministic orchestration and the common-variant interface in R-008? | Determines agent autonomy, permissions, and evaluation architecture | Yes |
| Q-007 | May external model/embedding services receive approved synthetic healthcare-shaped data, and which provider/model/data-retention/cost constraints apply? | Determines provider choice, privacy controls, reproducibility, credentials, and cost | Yes |
| Q-008 | Approve PostgreSQL/pgvector hybrid retrieval and Git-tracked migrations, while deferring managed hosting? | Resolves the operational database/vector-storage choice | Yes |
| Q-009 | Approve the transparent ML baseline in R-010 and acknowledge that synthetic-label results will not be represented as clinical or production validity? | Defines the first ML research path and claims boundary | Yes |
| Q-010 | Approve NIST AI RMF/OWASP as non-certifying reference frameworks and the fail-closed governance boundary? | Defines governance vocabulary and release-blocking behavior | Yes |
| Q-011 | What initial per-case and monthly experiment cost ceilings should apply, or should the first task measure baselines before ceilings are finalized? | Controls provider usage and architecture tradeoffs | Yes |
| Q-012 | Approve OpenTelemetry-compatible observability and local-only telemetry for the first milestone? | Determines trace format and external telemetry exposure | Yes |

### Important questions that need not block the first foundation task

| ID | Question | Why it matters | Blocks first task? |
|---|---|---|---|
| Q-013 | Which precise synthetic claim scenarios, line of business, and policy jurisdiction should form the benchmark? | Affects relevance and expert validation | No; resolve during benchmark design |
| Q-014 | Which exact FHIR profiles, required fields, terminology bindings, and validation packages are needed? | Prevents accidental semantic invention | No; resolve in a healthcare-data design task |
| Q-015 | Which policy sources, dates, licenses, update cadence, and historical-version rules are approved? | Ensures citation correctness and reproducibility | No; resolve before corpus ingestion |
| Q-016 | What reviewer qualifications, rubric, conflict-resolution process, and accessibility target apply? | Affects evaluation validity and UX | No; resolve before analyst workflow testing |
| Q-017 | What retention/deletion periods apply to source data, traces, prompts, reviewer identity, and evaluation results? | Affects privacy, storage, and audit design | No; resolve before persistent multi-user use |
| Q-018 | What scale, latency, availability, recovery, and concurrency targets apply? | Affects deployment architecture | No for the first local benchmark; required before hosted use |
| Q-019 | When, if ever, should a cloud provider, managed database, managed identity provider, or external telemetry backend be selected? | Introduces vendor, credential, residency, and ongoing cost commitments | No for local development |
| Q-020 | Should the repository directory name `VeriClam` be renamed to match the confirmed product name `VeriClaim`? | Avoids naming ambiguity in tooling and documentation | No |

---

## 18. Initial Proposed Backlog

> These are proposed work items only. They are not active tasks and must not be created until inception is approved and `.ai/project.json` is `INCEPTION_READY`.

| Order | Proposed task ID | Title | Purpose | Depends on |
|---:|---|---|---|---|
| 1 | FOUNDATION-001 | Define synthetic benchmark and evaluation protocol | Approve claim scenarios, dataset sources, research variants, metrics, splits, versioning, and validity limitations | Inception approval |
| 2 | DATA-001 | Define and validate the minimal FHIR R4 profile | Establish supported resources/fields/terminologies and synthetic fixtures without inventing payer semantics | FOUNDATION-001 |
| 3 | POLICY-001 | Define the versioned policy corpus | Approve sources, licensing, jurisdiction, effective dates, provenance, ingestion, and adversarial fixtures | FOUNDATION-001 |
| 4 | PLATFORM-001 | Establish the secure application foundation | Create the approved backend/frontend/database skeleton, identity boundary, migrations, contracts, and verification checks | FOUNDATION-001; approved stack/auth/deployment |
| 5 | RISK-001 | Implement transparent risk-analysis baselines | Produce deterministic signals and an interpretable ML baseline with reproducible metrics | DATA-001; PLATFORM-001 |
| 6 | RETRIEVAL-001 | Implement policy retrieval baseline | Add lexical/semantic retrieval, metadata filters, citations, and retrieval evaluation | POLICY-001; PLATFORM-001 |
| 7 | INVESTIGATION-001 | Implement the common investigation interface and baseline variants | Support controlled single-model, RAG, and bounded-agent workflows against the same case contract | RISK-001; RETRIEVAL-001 |
| 8 | GOVERNANCE-001 | Implement governance gate and audit trace | Enforce evidence, citation, schema, permission, injection, budget, and escalation controls | INVESTIGATION-001 |
| 9 | REVIEW-001 | Implement the analyst review workflow | Present cases and record human findings, rationale, feedback, and follow-up requests accessibly | GOVERNANCE-001 |
| 10 | EVALUATION-001 | Execute the comparative research experiment | Compare variants A–E on approved quality, safety, human, latency, token, and cost measures | REVIEW-001; benchmark frozen |
| 11 | DEPLOYMENT-001 | Prepare a hardened demonstration environment | Add the approved hosted or isolated deployment, operational controls, monitoring, and recovery evidence | EVALUATION-001; separate platform approval |

### Recommended first task

**FOUNDATION-001 — Define synthetic benchmark and evaluation protocol**

Reason: the benchmark, scenarios, labels, validity limits, and metrics determine whether subsequent data, ML, retrieval, agent, governance, and human-review work can produce defensible evidence.

---

## 19. Project-Level Decisions Already Approved

- VeriClaim is a governed healthcare payment-integrity research and decision-support platform.
- Humans retain authority for consequential claim, payment, clinical, and operational decisions.
- The system may identify claims for further review and assemble evidence, but may not autonomously approve, deny, adjudicate, or modify payment.
- Initial development uses synthetic or appropriate public data and does not require real PHI.
- FHIR is to be evaluated as the primary interoperability standard; the exact supported subset is not yet approved.
- Evidence grounding, citations, governance, traceability, security, and reproducible evaluation are first-class requirements.
- The five research variants A–E are evaluation targets, not preselected production architectures.
- No technology or provider listed in the raw idea is approved merely by being listed.
- The project must not claim HIPAA compliance without independent support for that claim.

---

## 20. Related Repository Documents

- `docs/architecture/SYSTEM.md`
- `docs/adr/ADR-0001-human-authority-over-claim-outcomes.md`
- `docs/adr/ADR-0002-synthetic-data-initial-boundary.md`
- `docs/standards/`
- `contracts/`
- `.ai/project.json`
- `.ai/tasks/`

