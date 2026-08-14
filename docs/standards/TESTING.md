# Testing Standards

Use the smallest effective layer:
- unit tests for pure logic
- integration tests for component boundaries
- contract tests for API compatibility
- end-to-end tests for critical user journeys

Always consider:
- happy path
- expected failures
- validation
- authorization boundaries
- important edge cases

Implementation-agent tests do not replace independent task testing when `architecture-report.json.impacts.testing=true`.

The tester records durable evidence in `test-report.json`; repository verification records final commit-bound evidence in `verification-report.json`.
