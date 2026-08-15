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

**Inception ready.** On 2026-08-14, the sponsor approved the first-milestone package R-001 through R-014, selected the existing CMS Blue Button sample FHIR data at repository-root `dataset/` as the initial local development dataset (`../dataset` from `backend/`), and confirmed local Vertex AI Gemini readiness through Application Default Credentials and external runtime configuration. A direct Gemini request through Vertex AI has been smoke-tested successfully. This proves local model connectivity only; questions Q-013 through Q-019 and the task-level orchestration/runtime choices remain deliberately deferred and do not block the first foundation task.

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

### Confirmed for the first demonstration

1. **Ingest a bounded synthetic corpus** — import a deliberately small, versioned FHIR R4 dataset and reject malformed or unsupported inputs.
2. **Score transparent risk signals** — combine deterministic/heuristic baselines with an interpretable ML baseline and retain feature-level explanations.
3. **Research a bounded policy corpus** — retrieve versioned public or project-authored policy passages through lexical and semantic search and preserve citations.
4. **Escalate ungrounded output** — block a report from analyst-ready status when required citations, provenance, confidence, or safety checks fail.

---

## 6. Core Capabilities

### Confirmed

- Synthetic healthcare claim and related-data handling, with FHIR R4 as the approved initial interoperability standard.
- Structured risk assessment that recommends investigation priority but does not decide claim outcomes.
- Evidence and policy retrieval with source citations and traceability.
- Bounded AI-assisted investigation with human oversight.
- Governance controls for unsupported conclusions, injection, leakage, excessive autonomy, tool permissions, versioning, escalation, and auditability.
- Human review and recorded feedback.
- Reproducible evaluation across ML, retrieval, LLM/RAG, agentic, governance, human-review, latency, and cost dimensions.

### Approved initial direction

- A narrow end-to-end vertical slice before broader payer, policy, FHIR, model, or deployment coverage.
- A single deployable application with clearly separated modules before considering independently deployed microservices.
- A bounded investigation workflow with deterministic application controls, explicit transitions, typed/scoped tools, and hard time/token/tool/cost limits rather than unconstrained agent-to-agent delegation.
- A common investigation contract and evaluation harness shared by all research variants.
- Hybrid lexical and semantic retrieval with source/version metadata and a post-retrieval evidence-validation stage.
- An explicit governance gate between generated investigation findings and analyst-ready presentation.

### Confirmed agent architecture boundary

```text
FHIR validation and normalization
  -> deterministic anomaly/risk signals
  -> bounded investigation workflow
  -> Gemini-supported evidence analysis
  -> schema/evidence/governance validation
  -> human analyst review
```

Gemini is neither the sole nor the authoritative anomaly detector. Its outputs are untrusted candidate findings and explanations that must cite available evidence and pass deterministic schema, evidence, authorization, and governance checks before human review.

A project-owned state-machine implementation, direct Google Gen AI SDK integration, Google ADK, and a future managed Agent Platform runtime are separate task-level architecture/runtime choices. None is selected by inception; task architecture must keep the choice visible and must preserve the confirmed bounded-control and human-authority invariants.

---

## 7. Scope

### Confirmed inception scope

- Define product, safety, privacy, traceability, research, and human-authority boundaries.
- Evaluate synthetic/public healthcare data sources and a minimal FHIR R4 resource profile.
- Define a research path for risk analysis, policy retrieval, AI-assisted investigation, governance, audit, and human review.
- Identify material decisions without selecting technologies or vendors by implication.

### Confirmed first-demonstration scope

- One synthetic line of business and one bounded claim scenario family.
- Batch or controlled submission of synthetic FHIR R4 claim bundles; no live production feed.
- A versioned public/synthetic policy corpus with jurisdiction and effective-date metadata.
- Transparent anomaly/duplicate/baseline signals plus one interpretable supervised or semi-supervised ML baseline if labels justify it.
- Bounded investigation workflows, a governance gate, an analyst case view, and immutable-style audit records.
- Research execution in a local Docker-based development environment, with sponsor-confirmed local ADC/runtime configuration for Vertex AI Gemini as the only approved external agent-development LLM endpoint.

