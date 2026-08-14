# Git Standards

## Branches

Feature:
`feature/<TASK-ID>-short-name`

Parallel workers:
- `agent/<TASK-ID>-backend`
- `agent/<TASK-ID>-frontend`

Bug tasks still use the same task-scoped feature branch unless the project deliberately adopts a different convention.

## Rules

- never implement directly on main/master
- prepare the feature branch with `python scripts/agentctl.py git prepare <TASK-ID>`
- commit planning/task/contract state before creating worker worktrees
- keep commits focused and reviewable
- do not force-push shared branches without explicit approval
- worker branches must pass their role scope check before completion
- integrated verification/security/review evidence must reference the final reviewed commit
