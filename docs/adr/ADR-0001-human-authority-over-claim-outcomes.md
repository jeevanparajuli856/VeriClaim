# ADR-0001 — Human authority over claim outcomes

## Status

Accepted during project inception; reaffirmed and narrowed for the one-day demo on 2026-08-15.

## Context

VeriClaim will use ML, retrieval, and AI agents to investigate healthcare payment-integrity cases. Those components can produce plausible but incorrect conclusions, encounter incomplete or conflicting policy evidence, and amplify bias in data or labels. Claim approval, denial, payment modification, recoupment, and clinical decisions are consequential actions that require accountable human authority.

## Decision

For the current milestone, VeriClaim is a local synthetic-data demonstration. It may expose deterministic anomaly signals and Gemini-generated candidate explanations, identify uncertainty or missing evidence, and suggest questions for investigation.

It must not autonomously approve, deny, adjudicate, or change payment; make a fraud determination; contact an external party as an official determination; diagnose or prescribe; or make another consequential clinical decision.

An authorized human remains responsible for consequential interpretation and downstream action. Governance failures, insufficient evidence, unsupported conclusions, and low-confidence cases are escalated rather than converted into autonomous outcomes.

## Alternatives considered

- **Autonomous adjudication:** rejected because it conflicts with the confirmed product purpose and creates unacceptable safety, legal, policy, and accountability risk.
- **Human review only above a risk threshold:** rejected as a default because thresholding does not make model-generated outcomes authoritative or eliminate evidence and bias risk.
- **Decision support with human authority:** selected.

## Consequences

### Positive

- Establishes a clear accountability boundary.
- Supports research on useful AI assistance without presenting model output as an authoritative claim decision.
- Makes escalation, uncertainty, evidence, and reviewer workflow core architecture concerns.

### Negative

- Limits automation and means model fluency cannot establish correctness.
- A formal reviewer workflow, identity system, and recorded disposition are future concerns, not one-day demo components.

### Security implications

- Agent tools must be deny-by-default and must not expose payment/adjudication side effects.
- The API wording must not misrepresent a deterministic signal or Gemini candidate explanation as a completed claim decision.
- The local demo exposes no consequential action or write tool; a future shared/deployed system would require explicit authorization boundaries.

### Operational implications

- Every demo response must state the candidate-only nature and limitations of model output.
- Any future production integration or consequential action requires a new approved decision, threat model, contract, authorization, and human-approval design.