### Out of scope for the first demonstration

- Real PHI or production healthcare transactions.
- Production claims adjudication or payment-system connectivity.
- Automatic external side effects beyond read-only research tools and controlled internal writes.
- Write-capable claim-system tools, production credentials, and autonomous claim decisions.
- Broad support for all FHIR resources, payers, benefit designs, jurisdictions, or policy types.
- General-purpose autonomous agents, internet-wide browsing by agents, self-modifying prompts, or self-granted tool permissions.
- Google ADK as a preselected framework; Gemini Enterprise Agent Platform Runtime, Cloud Run, GKE, or general Google Cloud application hosting.
- External telemetry containing prompts, FHIR data, model output, or other development content; embedding or reranking providers without separate approval.
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
- The selected Patient, Coverage, and ExplanationOfBenefit sample resources can seed the first research scenarios; additional resource types may be required by the approved benchmark design.
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
- **Accessibility:** the analyst-facing UI targets WCAG 2.2 AA and must support keyboard operation and established accessibility practices.
- **Maintainability:** component interfaces and responsibilities must remain explicit, testable, and provider-portable where practical.
- **Cost awareness:** model calls, tokens, retrieval operations, latency, and estimated per-investigation cost must be measurable.

### Recommended targets to define before implementation

- Maximum end-to-end latency and cost budget per investigation and per evaluation run.
- Required availability and recovery objectives for the demonstration environment.
- Minimum citation coverage and groundedness thresholds for analyst-ready reports.
- Security logging retention and research-data retention periods.
- Performance and quality thresholds based on a versioned benchmark rather than arbitrary production claims.

---

## 10. Data and Privacy

### Data involved

- The initial local development corpus is the repository-root `dataset/` directory (addressed as `../dataset` from `backend/`). It currently contains CMS Blue Button sample FHIR R4 Patient, Coverage, and ExplanationOfBenefit data for a single synthetic beneficiary.
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
- The local `dataset/` corpus is development input, not an application write target. Its files must remain versioned/provenanced, must be treated as untrusted input, and must not receive generated secrets, credentials, traces, or model output.
- Original source payloads remain logically separated from validated normalized records and derived features.
- Only the minimum necessary context may be sent to model, embedding, or reranking providers.
- The sponsor confirms that local Application Default Credentials and the required Google Cloud, Vertex AI, model, timeout, token, tool-call, workflow-duration, and cost-limit settings are present outside Git and that a direct Vertex AI Gemini request has succeeded. Approved synthetic/public development context may be sent only through this bounded configuration. Real PHI, production claims, secrets, and unnecessary identifiers remain prohibited.
- Retrieval content is untrusted input and cannot directly alter instructions, permissions, or tool policy.
- Exports must preserve source attribution while excluding secrets, hidden prompts, and unnecessary identity data.

### Open privacy/compliance questions

- What license/usage record and immutable version identifier should accompany the selected Blue Button sample corpus before the benchmark is frozen?
- What provider contractual retention/training and residency evidence must be recorded before model-backed development expands beyond the confirmed connectivity smoke test? Any future embedding/reranking provider remains separately approval-gated.
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

### Confirmed initial controls

- Standards-based OIDC, deny-by-default role permissions, object-level authorization, and server-side enforcement.
- Vertex AI development authentication through local Application Default Credentials, with runtime configuration and credentials excluded from Git and unavailable to the browser.
- Local-only telemetry by default; external telemetry may not contain prompts, FHIR data, model output, secrets, or private runtime configuration.

### Recommended controls

