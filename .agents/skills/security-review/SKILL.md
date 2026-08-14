---
name: security-review
description: Independently review the exact integrated commit for security risk and record structured release-blocking evidence.
---

# Security Review Workflow

Review:
- authentication and authorization
- trust boundaries
- secrets and credentials
- sensitive data flow/privacy
- input validation/injection
- SSRF/deserialization/file handling
- database/RLS authorization where relevant
- dependency and configuration risk
- logging/audit exposure
- rate limiting/abuse controls where relevant
- MCP/tool permissions and external-system boundaries

Do not modify production code.

Write only `security-report.json`.

Set `reviewed_commit` to the exact `git rev-parse HEAD` reviewed.

Each finding records severity, category, description, impact, remediation, and whether it blocks release.

Use `APPROVED` only when no unresolved blocking finding remains.

Before completion, run:

```bash
python scripts/agentctl.py scope check <TASK-ID> security
```

when operating in the task worktree/branch so any accidental non-report write is caught before handoff.
