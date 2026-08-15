# ADR-0001 — Human authority over claim outcomes

## Status

Accepted during project inception.

## Context

VeriClaim will use ML, retrieval, and AI agents to investigate healthcare payment-integrity cases. Those components can produce plausible but incorrect conclusions, encounter incomplete or conflicting policy evidence, and amplify bias in data or labels. Claim approval, denial, payment modification, recoupment, and clinical decisions are consequential actions that require accountable human authority.

## Decision

VeriClaim is a decision-support and research platform. It may prioritize a synthetic claim for review, assemble evidence, retrieve policy, explain signals, identify uncertainty, and recommend further investigation.

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

- Requires reviewer workflow, role enforcement, and auditable human disposition.
- Limits straight-through automation and means model accuracy alone cannot establish system success.

### Security implications

- Agent tools must be deny-by-default and must not expose payment/adjudication side effects.
- Authorization must distinguish research/recommendation capabilities from human-controlled actions.
- UI wording and APIs must not misrepresent an AI finding as a completed claim decision.

### Operational implications

- Every analyst-ready case needs an explicit governance status and human-review state.
- Any future production integration that adds consequential actions requires a new approved decision, threat model, contract, and human-approval design.

