# Security Standards

## Baseline

- least privilege
- secure defaults
- explicit authorization
- input validation
- output encoding where needed
- secure secret handling
- dependency review
- auditability

## Forbidden

- hard-coded credentials
- production secrets in Git
- disabled certificate verification without explicit justification
- authorization based only on frontend state
- destructive production operations without human approval

## Reviews should consider

- authentication
- authorization
- IDOR/BOLA
- injection
- SSRF
- XSS
- CSRF where applicable
- insecure deserialization
- file upload risk
- secret exposure
- logging/privacy
- rate limiting
- dependency/supply-chain risk
