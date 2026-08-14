# Contracts

This directory is authoritative for interfaces between system components.

- `openapi.yaml` — HTTP API contract
- `schemas/` — shared JSON schemas
- `events/` — asynchronous event contracts

Frontend and backend implementations must follow these contracts.

Do not silently change a contract during implementation.
