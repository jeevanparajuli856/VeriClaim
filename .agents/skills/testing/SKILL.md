---
name: testing
description: Independently design, implement, and execute tests against the integrated task revision and record durable evidence.
---

# Testing Workflow

1. Read acceptance criteria, architecture impacts, contracts, implementation reports, and integrated code.
2. Design the smallest deterministic test set that proves required behavior.
3. Cover happy paths, failures, validation, authorization boundaries, and important edge cases.
4. Add tests only under paths allowed by `permissions.tester`.
5. Run the exact relevant commands.
6. Do not hide skipped/flaky tests.
7. Update `.ai/tasks/<TASK-ID>/test-report.json`.
8. Set `tests.passed=true` only when required tests genuinely pass.
9. Run `python scripts/agentctl.py scope check <TASK-ID> tester` when working on an isolated branch.
