---
name: task-orchestration
description: Orchestrate a tracked development task through evidence-gated planning, implementation, verification, security, review, and PR readiness.
---

# Task Orchestration

Use `python scripts/agentctl.py ...` for deterministic lifecycle operations.

## 1. Create and branch

```bash
python scripts/agentctl.py task create <TASK-ID> "<TITLE>"
python scripts/agentctl.py git prepare <TASK-ID>
python scripts/agentctl.py task advance <TASK-ID>
```

The last command moves `PROPOSED → PLANNING` after validation.

## 2. Architecture

Spawn architect. It must complete `architecture-report.json` with explicit impact booleans.

Then:

```bash
python scripts/agentctl.py task advance <TASK-ID>
```

The gate refuses `ARCHITECTURE_READY` if architecture evidence is incomplete/blocked.

## 3. Contract

Define only required interfaces. Validate them.

```bash
python scripts/agentctl.py task advance <TASK-ID>
```

This gate validates the task/reports and OpenAPI contract before `CONTRACT_READY`.

Commit task/spec/architecture/contracts before creating implementation worktrees.

Then:

```bash
python scripts/agentctl.py task advance <TASK-ID>
```

moves to `IMPLEMENTATION`.

## 4. Spawn only required workers

Read `architecture-report.json.impacts`.

- database=true → database agent first
- backend=true → backend agent
- frontend=true → prepare Gemini worktree and ask human to start Gemini
- testing=true → tester after integration

Do not spawn specialists whose impact is false.

For parallel backend/frontend:

```bash
python scripts/agentctl.py worktree create <TASK-ID> backend
python scripts/agentctl.py worktree create <TASK-ID> frontend
```

Workers must run their scope check before completion.

After required implementation reports are COMPLETE:

```bash
python scripts/agentctl.py task advance <TASK-ID>
```

moves to `INTEGRATION`.

## 5. Integrate and test

Integrate approved worker branches onto the feature branch. Resolve conflicts deliberately; do not silently change contracts/architecture.

If testing impact is true, spawn tester. Tester writes `test-report.json` and must report passing tests.

Commit the integrated feature revision, then run:

```bash
python scripts/agentctl.py verify <TASK-ID>
```

This creates `verification-report.json` tied to the current Git commit. Any later implementation, requirement, architecture, contract, implementation-report, or test-evidence change makes that evidence stale and requires the affected verification/review stages to run again. Status-only task updates and expected downstream review report files are metadata and do not by themselves stale earlier evidence.

Then:

```bash
python scripts/agentctl.py task advance <TASK-ID>
```

moves to `SECURITY_REVIEW` only when test/verification evidence passes.

## 6. Security

Spawn security agent on the current integrated commit. It writes `security-report.json`, including `reviewed_commit`.

Security does not modify production implementation.

Advance only after APPROVED:

```bash
python scripts/agentctl.py task advance <TASK-ID>
```

## 7. Final review

Spawn reviewer. It reviews project/task/spec/architecture/contracts/reports/tests/verification/security/final diff and writes `review-report.json` with `reviewed_commit`.

Then:

```bash
python scripts/agentctl.py task advance <TASK-ID>
```

The gate reaches `PR_READY` only if verification, security, and final review all cover current HEAD and pass.

## 8. Human merge and closure

Human reviews/merges PR.

After the merge is actually complete:

```bash
python scripts/agentctl.py task advance <TASK-ID> --merged
```

## Blockers

Use structured categories such as:
- CONTRACT_CHANGE_REQUIRED
- ARCHITECTURE_DECISION_REQUIRED
- DATABASE_PROVIDER_DECISION_REQUIRED
- DATABASE_ACCESS_REQUIRED
- MIGRATION_CONFLICT
- DATA_MIGRATION_RISK
- RLS_POLICY_DECISION_REQUIRED
- DEPENDENCY_BLOCKED
- TEST_FAILURE
- PERMISSION_BOUNDARY_REQUIRED

Workers use the deterministic 5-line output from `AGENTS.md`.
