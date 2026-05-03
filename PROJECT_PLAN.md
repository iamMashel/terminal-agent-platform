# Terminal Agent Platform — Codex Build Plan

## Product Goal
Build a production-grade full-stack AI terminal assistant that helps developers understand, generate, review, approve, and safely execute terminal commands.

The system must be built using spec-driven development and implemented incrementally.

## Core Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Nuxt 4 + TypeScript | User interface, chat, sessions, command approval |
| Backend | FastAPI + Python | API, orchestration, validation, persistence |
| Agent | LangGraph + Anthropic Claude | Planning, command proposal, explanations |
| Execution | Docker sandbox | Safe isolated command execution |
| Database | PostgreSQL + SQLAlchemy | Sessions, messages, commands, execution logs |
| Realtime | Server-Sent Events | Streaming agent and execution output |
| Observability | Langfuse + structured logs | Agent tracing and debugging |
| DevOps | Docker Compose + GitHub Actions | Local development and CI |

## Non-Negotiable Invariants

1. The agent must never execute commands automatically.
2. Commands must follow this lifecycle: propose → approve → execute.
3. No command may run directly on the host machine.
4. All execution must happen in an isolated Docker sandbox.
5. LLM output must be validated before use.
6. Dangerous commands must be blocked even if the LLM suggests them.
7. All sessions, messages, commands, approvals, and execution results must be logged.
8. Production deployment must disable local Docker execution unless a secure remote sandbox is configured.

## Core User Flow

1. User opens the web app.
2. User creates or selects a session.
3. User asks for a terminal task.
4. Agent analyzes the task and proposes a command.
5. User reviews command, risk level, and explanation.
6. User approves or rejects the command.
7. If approved, backend executes command in sandbox.
8. Output streams back to the UI.
9. Session history persists.

## Feature Phases

### Phase 1 — Spec Bootstrap
Create the project structure and spec files before implementation.

### Phase 2 — System Bootstrap
Create Nuxt frontend, FastAPI backend, Docker Compose, and `/health` endpoint.

### Phase 3 — Chat Foundation
Create chat UI and `/chat` endpoint with mock response.

### Phase 4 — Structured Command Proposals
Return structured command proposal objects from backend.

### Phase 5 — Approval System
Add explicit approval before command execution.

### Phase 6 — Docker Execution
Run approved commands in isolated Docker containers.

### Phase 7 — Execution Hardening
Add timeout, memory limits, CPU limits, read-only filesystem, non-root user, dropped capabilities, and network disabled.

### Phase 8 — Observability
Add Langfuse traces and structured logs.

### Phase 9 — LangGraph Agent
Replace basic logic with a LangGraph state machine.

### Phase 10 — Claude Agent Nodes
Use Anthropic Claude behind a provider wrapper.

### Phase 11 — LLM Validation
Validate Claude output with Pydantic and retry/fallback safely.

### Phase 12 — Persistence
Add PostgreSQL, SQLAlchemy models, sessions, messages, commands, and outputs.

### Phase 13 — Multi-Session UI
Add session creation, listing, switching, and history loading.

### Phase 14 — SSE Streaming Foundation
Add Server-Sent Events for streaming responses.

### Phase 15 — Agent Streaming
Stream agent planning, reasoning, and command proposals.

### Phase 16 — Execution Streaming
Stream command output live to UI.

### Phase 17 — Safe Docker Streaming
Replace subprocess execution with Docker SDK streaming.

### Phase 18 — Production Readiness
Add environment config, CORS, error handling, logging, Docker improvements, and deployment safety.

### Phase 19 — Railway Deployment
Deploy web, API, Postgres, and Redis. Disable real execution in production demo.

## Recommended Build Rule for Codex
Codex must implement only one phase at a time. After each phase:

1. Run tests or basic verification.
2. Update `specs/progress-tracker.md`.
3. Commit changes with a clear message.
4. Do not proceed until the current phase works end to end.
