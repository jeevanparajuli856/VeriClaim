# Database standards — inactive for current milestone

The one-day VeriClaim demo has no database. `.ai/project.json` sets `components.database.enabled` to `false`; all processing and output are in memory, and `dataset/` is read-only input.

The former PostgreSQL/pgvector/Supabase/migration direction was superseded on 2026-08-15. Existing database/Supabase scaffold does not select a provider and must not be used by DEMO-001.

If persistence becomes a future approved component, choose a provider and migration path through project/architecture reconciliation before implementation. Database changes must then be Git-tracked, deterministic, tested, and deployed through an explicit human/CI gate; no live database state may be the only source of truth.
