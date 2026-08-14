# Project Definition

> This document defines what the project is, why it exists, who it serves, its current scope, major constraints, and the decisions/open questions that guide architecture and task planning.
>
> Classification labels:
> - **Confirmed** — explicitly established
> - **Assumption** — temporary working assumption
> - **Recommendation** — proposed choice awaiting approval where material
> - **Open question** — unresolved item

## 1. Project Summary

### Working name

[Project name]

### One-sentence description

[What this project does in one sentence.]

### Status

[Inception / Active / Maintenance]

---

## 2. Problem Statement

### Confirmed

- [What problem is known to exist?]

### Assumptions

- [What are we currently assuming about the problem?]

---

## 3. Goals and Intended Outcomes

### Primary goal

[Main outcome the project should create.]

### Secondary goals

- [Goal]
- [Goal]

### Non-goals

- [Explicitly out of scope]
- [Explicitly out of scope]

---

## 4. Intended Users and Actors

| Actor / User | Need | Expected Interaction |
|---|---|---|
| [Actor] | [Need] | [Interaction] |

---

## 5. Core Use Cases

1. **[Use case]** — [short description]
2. **[Use case]** — [short description]
3. **[Use case]** — [short description]

---

## 6. Core Capabilities

### Confirmed

- [Capability]

### Recommended / Proposed

- [Capability]

---

## 7. Scope

### In scope

- [Item]

### Out of scope

- [Item]

### Future / possible scope

- [Item]

---

## 8. Functional Requirements

### Confirmed

- [Requirement]

### Assumptions

- [Requirement assumption]

---

## 9. Non-Functional Requirements

Consider only what is relevant:

- security
- privacy
- performance
- reliability
- scalability
- accessibility
- auditability
- observability
- maintainability
- availability
- cost constraints

### Confirmed

- [Requirement]

### Recommended

- [Recommendation]

---

## 10. Data and Privacy

### Data involved

- [Data category]

### Sensitive / regulated data

- [Known or suspected sensitive data]

### Data boundaries

- [Where data may originate, flow, and persist]

### Open privacy/compliance questions

- [Question]

> Do not claim regulatory compliance unless it has been independently established.

---

## 11. Security and Trust Boundaries

### Confirmed requirements

- [Requirement]

### Recommended controls

- [Recommendation]

### Human approval boundaries

- [Actions that must remain human-controlled]

---

## 12. External Systems and Integrations

| System / Provider | Purpose | Status |
|---|---|---|
| [System] | [Purpose] | Confirmed / Proposed / Unknown |

---

## 13. Known Constraints

### Technical

- [Constraint]

### Business / operational

- [Constraint]

### Time / resource

- [Constraint]

---

## 14. Success Criteria

The project is successful when:

- [Measurable or observable outcome]
- [Measurable or observable outcome]

---

## 15. Assumptions Register

| ID | Assumption | Why needed | Validation needed |
|---|---|---|---|
| A-001 | [Assumption] | [Reason] | [How/when to validate] |

---

## 16. Recommended Decisions

| ID | Recommendation | Rationale | Human approval needed? |
|---|---|---|---|
| R-001 | [Recommendation] | [Reason] | Yes / No |

---

## 17. Open Questions

| ID | Question | Why it matters | Blocks first task? |
|---|---|---|---|
| Q-001 | [Question] | [Impact] | Yes / No |

---

## 18. Initial Proposed Backlog

> These are proposed work items only. They are not active tasks until deliberately created with `agentctl.py`.

| Order | Task ID | Title | Purpose | Depends on |
|---:|---|---|---|---|
| 1 | FOUNDATION-001 | [Title] | [Purpose] | — |
| 2 | [TASK-ID] | [Title] | [Purpose] | FOUNDATION-001 |

### Recommended first task

**[TASK-ID] — [Title]**

Reason: [Why this should be the first tracked task.]

---

## 19. Project-Level Decisions Already Approved

- [Decision]

---

## 20. Related Repository Documents

- `docs/architecture/SYSTEM.md`
- `docs/adr/`
- `docs/standards/`
- `contracts/`
- `.ai/tasks/`