- Session controls, auditable role changes, and detailed administrative workflows appropriate to the selected local/test identity provider.
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
| HL7 FHIR R4 | Healthcare interoperability representation | Approved initial standard; exact project profile remains a DATA-001 decision |
| Local `dataset/` (CMS Blue Button sample data) | Initial synthetic development corpus containing Patient, Coverage, and ExplanationOfBenefit examples | Approved for local development; provenance/license/version and benchmark fitness must be recorded before benchmark freeze |
| Synthea | Optional future synthetic clinical record generation | Not selected for the initial corpus; may be evaluated later if additional scenarios require generated data |
| CMS coverage/policy sources | Public policy research corpus | Recommended bounded source; licensing, versioning, and ingestion method open |
| Google Cloud Vertex AI Gemini | Bounded agent-development evidence analysis/reasoning | Approved and locally configured through Application Default Credentials plus uncommitted runtime settings; direct model connectivity is smoke-tested; this is not production or general Google Cloud hosting approval |
| Agent orchestration/integration runtime | Coordinate the bounded investigation workflow and connect to Gemini | Task-level choice remains open among a project-owned state-machine implementation, direct Google Gen AI SDK integration, Google ADK, or another architecture-approved approach; Gemini Enterprise Agent Platform Runtime deployment is not approved |
| Identity provider | Authentication and identity lifecycle | Standards-based OIDC approved; a local/test provider may be selected during platform design, while hosted identity remains deferred |
| PostgreSQL with pgvector | Operational records, policy index, traces, and evaluation data | Approved for local development with native full-text search and Git-tracked migrations; managed hosting remains unselected |
| Cloud provider | Hosted application deployment, storage, networking, and observability | No hosted application platform selected; local Docker development is approved first, and Vertex AI approval does not approve general Google Cloud hosting |

No external integration is approved for production or write-capable claim-system use. Vertex AI Gemini is approved only as the bounded, synthetic/public-only development LLM boundary described above.

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

- A local cost-limit setting is present, but final budget, delivery timeline, team size, expected case volume, and cloud/provider spending authority are not yet approved.
- Local Vertex AI authentication, bounded runtime limits, and model connectivity are sponsor-confirmed; all values remain outside Git. This evidence does not establish production credentials, production readiness, provider guarantees, or approval for other Google Cloud services.

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
| A-002 | FHIR R4 is the initial interoperability baseline | Provides a stable healthcare representation | Dataset fit assessment and approved minimal resource/profile list |
| A-004 | A bounded public CMS policy corpus is sufficient for initial retrieval research | Enables source-grounded experiments | Source/license/version review and domain-expert relevance check |
| A-006 | Human reviewers can provide meaningful structured feedback | Supports evaluation and escalation | Define reviewer qualifications, rubric, and agreement process |
| A-008 | FHIR Provenance/AuditEvent supplement rather than replace detailed internal traces | Healthcare interoperability records differ from AI telemetry | Prototype mapping and audit-requirement review |

The former assumptions that the first milestone might not be approved (A-001), that Synthea would seed the initial benchmark (A-003), that the modular monolith was merely provisional (A-005), and that an external AI provider might be allowed (A-007) are obsolete. They were resolved by the 2026-08-14 approval package: the first milestone and modular-monolith direction are confirmed, the existing Blue Button sample corpus is the initial dataset, and Vertex AI Gemini is approved within the synthetic/public-only development boundary.

---

## 16. Approved Inception Decisions

