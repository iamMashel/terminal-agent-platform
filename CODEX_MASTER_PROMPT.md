# Codex Master Prompt

You are building a production-grade full-stack AI Terminal Agent Platform.

Read these files first:

- `PROJECT_PLAN.md`
- `specs/architecture.md`
- `specs/code-standards.md`
- `specs/api-contracts.md`
- `specs/agent-behavior.md`
- `specs/security-model.md`
- `specs/ui-context.md`
- `specs/progress-tracker.md`

## Work Rules

1. Follow spec-driven development.
2. Implement one phase at a time.
3. Do not invent behavior outside the specs.
4. If requirements are missing, add questions to `specs/progress-tracker.md`.
5. Keep implementation small, testable, and incremental.
6. After each phase, update `specs/progress-tracker.md`.
7. Do not execute commands directly on the host in app code.
8. Never bypass command approval.
9. Validate LLM output with Pydantic.
10. Use environment variables for secrets and config.

## Start Task

Begin with Phase 1 and Phase 2 only:

1. Create the monorepo folder structure.
2. Initialize FastAPI backend in `apps/api`.
3. Initialize Nuxt frontend in `apps/web`.
4. Add Docker Compose for local development.
5. Add a backend `/health` endpoint.
6. Make the frontend call the backend health endpoint.
7. Update `specs/progress-tracker.md`.
8. Stop and summarize what changed.

Do not implement the agent yet.
