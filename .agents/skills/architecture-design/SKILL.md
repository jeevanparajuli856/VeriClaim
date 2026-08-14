---
name: architecture-design
description: Design task-level architecture and produce machine-readable component impact needed by orchestration gates.
---

# Architecture Design Workflow

1. Read project/task source-of-truth, relevant ADRs, standards, contracts, and existing code.
2. Define only architecture required by this task.
3. Identify components, data flow, trust boundaries, failure modes, dependencies, migration impact, and security implications.
4. Do not silently introduce project-wide decisions.
5. Create an ADR only for significant decisions that are actually justified/approved.
6. Update `architecture-report.json`.

Before setting the report `COMPLETE`, set every impact field explicitly to `true` or `false`:
- `database`
- `backend`
- `frontend`
- `infrastructure`
- `testing`
- `contract_change`

These flags control which implementation workers the orchestrator should run. Do not leave them `null` when complete.
