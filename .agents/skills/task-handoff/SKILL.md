---
name: task-handoff
description: Produce or consume structured handoff reports between Codex, Gemini, reviewers, and the orchestrator.
---

# Task Handoff Workflow

## Producer

1. Do not modify `task.json` unless you are the orchestrator.
2. Write your own report file.
3. Include:
   - status
   - summary
   - files changed
   - contracts used
   - tests
   - blockers
   - notes for next agent

## Consumer

1. Read `task.json`.
2. Read prior reports.
3. Read current contracts.
4. Verify assumptions against repository state.
5. Never rely only on prose from chat history.

## Blocker types

- `CONTRACT_CHANGE_REQUIRED`
- `ARCHITECTURE_DECISION_REQUIRED`
- `SECURITY_REVIEW_REQUIRED`
- `DEPENDENCY_BLOCKED`
- `TEST_FAILURE`
