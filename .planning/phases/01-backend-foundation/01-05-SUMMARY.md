---
phase: "01"
plan: "05"
subsystem: backend-auth
tags: [auth, users, seed, jwt, fastapi]
dependency_graph:
  requires: ["01-03", "01-04"]
  provides: ["auth-router", "users-router", "seed-data"]
  affects: ["app/main.py", "app/routers/auth.py", "app/routers/users.py", "scripts/seed.py"]
tech_stack:
  added: []
  patterns: ["JWT login flow", "role-based access control via Depends", "idempotent seed"]
key_files:
  created:
    - app/routers/auth.py
    - app/routers/users.py
    - scripts/seed.py
  modified:
    - app/main.py
decisions:
  - "POST /auth/login accepts email+password, returns {access_token, token_type} — no refresh token at MVP"
  - "require_role() dependency pattern used for RBAC — admin-only on POST/PATCH /users/"
  - "Seed is idempotent via check-before-insert (not upsert) to keep logic transparent"
  - "PATCH /users/{id} applies only non-None fields via model_dump(exclude_none=True) to prevent mass assignment"
metrics:
  duration: "~3 min"
  completed: "2026-06-04"
  tasks_completed: 4
  files_modified: 4
---

# Phase 01 Plan 05: Auth Router, Users Router, and Seed Data Summary

**One-liner:** JWT login endpoint, role-gated user management, and idempotent demo seed covering all four roles.

## Tasks Completed

| Task | Description | Status |
|------|-------------|--------|
| T01 | Created app/routers/auth.py — POST /auth/login | Done |
| T02 | Created app/routers/users.py — GET /me, POST /, PATCH /{id} | Done |
| T03 | Created scripts/seed.py — departments, vendors, users, approval rules | Done |
| T04 | Updated app/main.py to register auth and users routers | Done |

## What Was Built

### app/routers/auth.py
- `POST /auth/login` — accepts `LoginRequest(email, password)`, validates against DB, returns `Token(access_token, token_type)`
- Uses `verify_password` (direct bcrypt) and `create_access_token` from `app.core.security`
- Returns 401 with `WWW-Authenticate: Bearer` header for invalid credentials
- No auth on this endpoint itself (it is the login endpoint)

### app/routers/users.py
- `GET /users/me` — any authenticated active user; returns `UserResponse` from JWT-derived user
- `POST /users/` — admin only; creates user with hashed password, checks email uniqueness (400 if dup)
- `PATCH /users/{user_id}` — admin only; partial update via `model_dump(exclude_none=True)`, 404 if missing
- Never exposes `hashed_password` (not in `UserResponse` schema)

### scripts/seed.py
- Seeds: 3 departments (IT, Finance, Operations), 2 vendors, 4 users (one per role), 3 approval rules
- Idempotent: queries before inserting, prints count of newly created records per category
- Second run prints all zeros — no duplicates

### app/main.py
- Registers `auth.router` and `users.router` via `app.include_router()`
- Health check endpoint preserved

## Verification Steps (run in order)

```powershell
# 1. Apply migrations
py -m alembic upgrade head

# 2. Run seed (first run)
py scripts/seed.py
# Expected:
#   Seeded departments: 3
#   Seeded vendors: 2
#   Seeded users: 4
#   Seeded approval rules: 3
#   Seed complete.

# 3. Verify server starts with no import errors
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# Then Ctrl+C

# 4. Verify routers importable
py -c "from app.routers.auth import router; from app.routers.users import router; print('ROUTERS OK')"
# Expected: ROUTERS OK

# 5. Run seed again (idempotency check)
py scripts/seed.py
# Expected: all counts = 0, "Seed complete."
```

## Deviations from Plan

None — plan executed exactly as written.

## Security Notes

- Passwords hashed with bcrypt direct API (consistent with existing security.py pattern)
- Seed passwords are dev-only values (`alice123`, `bob123`, `carol123`, `admin123`) — not production credentials
- No plaintext passwords stored or logged
- PATCH /users/{id} uses `model_dump(exclude_none=True)` to guard against mass assignment
- `UserResponse` schema does not include `hashed_password` field

## Known Stubs

None — all endpoints are fully wired.

## Self-Check

- [x] app/routers/auth.py exists with POST /auth/login
- [x] app/routers/users.py exists with GET /me, POST /, PATCH /{id}
- [x] scripts/seed.py exists, idempotent, no plaintext passwords
- [x] app/main.py includes both routers
- [x] All imports resolve against confirmed-existing modules (security.py, deps.py, base.py, models.py, schemas/)
