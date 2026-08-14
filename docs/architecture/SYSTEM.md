# System Architecture

> Replace this template with the real project architecture during project bootstrap.

## System summary

Describe:
- project purpose
- major user types
- major services
- primary data stores
- external integrations

## Components

### Frontend

Framework: TBD

Responsibilities:
- user interface
- browser state
- client-side validation
- API consumption

### Backend

Framework: TBD

Responsibilities:
- business logic
- authorization
- API implementation
- integrations

### Database

Technology: TBD

### Infrastructure

Technology: TBD

## Data flow

```text
User
  ↓
Frontend
  ↓
API
  ↓
Backend
  ↓
Database / External services
```

## Trust boundaries

Document:
- browser boundary
- API boundary
- service-to-service boundary
- data store boundary
- external provider boundary

## Security architecture

Document:
- authentication
- authorization
- secrets management
- encryption
- audit logging
- sensitive data handling

## Observability

Document:
- logs
- metrics
- traces
- alerts
