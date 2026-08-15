# Testing standards

Use the smallest effective layer:

- unit tests for Patient/Coverage/EOB extraction, stable evidence IDs, and every deterministic rule;
- integration tests for `POST /api/v1/analyze-demo`, response separation, and the model-client boundary;
- contract tests for the approved OpenAPI/Pydantic response; and
- source-integrity checks proving `dataset/` remains unchanged.

The one-day milestone must cover happy paths, malformed/unsupported local input, missing evidence, rule no-signal/signal cases, provider/configuration timeout or error, invalid model JSON/schema, unknown model evidence references, and enforcement of one call with no tools. Model tests use a fake/stub client and must not require live credentials.

Implementation tests do not replace independent task testing when architecture marks testing impact. The tester records durable evidence in `test-report.json`; repository verification records commit-bound evidence in `verification-report.json`.
