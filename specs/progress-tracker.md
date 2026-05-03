# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase
Phase 10 complete

## Current Goal
Prepare for Phase 11 LLM validation.

## Completed
- Codex-ready specs prepared
- Documented professional Git history rules for phase branches, scoped commits, and merge expectations
- Created monorepo ownership structure for `apps/api`, `apps/web`, and `infra`
- Added backend subdirectories for routes, schemas, services, core config, database, LLM, agent, execution, and tests
- Added frontend placeholder directories for pages, components, composables, public assets, and shared types
- Added infrastructure placeholder directories for Docker and deployment configuration
- Initialized FastAPI backend in `apps/api`
- Added typed backend `/health` endpoint returning the documented health contract
- Initialized Nuxt 4 frontend in `apps/web`
- Added Nuxt 4 app-directory health status view that calls the backend `/health` endpoint through runtime config
- Added Dockerfiles for API and web services
- Added Docker Compose for local API and web development
- Added `.env.example`, `.gitignore`, and Docker ignore files to keep secrets and generated files out of git
- Added backend health endpoint test
- Installed local ignored development dependencies for verification
- Added typed backend `/chat` endpoint with a mock assistant response
- Added chat request/response Pydantic models and mock chat service
- Added backend chat endpoint tests for successful and invalid requests
- Replaced the frontend bootstrap screen with a simple chat control-panel UI
- Wired the Nuxt chat composer to POST messages to the backend `/chat` endpoint
- Added typed backend command proposal schema to the `/chat` response
- Added deterministic mock command proposals for safe read-only file and directory inspection
- Rendered structured command proposal cards in the Nuxt chat UI with visible risk labels
- Added backend command approval contract for explicit approve/reject decisions
- Added in-memory command status tracking for Phase 5
- Added command approval controls to the Nuxt command proposal UI
- Added backend command execution contract for approved commands
- Added Docker SDK execution service for approved command proposals
- Added local Docker socket wiring and execution config for API development
- Added frontend execute action and execution output panel for approved commands
- Added Docker execution hardening defaults for non-root user, read-only filesystem, dropped capabilities, memory limit, CPU quota, and timeout termination
- Added structured JSON logging with request and trace identifiers
- Added observability middleware that emits request lifecycle events and trace headers
- Added optional Langfuse trace client configuration for request spans
- Added deterministic LangGraph agent state machine for planning, safety validation, command generation, and explanations
- Routed `/chat` command proposals through the LangGraph agent graph
- Added Anthropic Claude command planner provider behind an isolated LLM wrapper
- Added config to enable Claude planning while keeping mock planning as the local default
- Wired the LangGraph command generator node to use the configured provider when available
- Set the default Claude model to `claude-haiku-4-5-20251001`

## In Progress
- None

## Next Up
- Phase 11: validate Claude output with Pydantic and retry/fallback safely

## Open Questions
- Which deployment provider will be final after Railway demo?
- When should real production execution be enabled? Later on.
- Should auth be Clerk, Supabase, or custom JWT? Custom JWT.

## Architecture Decisions
- Use Nuxt 4 for frontend
- Use FastAPI for backend
- Use LangGraph for agent workflow
- Use Anthropic Claude for LLM provider
- Use Docker for local sandbox execution
- Disable execution in production demo by default

## Session Notes
This project should be built one phase at a time. Codex should not jump ahead or combine unrelated phases.
Phase 2 verification completed with backend pytest, backend Ruff, Nuxt typecheck, Docker Compose config validation, Python compile, API health curl, Nuxt root-route curl, and a path/secret scan.
Phase 3 verification completed with backend pytest, backend Ruff, and Nuxt typecheck.
Phase 4 verification completed with backend pytest, backend Ruff, and Nuxt typecheck.
Phase 5 verification completed with backend pytest, backend Ruff, and Nuxt typecheck.
Phase 6 verification completed with backend pytest, backend Ruff, Nuxt typecheck, Docker CLI sandbox probe, and Docker SDK service probe.
Phase 7 verification completed with backend pytest, backend Ruff, Nuxt typecheck, Docker non-root/read-only probe, and Docker timeout termination probe.
Phase 8 verification completed with backend pytest, backend Ruff, Nuxt typecheck, and Langfuse SDK import smoke check.
Phase 9 verification completed with backend pytest, backend Ruff, Nuxt typecheck, and LangGraph import smoke check.
Phase 10 verification completed with backend pytest, backend Ruff, Nuxt typecheck, and Anthropic SDK import smoke check.
