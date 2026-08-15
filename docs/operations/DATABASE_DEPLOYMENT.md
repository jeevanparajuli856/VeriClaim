# Database deployment model

## Development

The approved inception platform uses local PostgreSQL with pgvector. Schema changes must be represented by reviewed, Git-tracked migrations under `database/migrations/`; the exact migration tool and file format are selected during PLATFORM-001.

```text
Database agent
  ↓
create migration under database/migrations/
  ↓
test against the local PostgreSQL/pgvector development service
  ↓
record schema/integrity/authorization verification
  ↓
database-report.json
```

Development contains only approved synthetic/public data. Managed database hosting is not selected, and the pre-existing `supabase/` scaffold is not evidence that Supabase has been approved.

## Production

Production database hosting and deployment are not approved during inception. A later provider decision must define backup/recovery, encryption/key ownership, migration promotion, rollback, access control, residency, monitoring, and protected credentials. Production promotion will apply the same reviewed Git migration history through an approved human/CI gate; it will never copy the development database or development rows into production.

If Supabase is selected later, follow the conditional Supabase lifecycle in `docs/standards/DATABASE.md` and update `.ai/project.json` before implementation relies on it.
