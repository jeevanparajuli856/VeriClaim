# Contracts

This directory is authoritative for approved component interfaces.

- `openapi.yaml` defines the implemented bodyless `POST /api/v1/analyze-demo` interface, including deterministic success/fallback and sanitized pipeline-error responses. FRONTEND-001 consumes this unchanged contract and generates TypeScript types from it.
- `fhir/data-001/` preserves the cancelled DATA-001 compatibility-contract history. It is not an active strict-CARIN or offline-terminology dependency for the one-day demo.

Implementation agents must not silently invent or change contracts. Contract changes require feature/architecture reconciliation and validation before `CONTRACT_READY`.
