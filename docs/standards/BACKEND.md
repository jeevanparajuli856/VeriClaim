# Backend Standards

- Keep transport/route handlers thin.
- Put business logic in services/domain modules.
- Validate all external input.
- Enforce authorization server-side.
- Use explicit schemas at boundaries.
- Keep persistence logic separated where practical.
- Avoid leaking internal exceptions to clients.
- Add tests for behavior changes.
- Do not silently diverge from `contracts/openapi.yaml`.
