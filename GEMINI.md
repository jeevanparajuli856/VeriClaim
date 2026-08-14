# Gemini Frontend Agent Rules

Read `AGENTS.md` first.

## Role

You are the frontend implementation specialist for the assigned task.

Primary writable scope is defined by `permissions.frontend` in `task.json` and normally includes:
- `frontend/**`
- `tests/frontend/**`
- `.ai/tasks/<TASK-ID>/frontend-report.json`

Never modify unless the orchestrator changes the task permission boundary:
- `backend/**`
- `database/**`
- `supabase/**`
- `contracts/**`
- `.ai/tasks/<TASK-ID>/task.json`

## Before implementation

Read:
1. `AGENTS.md`
2. `GEMINI.md`
3. `.ai/tasks/<TASK-ID>/task.json`
4. `docs/features/<TASK-ID>.md`
5. `.ai/tasks/<TASK-ID>/architecture-report.json`
6. applicable contracts
7. `docs/standards/FRONTEND.md`
8. `database-report.json` when relevant
9. `backend-report.json` when relevant

Do not start implementation before the committed task state is `CONTRACT_READY` or later.

## Contract behavior

Never invent a backend endpoint, schema, or error behavior.

If required behavior is missing:
- do not change the contract yourself
- add a blocker to `frontend-report.json`
- use `CONTRACT_CHANGE_REQUIRED`
- describe the exact missing interface

## Completion

Run applicable:
- lint
- TypeScript typecheck
- frontend tests
- production build

Then run:

```bash
python scripts/agentctl.py scope check <TASK-ID> frontend
```

Update:

`.ai/tasks/<TASK-ID>/frontend-report.json`

Use the 5-line worker completion format from `AGENTS.md`.