| ID | Approved decision | Rationale | Status |
|---|---|---|---|
| R-001 | Make the first milestone a narrow, end-to-end research vertical slice using only synthetic data | Tests the core safety/research thesis without premature breadth | Approved 2026-08-14 |
| R-002 | Use FHIR R4 with a project-defined minimal profile; use the existing local Blue Button sample corpus first and consider Synthea only if later scenarios need it | Keeps interoperability explicit while limiting the initial surface | Approved with dataset refinement 2026-08-14 |
| R-003 | Start with a Python modular-monolith backend using FastAPI and Pydantic | Fits healthcare parsing, ML, evaluation, and explicit typed boundaries | Approved 2026-08-14 |
| R-004 | Include a minimal TypeScript/Next.js analyst UI in the first vertical slice | Human review is easier to validate through an actual review workflow | Approved 2026-08-14 |
| R-005 | Use PostgreSQL with pgvector and native full-text search, with Git-tracked migrations; choose hosting separately | Supports structured data, audit relationships, and hybrid retrieval without an extra vector vendor initially | Approved 2026-08-14 |
| R-006 | Use local Docker-based development first; defer hosted application-cloud selection until justified | Avoids early cloud cost, credentials, and residency commitments | Approved 2026-08-14 |
| R-007 | Use standards-based OIDC and deny-by-default RBAC; allow a local/test identity provider for the first demonstration | Avoids custom authentication and preserves a clear authorization boundary | Approved 2026-08-14 |
| R-008 | Enforce a bounded investigation workflow with deterministic application controls, explicit transitions, scoped typed tools, hard budgets, and a common experiment interface; defer the concrete orchestration/framework implementation | Makes autonomy limits and comparative evaluation testable without preselecting a project-owned state machine, direct SDK integration, Google ADK, or managed agent runtime | Approved and framework boundary clarified 2026-08-14 |
| R-009 | Use a provider adapter and Vertex AI Gemini for bounded agent-development evidence analysis; local ADC/configuration and direct connectivity are confirmed, while embedding/reranking choices remain task-scoped | Portability is useful, while reproducibility requires controlled configuration without committing private runtime values | Approved and connectivity confirmed 2026-08-14 |
| R-010 | Begin risk research with deterministic baselines and interpretable scikit-learn models; add boosted/deep models only when data and metrics justify them | Produces transparent baselines and avoids overstating synthetic labels | Approved 2026-08-14 |
| R-011 | Adopt NIST AI RMF as a governance vocabulary and OWASP guidance as threat input, without claiming certification or compliance | Supplies useful structure while keeping project-specific controls evidence-based | Approved 2026-08-14 |
| R-012 | Use OpenTelemetry-compatible traces/metrics/logs and keep the first backend, worker, and UI in one deployment boundary unless isolation needs prove otherwise | Enables cross-component evaluation without premature infrastructure | Approved 2026-08-14 |
| R-013 | Enforce the sponsor-confirmed local timeout/token/tool/workflow/cost settings as smoke-test guardrails; use the foundation task to measure baselines before approving final experiment ceilings | Limits runaway behavior and makes cost a testable governance property without treating private local values as durable policy | Approved and local guardrails confirmed 2026-08-14 |
| R-014 | Treat all retrieved content and model/tool output as untrusted; require origin metadata and governance checks before analyst-ready status | Directly addresses injection, poisoning, and unsupported-output risk | Confirmed safety requirement |

---

## 17. Decision Resolution and Deferred Questions

### Approval package resolved for `INCEPTION_READY`

| ID | Resolution | Result |
|---|---|---|
| Q-001 | Approve R-001. | The narrow synthetic end-to-end vertical slice is the first milestone. |
| Q-002 | Approve R-003 through R-005. | Backend, frontend, and database are enabled using Python/FastAPI/Pydantic, TypeScript/Next.js, and PostgreSQL/pgvector respectively. |
| Q-003 | Approve the FHIR R4 and synthetic-only direction, refined to use repository-root `dataset/` first. | Exact FHIR profiles remain a DATA-001 design decision; Synthea is no longer assumed to be the first source. |
| Q-004 | Approve local Docker development first. | No hosted application cloud is selected; using Vertex AI does not approve general Google Cloud hosting. |
| Q-005 | Approve standards-based OIDC, deny-by-default RBAC, and a local/test identity provider for the first demo. | Detailed role permissions and provider selection belong to PLATFORM-001. |
| Q-006 | Approve R-008. | Orchestration is bounded and deterministic, with typed specialist tools and a common experiment interface. |
| Q-007 | Approve Vertex AI Gemini for bounded agent-development LLM use with approved synthetic/public context. | Local ADC, required runtime configuration, limits, and a successful direct connectivity smoke test are sponsor-confirmed and remain outside Git. This does not approve production data/credentials, hosting, external sensitive telemetry, embeddings/reranking, Google ADK, or a managed agent runtime. |
| Q-008 | Approve R-005. | PostgreSQL/pgvector, native full-text search, and Git-tracked migrations are the initial persistence/retrieval platform; managed hosting is deferred. |
| Q-009 | Approve R-010 and its validity limitation. | Transparent baselines come first and synthetic results cannot be represented as clinical or production validity. |
| Q-010 | Approve R-011 and the fail-closed governance boundary. | NIST AI RMF and OWASP are non-certifying references, not compliance claims. |
| Q-011 | Use the configured local smoke-test limits as development guardrails and measure baselines in FOUNDATION-001 before finalizing experiment ceilings. | The presence of local timeout/token/tool/workflow/cost values is confirmed but does not make them final benchmark policy; no autonomous tool loop may exceed task-approved limits. |
| Q-012 | Approve OpenTelemetry-compatible observability and local-only telemetry. | External telemetry remains prohibited until separately approved. |

