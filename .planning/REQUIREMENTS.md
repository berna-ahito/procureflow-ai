# ProcureFlow AI — Requirements

## Functional Requirements

### FR-AUTH: Authentication
- FR-AUTH-1: `POST /auth/login` accepts `{email, password}`, returns `{access_token, token_type}`
- FR-AUTH-2: All non-public endpoints require `Authorization: Bearer <token>`
- FR-AUTH-3: Tokens encode `user_id`, `role`, `exp`
- FR-AUTH-4: Expired/invalid tokens return 401

### FR-USERS: User Management
- FR-USERS-1: Users have `id, email, hashed_password, full_name, role, department_id, is_active`
- FR-USERS-2: Roles: `requester | manager | finance | admin`
- FR-USERS-3: Admin can create/deactivate users
- FR-USERS-4: Seed script creates one user per role for dev/test

### FR-REQUESTS: Purchase Request Lifecycle
- FR-REQ-1: Requester submits request: `title, description, category, urgency, quantity, estimated_cost, vendor_id (optional), justification`
- FR-REQ-2: Backend validates all fields server-side (no trust of client)
- FR-REQ-3: New request status = `draft`
- FR-REQ-4: Requester submits draft → status becomes `pending_review`
- FR-REQ-5: Requester can view only own requests (IDOR protection)
- FR-REQ-6: Manager/finance can view requests routed to them
- FR-REQ-7: Admin can view all requests
- FR-REQ-8: Separate create schema, update schema, admin schema (no mass assignment)

### FR-APPROVAL: Approval Rules Engine
- FR-APPR-1: `approval_rules` table: `id, name, min_amount, max_amount, category (nullable), required_role, priority`
- FR-APPR-2: Engine evaluates rules in priority order; first match wins
- FR-APPR-3: Match result assigns `assigned_role` and updates request status to `pending_approval`
- FR-APPR-4: If no rule matches, request is flagged `needs_rule` (not auto-approved)
- FR-APPR-5: Approver records decision: `approved | rejected | needs_more_info`
- FR-APPR-6: `needs_more_info` returns request to `draft` with a note
- FR-APPR-7: Approved → status `approved`. Rejected → status `rejected`.
- FR-APPR-8: AI-derived recommended_action is advisory only; human decision is recorded separately

### FR-AI: AI Review Service
- FR-AI-1: AI review triggers on `pending_review` status
- FR-AI-2: Provider-agnostic interface: `AIReviewProvider.review(request) → AIReviewResult`
- FR-AI-3: `AIReviewResult` fields:
  - `category: str` + `category_confidence: float (0–1)`
  - `urgency: str (low|medium|high|critical)` + `urgency_confidence: float`
  - `risk_level: str (low|medium|high)` + `risk_confidence: float`
  - `missing_info: list[str]` + `missing_info_confidence: float`
  - `summary: str` + `summary_confidence: float`
  - `recommended_action: str` + `recommended_action_confidence: float`
  - `rfq_draft: str` + `rfq_draft_confidence: float`
  - `provider: str`
  - `reviewed_at: datetime`
- FR-AI-4: `MockProvider` returns deterministic plausible values based on request fields
- FR-AI-5: AI review stored in `ai_reviews` table, linked to request
- FR-AI-6: AI result is visible to approver as context, not as a decision

### FR-AUDIT: Audit Logging
- FR-AUDIT-1: Every status change writes an `audit_log` row
- FR-AUDIT-2: `audit_log`: `id, request_id, actor_id, action, old_status, new_status, note, created_at`
- FR-AUDIT-3: Audit log is append-only (no updates or deletes)
- FR-AUDIT-4: Audit log visible to admin

### FR-FRONTEND: UI (3-screen SPA)
- FR-FE-1: Login screen (email/password → JWT stored in localStorage)
- FR-FE-2: Dashboard (list of requests visible to current user, status badges, filters)
- FR-FE-3: Submit request form (all fields, client-side validation mirrors server)
- FR-FE-4: Request detail view: full fields + AI review panel + approve/reject/needs-info actions
- FR-FE-5: Role-aware: submit button only for `requester`, approve/reject only for `manager/finance`

## Non-Functional Requirements

### NFR-SECURITY
- NFR-SEC-1: No secrets in source. `.env.example` only.
- NFR-SEC-2: IDOR check on every request ID access (owner or authorized role only)
- NFR-SEC-3: Rate limiting on auth and submission endpoints before deployment
- NFR-SEC-4: Status transitions validated server-side; no client-driven status jumps
- NFR-SEC-5: Passwords hashed with bcrypt (passlib)

### NFR-TESTING
- NFR-TEST-1: 80% coverage minimum on approval engine and validation
- NFR-TEST-2: Tests for all status transition rules
- NFR-TEST-3: Tests for IDOR enforcement
- NFR-TEST-4: httpx-based API integration tests

### NFR-CODE
- NFR-CODE-1: No one-file app. Module structure enforced.
- NFR-CODE-2: Separate Pydantic schemas: `Create`, `Update`, `AdminUpdate`, `Response`
- NFR-CODE-3: No random dependencies. Justify each package.
- NFR-CODE-4: Windows-compatible commands only (`py`, not `python`)
