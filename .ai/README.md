# `.ai/` task coordination

This directory stores structured, Git-tracked coordination state.

## Single-writer rule

Only the orchestrator modifies:

`tasks/<TASK-ID>/task.json`

Worker agents write their own report files.

## Do not store here

- chain-of-thought
- secrets
- access tokens
- huge logs
- temporary model scratchpads