### Important questions that need not block the first foundation task

| ID | Question | Why it matters | Blocks first task? |
|---|---|---|---|
| Q-013 | Which scenarios, line of business, and policy jurisdiction should be built from the selected Blue Button sample corpus, and what additional synthetic fixtures are needed? | Affects relevance and expert validation | No; resolve during benchmark design |
| Q-014 | Which exact FHIR profiles, required fields, terminology bindings, and validation packages are needed for Patient, Coverage, and ExplanationOfBenefit? | Prevents accidental semantic invention | No; resolve in a healthcare-data design task |
| Q-015 | Which policy sources, dates, licenses, update cadence, and historical-version rules are approved? | Ensures citation correctness and reproducibility | No; resolve before corpus ingestion |
| Q-016 | What reviewer qualifications, rubric, and conflict-resolution process apply? WCAG 2.2 AA is the approved analyst-interface target. | Affects evaluation validity and UX | No; resolve before analyst workflow testing |
| Q-017 | What retention/deletion periods apply to source data, traces, prompts, reviewer identity, and evaluation results? | Affects privacy, storage, and audit design | No; resolve before persistent multi-user use |
| Q-018 | What scale, latency, availability, recovery, and concurrency targets apply? | Affects deployment architecture | No for the first local benchmark; required before hosted use |
| Q-019 | When, if ever, should a hosted application platform, managed database, managed identity provider, or external telemetry backend be selected? | Introduces vendor, credential, residency, and ongoing cost commitments beyond the bounded Vertex AI development endpoint | No for local development |

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
| 7 | INVESTIGATION-001 | Select the orchestration/integration approach and implement the common investigation interface | Architecture review selects among the still-open project-owned state-machine/direct SDK/Google ADK options as appropriate, then supports controlled single-model, RAG, and bounded-agent variants against the same case contract | RISK-001; RETRIEVAL-001 |
| 8 | GOVERNANCE-001 | Implement governance gate and audit trace | Enforce evidence, citation, schema, permission, injection, budget, and escalation controls | INVESTIGATION-001 |
| 9 | REVIEW-001 | Implement the analyst review workflow | Present cases and record human findings, rationale, feedback, and follow-up requests accessibly | GOVERNANCE-001 |
| 10 | EVALUATION-001 | Execute the comparative research experiment | Compare variants A–E on approved quality, safety, human, latency, token, and cost measures | REVIEW-001; benchmark frozen |
| 11 | DEPLOYMENT-001 | Prepare a hardened demonstration environment | Add the approved hosted or isolated deployment, operational controls, monitoring, and recovery evidence | EVALUATION-001; separate platform approval |

### Selected first task

**FOUNDATION-001 — Define synthetic benchmark and evaluation protocol**

Reason: the benchmark, scenarios, labels, validity limits, and metrics determine whether subsequent data, ML, retrieval, agent, governance, and human-review work can produce defensible evidence.

