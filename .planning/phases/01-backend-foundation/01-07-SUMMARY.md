---
phase: "01"
plan: "07"
subsystem: backend
tags: [fastapi, routers, requests, approvals, audit, idor-protection, role-based-access]
dependency_graph:
  requires: [01-02, 01-03, 01-04, 01-05, 01-06]
  provides: [requests-router, approvals-router, audit-router]
  affects: [app/main.py]
tech_stack:
  added: []
  patterns: [role-scoped-query-filtering, status-transition-enforcement, audit-logging-on-write]
key_files:
  created:
    - app/routers/requests.py
    - app/routers/approvals.py
    - app/routers/audit.py
  modified:
    - app/main.py
decisions:
  - IDOR guard extracted to _get_request_or_403 helper for reuse across get/update/submit
  - Manager and finance filters use OR to include own requests as well as assigned-role requests
  - Approvals router persists ApprovalDecision record AND writes audit log in the same transaction boundary
metrics:
  duration: "~4 min"
  completed: "2026-06-04T13:33:49Z"
  tasks_completed: 4
  files_created: 3
  files_modified: 1
---

# Phase 01 Plan 07: Requests, Approvals, and Audit Routers Summary

**One-liner:** Three FastAPI routers (requests CRUD, approval decisions + rules management, admin audit trail) wired into main.py, covering 12 total routes with role-scoped access and IDOR protection throughout.

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| T01 | Create app/routers/requests.py | f2c2ab2 | app/routers/requests.py |
| T02 | Create app/routers/approvals.py | 8b093ba | app/routers/approvals.py |
| T03 | Create app/routers/audit.py | 3837e76 | app/routers/audit.py |
| T04 | Update app/main.py with all 3 routers | 2e8606a | app/main.py |

## What Was Built

### requests router (`/requests`)

- `POST /requests/` — creates a draft PurchaseRequest (requester role only); no mass assignment; fields explicitly mapped from schema to model
- `GET /requests/` — role-scoped list: requesters see own; managers see assigned-to-manager OR own; finance sees assigned-to-finance OR own; admins see all
- `GET /requests/{id}` — fetch single request via `_get_request_or_403` IDOR guard
- `PATCH /requests/{id}` — update draft only (requester, draft status enforced); uses `model_dump(exclude_none=True)` to avoid overwriting fields
- `POST /requests/{id}/submit` — transitions draft to pending_review, routes via approval_engine, writes two audit log entries (submitted + routed)

### approvals router (`/approvals`)

- `POST /approvals/{id}/decide` — approve/reject/needs_more_info; validates assigned_role matches actor (admin exempt); status must be pending_approval; persists ApprovalDecision record; audit logged
- `GET /approvals/rules` — list active ApprovalRules ordered by priority (admin only)
- `POST /approvals/rules` — create new ApprovalRule (admin only); explicit field mapping, no mass assignment

### audit router (`/audit`)

- `GET /audit/requests/{id}` — per-request audit trail ascending (admin only)
- `GET /audit/` — most recent 100 entries descending (admin only)

### main.py

All 5 routers now registered: auth, users, requests, approvals, audit.

## Verification Results

Import check passed:
```
ALL ROUTERS OK
```

Server startup: no errors, application startup complete.

OpenAPI routes confirmed:
```
/approvals/rules
/approvals/{request_id}/decide
/audit/
/audit/requests/{request_id}
/auth/login
/health
/requests/
/requests/{request_id}
/requests/{request_id}/submit
/users/
/users/me
/users/{user_id}
```

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None. All endpoints wire to real DB models and services.

## Threat Flags

No new threat surface beyond what the plan defined. IDOR protection is present on all request-scoped endpoints via `_get_request_or_403`. Audit log is written for every state-changing action (submit, route, decide).

## Self-Check: PASSED

- app/routers/requests.py: FOUND
- app/routers/approvals.py: FOUND
- app/routers/audit.py: FOUND
- app/main.py updated: FOUND
- f2c2ab2: FOUND (T01)
- 8b093ba: FOUND (T02)
- 3837e76: FOUND (T03)
- 2e8606a: FOUND (T04)
