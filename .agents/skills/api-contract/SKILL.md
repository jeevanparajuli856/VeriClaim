---
name: api-contract
description: Create or modify API contracts between components, especially frontend and backend.
---

# API Contract Workflow

1. Read the feature task and specification.
2. Read existing `contracts/openapi.yaml`.
3. Identify affected endpoints.
4. Define request schemas.
5. Define response schemas.
6. Define authentication/authorization expectations.
7. Define error responses and status codes.
8. Define pagination/filtering/idempotency when applicable.
9. Update the OpenAPI contract before implementation.
10. Validate the contract.
11. Frontend and backend must implement the contract rather than invent behavior.
