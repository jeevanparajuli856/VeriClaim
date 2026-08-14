# Database deployment model

## Development

For Supabase projects:

```text
Database agent
  ↓
create timestamped migration in Git
  ↓
local/reset test when available
  ↓
supabase db push to linked DEV project
  ↓
MCP inspection / RLS / advisor verification
  ↓
database-report.json
```

The DEV project contains non-production data.

## Production

Production is a separate deployment target.

After PR approval/merge, apply the same reviewed migration history to production deliberately:

```bash
supabase link --project-ref <PROD_PROJECT_REF>
supabase db push
```

`db push` applies pending migration files from the repository. It does not copy the DEV database or DEV test rows into production.

For mature projects, replace the local production command with CI/CD using protected production credentials and a human merge/approval gate.