---

## 19. Decision Impact Assessment (2026-08-14)

| Concern | Changed? | Recorded outcome |
|---|---|---|
| `docs/PROJECT.md` | Yes | Promotes the R-001–R-014 approval package, records the selected local Blue Button corpus and Vertex AI Gemini boundary, resolves obsolete assumptions, and marks inception ready. |
| `docs/architecture/SYSTEM.md` | Yes | Promotes the approved stack/topology and adds the local-dataset and Vertex AI trust/data flows. |
| ADRs | Yes | ADR-0002 is refined with the selected initial corpus; ADR-0003 records the approved initial application platform; ADR-0004 records the bounded Vertex AI Gemini development-provider decision. |
| Security/privacy boundaries | Yes, without relaxing the synthetic/public-only classification | The external trust boundary now includes approved synthetic/public-only calls to Vertex AI Gemini. Data minimization, explicit configuration, uncommitted credentials, provider-term review, quotas, audit, and fail-closed behavior are required; PHI and production claims remain prohibited. |
| Database/provider configuration | Yes | PostgreSQL with pgvector and native full-text search is enabled for local development; migrations are Git-tracked under `database/migrations/`; managed hosting remains unselected. |
| Operational project configuration | Yes | `.ai/project.json` is set to `INCEPTION_READY`, all component enablement/technology fields are resolved, and the database provider/migration path are declared. Vertex details remain in product/architecture/ADR artifacts because the operational schema has no model-provider field. |
| Local Vertex readiness | Yes | Application Default Credentials, required private runtime settings/limits, and a direct Vertex AI Gemini smoke test are confirmed; only variable-name placeholders are committed, and connectivity is explicitly separated from production deployment approval. |

---

## 20. Project-Level Decisions Already Approved

- VeriClaim is a governed healthcare payment-integrity research and decision-support platform.
- Humans retain authority for consequential claim, payment, clinical, and operational decisions.
- The system may identify claims for further review and assemble evidence, but may not autonomously approve, deny, adjudicate, or modify payment.
- Initial development uses the local Blue Button sample data at `dataset/` and other explicitly approved synthetic/public data; real PHI is prohibited.
- FHIR R4 is the initial interoperability standard; the exact supported project profile remains a DATA-001 decision.
- The initial stack is a Python/FastAPI/Pydantic modular-monolith backend, TypeScript/Next.js frontend, and local PostgreSQL/pgvector database with Git-tracked migrations and Docker-based development.
- Vertex AI Gemini is the approved agent-development LLM provider for minimized synthetic/public context; local ADC/configuration and direct connectivity are confirmed outside Git. This is not approval for PHI, production claims/credentials, Gemini Enterprise Agent Platform Runtime, or general hosted deployment.
- Standards-based OIDC, deny-by-default RBAC, bounded deterministic application control, OpenTelemetry-compatible local observability, transparent ML baselines, and the NIST AI RMF/OWASP non-certifying reference direction are approved.
- The concrete orchestration/integration choice remains task-level: project-owned state-machine implementation, direct Google Gen AI SDK integration, and Google ADK are not selected during inception.
- Evidence grounding, citations, governance, traceability, security, and reproducible evaluation are first-class requirements.
- The five research variants A–E are evaluation targets, not preselected production architectures.
- The project must not claim HIPAA compliance without independent support for that claim.

---

## 21. Related Repository Documents

- `docs/architecture/SYSTEM.md`
- `docs/adr/ADR-0001-human-authority-over-claim-outcomes.md`
- `docs/adr/ADR-0002-synthetic-data-initial-boundary.md`
- `docs/adr/ADR-0003-initial-application-platform.md`
- `docs/adr/ADR-0004-vertex-ai-gemini-development-provider.md`
- `docs/operations/VERTEX_AI_LOCAL.md`
- `docs/standards/`
- `contracts/`
- `.ai/project.json`
- `.ai/tasks/`
