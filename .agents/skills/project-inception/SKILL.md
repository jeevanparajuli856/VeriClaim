---
name: project-inception
description: Convert a raw project idea into approved project source-of-truth documentation and deterministic operational configuration before implementation tasks exist.
---

# Project Inception

Use for a brand-new project before implementation tasks/worktrees exist.

## Required outputs

Create/update:
- `docs/PROJECT.md` using `.ai/templates/project.template.md`
- `docs/architecture/SYSTEM.md`
- `.ai/project.json`
- only standards justified by confirmed decisions
- ADRs only for significant approved decisions
- dependency-aware proposed backlog in `docs/PROJECT.md`

## Information classes

Keep these explicit:
- Confirmed
- Assumption
- Recommendation
- Open question

Never silently convert assumptions/recommendations into confirmed requirements.

## `.ai/project.json`

This file is operational configuration for deterministic scripts/CI, not a second product requirements document.

During inception:
- set `status` to `INCEPTION_DRAFT` while material choices remain unresolved
- set component `enabled` fields only when known
- record selected technology/provider only when confirmed
- define required project verification commands after the stack is known
- define required project security commands after the stack is known
- before `INCEPTION_READY`, resolve backend/frontend/database `enabled` to true/false
- when backend/frontend is enabled, record its selected technology
- when database is enabled, record its provider and migration path
- set `status` to `INCEPTION_READY` only when the first implementation task can be selected without unresolved platform blockers

Examples of verification checks:

```json
{
  "name": "backend-tests",
  "command": ["python", "-m", "pytest"],
  "cwd": "backend",
  "required": true
}
```

Do not invent commands for technology that has not been selected.

## Human decision policy

Stop only for material unresolved decisions affecting scope, behavior, architecture, platform/vendor, sensitive data, security/trust, cost, or required credentials/access.

## Prohibited during inception

Do not:
- implement production code
- create feature tasks/worktrees
- fabricate contracts for speculative features
- invent a stack to make templates look complete

## Completion

Use:

```text
STATUS: <INCEPTION_DRAFTED | DECISION_REQUIRED | INCEPTION_READY>
RESULT: <one concise sentence>
FILES: <comma-separated key files>
NEXT_MODE: <AUTOMATIC | HUMAN_ACTION_REQUIRED | COMPLETE>
NEXT: <one concrete next action>
```
