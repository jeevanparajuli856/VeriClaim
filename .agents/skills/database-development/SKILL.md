---
name: database-development
description: Implement database-impacting tasks using Git-tracked migrations, Supabase CLI migration lifecycle when selected, and scoped MCP for development inspection/verification.
---

# Database Development

Use only when `architecture-report.json.impacts.database=true` and task status is `IMPLEMENTATION`.

## Core rule

Git-tracked migration/schema artifacts are authoritative.

For Supabase, prefer this flow:

```text
inspect approved DEV state (MCP/CLI)
        ↓
supabase migration new <description>
        ↓
write migration SQL
        ↓
local/reset test when available
        ↓
apply pending migration(s) to linked DEV with supabase db push
        ↓
inspect/verify resulting DEV state with MCP
        ↓
review RLS/indexes/advisors
        ↓
database-report.json
```

Do not make direct dashboard/MCP schema edits that are not represented by a migration file.

## Supabase rules

- use timestamped CLI-generated migration names
- use a linked DEVELOPMENT/TEST project only
- `supabase db push` promotes pending Git migrations to the currently linked DEV remote
- MCP is primarily for scoped inspection, diagnostics, advisors, verification, and generated types
- `execute_sql` is primarily diagnostic/read-only; never use it as the sole schema implementation
- write-capable MCP calls remain approval-gated
- never connect normal agent MCP to production
- never use DEV test data as production seed data

If CLI/local Supabase is unavailable, still create/review the migration and record exactly which live checks were not performed.

## Completion

Update `database-report.json`, including migration files, environment, verification, RLS/index review, advisors, blockers, and backend notes.

Run:

```bash
python scripts/agentctl.py scope check <TASK-ID> database
```

before reporting completion when working on an isolated agent branch.
