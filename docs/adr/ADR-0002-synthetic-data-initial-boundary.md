# ADR-0002 — Synthetic data is the initial healthcare-data boundary

## Status

Accepted during project inception.

## Context

VeriClaim needs healthcare-shaped data to research FHIR ingestion, risk signals, retrieval, agents, governance, and analyst review. Real claims and clinical data can contain PHI and introduce regulatory, contractual, privacy, security, residency, and operational obligations that are not established for this new project.

## Decision

Initial development and evaluation will use synthetic, project-authored, or appropriate public data. The project will not require or ingest real PHI or production claims.

Data described as de-identified is not automatically inside this boundary: its provenance, de-identification basis, permitted use, and re-identification risk require explicit review and approval. Synthetic healthcare-shaped data will still receive conservative handling, access control, provenance, and retention practices.

Introducing real PHI, production claims, or production system connectivity requires a separate explicit human approval and a revised privacy, security, compliance, data-governance, architecture, and operating assessment.

### Inception refinement — 2026-08-14

The initial local development source is the repository-root `dataset/` directory (`../dataset` from the planned `backend/` working directory). It contains CMS Blue Button sample FHIR R4 Patient, Coverage, and ExplanationOfBenefit examples for a single synthetic beneficiary. This replaces the earlier assumption that Synthea would be evaluated first; Synthea remains an optional future source if additional synthetic scenarios require it.

Selection does not waive provenance or privacy controls. Before the corpus is frozen as a benchmark, its source, license/usage basis, immutable version or content hashes, transformations, limitations, and synthetic classification must be recorded. Application code must treat it as read-only, untrusted input and must never write credentials, prompts, traces, or generated outputs into it.

## Alternatives considered

- **Use real claims during initial research:** rejected because it is unnecessary for inception and introduces unsupported risk and obligations.
- **Accept any dataset labeled de-identified:** rejected because labels alone do not establish permitted use or sufficient privacy protection.
- **Start with synthetic/public data and add a formal gate for regulated data:** selected.

## Consequences

### Positive

- Enables reproducible research without making PHI handling a prerequisite.
- Reduces privacy and compliance exposure during early experimentation.
- Makes controlled anomalies, adversarial cases, and benchmark versioning practical.

### Negative

- Findings may not generalize to real payer distributions, coding behavior, drift, or operational constraints.
- Synthetic labels and scenarios require careful domain review and must not be presented as evidence of production validity.

### Security implications

- Synthetic/public inputs remain untrusted and may contain malicious narratives, documents, or metadata.
- Access, logging, export, retention, and model-provider controls still apply.
- Test fixtures must be clearly marked synthetic and scanned to prevent accidental secret or real-data inclusion.

### Operational implications

- Dataset provenance, license, generator/version, perturbations, and benchmark splits must be recorded.
- Production credentials and live healthcare integrations are not needed for initial work.
