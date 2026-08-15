# Operator quickstart

The repo carries the tracked lifecycle through `python scripts/agentctl.py ...` (use `python3` only on systems where `python` is not installed as an alias).

## Current next action

After reviewing the approved re-inception artifacts, the human may authorize the single proposed task:

```text
Approve DEMO-001 as the implementation task.
Proceed using AGENTS.md and the task-orchestration skill.
Continue automatically until human action is genuinely required.
```

DEMO-001 does not exist until that authorization is given and `agentctl.py task create` is run. No separate frontend or Gemini frontend worktree is needed because FastAPI `/docs` is the demonstration interface.

## Generic lifecycle reminders

- Normal progress uses `python scripts/agentctl.py task advance <TASK-ID>`.
- Administrative recovery/cancellation uses `task status` only when justified.
- Implementation must not occur on `main`/`master`.
- The feature branch is prepared only after task creation.
- Verification, security review, final review, and human PR/merge remain evidence gates under `AGENTS.md`.
