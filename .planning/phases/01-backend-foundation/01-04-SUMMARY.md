---
phase: "01"
plan: "04"
subsystem: backend-auth
tags: [jwt, bcrypt, security, dependency-injection, fastapi]
dependency_graph:
  requires: ["01-01", "01-02", "01-03"]
  provides: ["app/core/security.py", "app/core/deps.py"]
  affects: ["all protected routers", "01-05", "01-06", "01-07"]
tech_stack:
  added: ["bcrypt (direct API, bypassing passlib)", "python-jose"]
  patterns: ["OAuth2PasswordBearer", "FastAPI Depends factory", "require_role factory pattern"]
key_files:
  created:
    - app/core/security.py
    - app/core/deps.py
  modified: []
decisions:
  - "Used bcrypt 5.0.0 direct API instead of passlib CryptContext — passlib 1.7.4 is incompatible with bcrypt 4+"
metrics:
  duration: "~5 min"
  completed: "2026-06-04"
  tasks_completed: 2
  files_created: 2
---

# Phase 1 Plan 4: Auth Core (Security + Dependency Injection) Summary

**One-liner:** JWT encode/decode with bcrypt password hashing and FastAPI OAuth2PasswordBearer dependency injection for role-based access control.

## What Was Built

Two files implement the entire security foundation for all protected routes:

**app/core/security.py**
- `get_password_hash(password)` — bcrypt salt + hash, returns `$2b$` string
- `verify_password(plain, hashed)` — constant-time bcrypt comparison
- `create_access_token(data, expires_delta)` — encodes `user_id`, `role`, `exp` via python-jose; defaults to `settings.access_token_expire_minutes`
- `decode_access_token(token)` — jose JWT decode; propagates `JWTError` to caller

**app/core/deps.py**
- `oauth2_scheme` — `OAuth2PasswordBearer(tokenUrl="/auth/login")` reads `Authorization: Bearer` header only; never reads user identity from request body
- `get_current_user` — decodes token, extracts `user_id`, queries DB; raises 401 for missing/expired/invalid token or unknown user
- `get_current_active_user` — raises 403 if `user.is_active` is False
- `require_role(*allowed_roles)` — factory returning a dependency; raises 403 if `current_user.role not in allowed_roles`

## Verification Results

```
SECURITY CORE TESTS PASSED
DEPS IMPORTABLE
```

All acceptance criteria from the plan met:
- bcrypt hash starts with `$2b$`
- `verify_password("secretpass", hash)` returns True
- `verify_password("wrongpass", hash)` returns False
- JWT has 3 dot-separated parts
- `decode_access_token` round-trips `user_id=42`, `role="finance"`, `exp` present
- `deps.py` imports cleanly with all three dependency functions

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] passlib 1.7.4 incompatible with bcrypt 5.0.0**
- **Found during:** T01 verification
- **Issue:** `passlib.handlers.bcrypt` reads `bcrypt.__about__.__version__` which was removed in bcrypt 4+. The `hashpw` call raises `ValueError: password cannot be longer than 72 bytes` due to changed bcrypt internal API.
- **Fix:** Replaced `passlib.context.CryptContext` with direct `bcrypt` module calls (`bcrypt.gensalt()`, `bcrypt.hashpw()`, `bcrypt.checkpw()`). Removed `passlib` import from `security.py`. The bcrypt 5.0.0 direct API is stable and produces identical `$2b$12$...` hashes.
- **Files modified:** `app/core/security.py`
- **Security equivalence:** Same bcrypt work factor (12 rounds default), same `$2b$` format, same constant-time verification guarantee.

## Known Stubs

None. Both files are fully implemented with no placeholder values or deferred logic.

## Threat Flags

None. No new network endpoints introduced. `deps.py` hardens existing auth surface by extracting user identity from the JWT token only (never from request body), directly addressing IDOR/BOLA requirements from CLAUDE.md.

## Self-Check: PASSED

- `D:\Projects\procureflow-ai\app\core\security.py` — EXISTS (verified by Read)
- `D:\Projects\procureflow-ai\app\core\deps.py` — EXISTS (verified by Read)
- Files tracked in git index (`git ls-files app/core/` confirms both)
- Verification commands both returned expected output
