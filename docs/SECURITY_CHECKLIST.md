# Security Checklist

- No secrets committed
- `.env.example` only
- Server-side validation
- Separate create/update/admin schemas
- IDOR/BOLA checks on request IDs
- No mass assignment
- Deterministic status transitions
- Audit logs for sensitive actions
- Rate limiting before deployment
- Tests for approval rules
- Tests for validation
- No paid APIs
- No autonomous spending approval
