# Database Standards

- Database changes must be represented by explicit Git-tracked migrations/schema artifacts.
- Migrations should be deterministic, reviewable, backward-compatible where practical, and reversible where practical.
- Protect referential/domain integrity with database constraints where appropriate.
- Review indexes against real query/access patterns; avoid speculative indexing.
- Treat authorization/RLS as part of the security model, not an application convenience.
- Avoid destructive schema changes without an explicit migration/data-backfill/rollback plan.
- Never run destructive production statements without human approval.

## Supabase

When Supabase is selected:
- create migrations with `supabase migration new <description>` so filenames use the CLI timestamp convention
- test locally with `supabase db reset` when local Supabase is available
- deploy pending reviewed migrations to the linked DEV project with `supabase db push`
- use project-scoped DEV MCP primarily for inspection, diagnostics, advisors, verification, and type generation
- do not use MCP/direct dashboard edits as the only representation of schema change
- production deployment promotes the reviewed migrations separately after PR approval/merge
