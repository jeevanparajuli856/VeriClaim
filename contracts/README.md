# Contracts

This directory is authoritative for approved component interfaces.

- `openapi.yaml` is currently an empty placeholder. DEMO-001 must define and validate the single `POST /api/v1/analyze-demo` interface before implementation relies on it.
- `fhir/data-001/` preserves the cancelled DATA-001 compatibility-contract history. It is not an active strict-CARIN or offline-terminology dependency for the one-day demo.

Implementation agents must not silently invent or change contracts. Contract changes require feature/architecture reconciliation and validation before `CONTRACT_READY`.
