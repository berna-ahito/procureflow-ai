# ProcureFlow AI — Project Context

## Mission

Turn messy employee purchase requests into structured, validated, auditable procurement data. AI assists but never decides. Humans approve or reject spending.

## Users & Roles

| Role | Can Do |
|------|--------|
| `requester` | Submit purchase requests, view own requests |
| `manager` | Approve/reject requests routed to them, view team requests |
| `finance` | Approve/reject high-value requests, view all requests |
| `admin` | Manage approval rules, users, departments, vendors |

Auth: JWT login. `POST /auth/login` → bearer token. Token required on all protected endpoints.

## Core Workflow

1. Requester submits purchase request (item, quantity, estimated cost, justification, category, urgency).
2. Backend validates and stores request.
3. AI review service runs synchronously: returns category, urgency, risk_level, missing_info, summary, recommended_action, rfq_draft — all with confidence scores.
4. Approval rules engine determines routing: which role(s) must approve, based on configurable DB rules.
5. Notified approver(s) approve, reject, or request more info.
6. Every sensitive status change is written to audit_log.

## AI Boundary (hard rule)

AI may: classify, summarize, detect missing info, assign risk label, recommend action, draft RFQ text.
AI must never: approve or reject spending. That is always a human action.

## Non-Goals (MVP)

- No email/notification system
- No file attachments
- No multi-currency or tax calculations
- No OAuth / SSO
- No vendor portal / external access
- No real-time websocket updates
- No paid AI APIs

## Constraints

- Windows development (use `py`, not `python`)
- SQLite local-first (no Postgres until deployment need is real)
- No paid APIs
- Free-first deployment only
- MockProvider as the only AI provider for MVP
- Coverage target: 80% on approval logic and validation

## Stack

| Layer | Choice |
|-------|--------|
| Backend | FastAPI |
| ORM | SQLAlchemy (async-optional, sync-first for simplicity) |
| DB | SQLite via SQLAlchemy |
| Migrations | Alembic |
| Auth | python-jose + passlib (bcrypt) |
| Validation | Pydantic v2 |
| Tests | pytest + httpx |
| Frontend | React + Vite |
| HTTP client | axios or fetch |
| AI (MVP) | MockProvider (internal) |
| AI (later) | Gemini free tier / Groq free tier / Ollama |

## Portfolio Goal

Demonstrate: full-stack AI workflow design, security-conscious backend, human-in-the-loop AI pattern, clean API design, tested business logic.
