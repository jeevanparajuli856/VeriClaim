# Backend Agent Instructions

These rules specialize the root `AGENTS.md`.

- Backend owns server-side validation and authorization.
- Keep route/controller handlers thin.
- Keep business logic separated from transport code.
- Use explicit boundary schemas.
- Add tests for behavior changes.
- Do not silently modify `contracts/`.
