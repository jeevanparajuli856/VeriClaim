# FOUNDATION-001 — Define synthetic benchmark and evaluation protocol

## Goal

Define a reproducible, reviewable synthetic benchmark and evaluation protocol that later VeriClaim tasks can implement without inventing claim semantics, labels, comparison rules, or safety claims. The protocol must use the approved local Blue Button sample corpus as its starting point and make its limitations explicit.

## In scope

- Inventory the selected `dataset/` corpus, its synthetic classification, origin evidence, usage/license evidence, immutable identification approach, and known fitness limitations without modifying the corpus.
- Recommend one bounded initial claim-scenario family, line of business, and policy-jurisdiction scope that the available corpus can credibly seed; distinguish confirmed source facts from project-authored perturbations and expert-validated labels.
- Identify the minimum additional synthetic fixtures or controlled perturbations needed for meaningful positive, negative, boundary, and adversarial benchmark cases.
- Define a common case/evidence configuration and comparison protocol for research variants A–E so inputs, available evidence, output expectations, scoring, and governance interventions remain comparable where scientifically appropriate.
- Define benchmark versioning, freezing, train/development/evaluation separation, leakage controls, repeatability inputs, and change-control rules.
- Define metric calculations and evidence requirements across deterministic/ML, retrieval, LLM/RAG, agentic, governance, human-review, latency, token, and estimated-cost dimensions, including how undefined or inapplicable metrics are reported.
- Distinguish sponsor-confirmed private local smoke-test limits from benchmark policy: the former are hard development guardrails, while final experiment ceilings require measured baselines and explicit approval.
- Record validity limits and the downstream decisions handed to DATA-001, POLICY-001, PLATFORM-001, and later implementation/evaluation tasks.

## Out of scope

- Creating or changing datasets, fixtures, application code, tests, API contracts, schemas, migrations, infrastructure, deployment resources, or cloud configuration.
- Defining the exact supported FHIR profile, terminology bindings, validation packages, or normalization mappings owned by DATA-001.
- Selecting policy documents, ingestion behavior, or a final policy interpretation owned by POLICY-001 and qualified human review.
- Selecting an orchestration framework, direct SDK, Google ADK, managed agent runtime, embedding provider, reranker, hosted application platform, or production architecture.
- Using Vertex AI, production credentials, PHI, production claims, write-capable claim-system tools, or external telemetry during this documentation task.
- Claiming clinical, fraud, coverage, payment, regulatory, or production validity from synthetic benchmark results.

## Architecture impact

- Expected to be documentation/evaluation-design only. The architecture specialist must explicitly classify database, backend, frontend, infrastructure, testing, and contract impacts in `architecture-report.json`.
- The protocol must preserve the approved flow: FHIR validation/normalization, deterministic anomaly/risk signals, bounded investigation, Gemini-supported evidence analysis, deterministic schema/evidence/governance validation, and human review.
- The repository-root `dataset/` remains read-only, untrusted source input. Generated fixtures and benchmark artifacts, when later implemented, must live outside that source directory and carry provenance.

## Contract impact

- No component interface change is anticipated. If architecture identifies a required contract, it must be reconciled and validated before `CONTRACT_READY`; otherwise this task has no contract artifact.

## Security considerations

- Only approved synthetic/public development context is in scope; no PHI, production claims, credentials, tokens, project identifiers, or private environment values may enter documentation or reports.
- Dataset content, retrieved content, agent/model output, tool output, synthetic labels, and evaluator output are untrusted evidence until independently validated.
- Gemini is neither the sole nor authoritative anomaly detector. Any later model output is a candidate finding that must cite available evidence and pass deterministic validation before human review.
- Human analysts retain authority for consequential interpretation; the protocol must score unsafe autonomous behavior as failure, not capability.
- Benchmark design must test injection, unsupported claims, citation failure, leakage, permission violations, budget violations, and fail-closed escalation without enabling write-capable external actions.

## Dependencies

- Project inception is `INCEPTION_READY`, including approved ADR-0001 through ADR-0004.
- The sponsor approved the repository-root `dataset/` Blue Button examples as the initial local development corpus.
- Local Vertex AI connectivity and private bounded settings are sponsor-confirmed, but provider execution is not required for this task and does not establish production readiness.

## Acceptance criteria

- The protocol records a deterministic inventory and immutable identification method for every selected source file, plus origin, synthetic classification, usage/license evidence status, and material limitations; it does not modify `dataset/`.
- It recommends one bounded scenario family, line of business, and policy-jurisdiction scope grounded in available evidence, and clearly marks any item that still requires sponsor or qualified-domain-expert approval.
- It specifies additional synthetic cases or perturbation classes, their provenance, expected labels, independent review needs, and separation from untouched source records.
- It defines controlled comparison rules for variants A–E, including shared inputs/evidence, frozen configuration, repeated runs where applicable, scoring, and treatment of failed/abstained/escalated outputs.
- It defines benchmark version/freeze rules, dataset partitions, leakage prevention, random seeds or deterministic alternatives, run manifests, and change invalidation rules.
- It defines each applicable metric family, required evidence, aggregation and uncertainty reporting, evaluator authority, and the method for proposing thresholds after baselines; model judges are never the sole basis for safety claims.
- It records validity and generalization limits, explicitly prohibits production/clinical/payment/fraud claims, and preserves the synthetic/public-only Vertex AI and human-authority boundaries.
- It gives DATA-001, POLICY-001, PLATFORM-001, and later experiment tasks concrete inputs and explicitly deferred decisions without silently selecting contracts, schemas, frameworks, providers, or hosting.
