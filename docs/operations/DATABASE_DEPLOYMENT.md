# Database deployment model — superseded/inactive

The 2026-08-15 project scope reset disabled the database for the one-day local demo. There is no database deployment, migration, seed, Supabase project, PostgreSQL service, pgvector dependency, or production promotion step in the active milestone.

The prior PostgreSQL/pgvector migration plan is retained in Git history and ADR-0003's historical record; it is not an active requirement. Existing `supabase/` or Docker scaffold must not be treated as approved configuration.

Any future persistence or production database work requires a new approved provider, migration path, data/security model, operational plan, and `.ai/project.json` update before task creation.
