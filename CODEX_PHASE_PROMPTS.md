# Codex Phase Prompts

Use these one at a time in VS Code/Codex.

## Phase 1-2 Prompt

Read all project specs. Implement only the system bootstrap: Nuxt frontend, FastAPI backend, Docker Compose, and `/health` endpoint. Update progress tracker. Do not implement chat or agent yet.

## Phase 3 Prompt

Implement chat foundation only. Add `/chat` endpoint with a mock assistant response. Add a simple Nuxt chat UI. Verify frontend can send a message and display response. Update progress tracker.

## Phase 4 Prompt

Implement structured command proposals. Backend should return `message` and `commands[]` with `id`, `cmd`, `risk`, and `explanation`. Frontend should render command proposal cards. Do not execute commands. Update progress tracker.

## Phase 5 Prompt

Implement command approval lifecycle. Add approval endpoint and update command status to approved. Execution must still be disabled. Update progress tracker.

## Phase 6-7 Prompt

Implement Docker sandbox execution for approved commands. Add security hardening: network disabled, non-root user, memory/CPU limits, timeout, read-only filesystem where possible, and command filtering. Update progress tracker.

## Phase 8 Prompt

Add observability: structured logs and Langfuse tracing for chat, command proposal, approval, and execution. Move credentials to env variables. Update progress tracker.

## Phase 9-11 Prompt

Implement LangGraph agent using Anthropic Claude. Use a provider wrapper. Validate LLM output with Pydantic. Add retry and fallback. Backend safety must override LLM output. Update progress tracker.

## Phase 12-13 Prompt

Add PostgreSQL persistence with SQLAlchemy. Implement sessions, messages, commands, status, and outputs. Add multi-session UI with create/list/load session history. Update progress tracker.

## Phase 14-15 Prompt

Implement SSE streaming for agent status, reasoning, and command proposals. Keep normal `/chat` endpoint working. Update progress tracker.

## Phase 16-17 Prompt

Implement live streaming execution output using Docker SDK logs streaming. Remove unsafe subprocess execution. Preserve approval requirement and sandbox restrictions. Update progress tracker.

## Phase 18-19 Prompt

Prepare deployment for Railway. Use env-based config, production start commands, CORS config, and `EXECUTION_MODE=disabled` for production demo. Update README and progress tracker.
