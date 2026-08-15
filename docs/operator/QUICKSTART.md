# Operator quickstart

The repo carries the tracked lifecycle through `python scripts/agentctl.py ...` (use `python3` only on systems where `python` is not installed as an alias).

## Current next action

DEMO-001 is an active tracked implementation task. Its current lifecycle state is authoritative in
`.ai/tasks/DEMO-001/task.json`; normal advancement must use `python scripts/agentctl.py task advance DEMO-001`
so repository evidence gates are enforced. No separate frontend or Gemini frontend worktree is needed because
FastAPI `/docs` is the demonstration interface.

## Generic lifecycle reminders

- Normal progress uses `python scripts/agentctl.py task advance <TASK-ID>`.
- Administrative recovery/cancellation uses `task status` only when justified.
- Implementation must not occur on `main`/`master`.
- The feature branch is prepared only after task creation.
- Verification, security review, final review, and human PR/merge remain evidence gates under `AGENTS.md`.
