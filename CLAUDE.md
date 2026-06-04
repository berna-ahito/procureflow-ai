# ProcureFlow AI — Claude Code Instructions

You are working on ProcureFlow AI, a portfolio-grade full-stack AI workflow system.

## Product
ProcureFlow AI is an AI-ready procurement intake, approval, RFQ drafting, and audit system.

It turns messy purchase requests into structured, validated, auditable procurement data.

## Stack
- Backend: FastAPI
- Frontend: React + Vite
- Database: SQLite local-first
- AI: provider-agnostic MockProvider first
- Later AI adapters: Gemini/Groq/Ollama only if free-safe
- Deployment later: free-first only

## Windows command rules
- Use `py`, not `python`.
- Use `py -m pip`, `py -m pytest`, `py -m uvicorn`.
- Do not assume Linux-only commands.

## Build rules
- Do not build everything in one go.
- Use GSD phase workflow.
- Plan first, then execute small milestones.
- No paid APIs.
- No random dependencies.
- No one-file app.
- No autonomous spending approval.
- Deterministic approval rules first.
- AI may classify, summarize, detect missing info, recommend risk, and draft RFQ text only.
- Humans approve or reject spending.
- Every sensitive status change must create an audit log.

## Security rules
- Protect against IDOR/BOLA.
- Avoid mass assignment.
- Use separate create/update/admin schemas.
- Validate server-side.
- Add rate limiting before deployment.
- Add status transition checks.
- Add tests for approval rules and validation.
- Never commit secrets.
- Create `.env.example`, never `.env`.

## Useful skills/agents
Use relevant installed skills automatically:
- api-design
- backend-patterns
- frontend-patterns
- coding-standards
- security-review
- tdd-workflow
- verification-loop
- documentation-lookup

Do not use Obsidian, claude-mem, GraphRAG, ADK, browser automation, or agent platforms unless explicitly requested later.
