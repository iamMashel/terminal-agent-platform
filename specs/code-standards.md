# Code Standards

## General

- Build one vertical slice at a time.
- Keep modules small and single-purpose.
- Fix root causes; do not layer hacks.
- Do not mix UI, API, database, and execution logic in one place.
- Do not invent features not defined in specs.

## TypeScript / Nuxt

- Use strict TypeScript.
- Avoid `any` unless there is a clear boundary and a TODO to replace it.
- Keep API base URL in runtime config.
- Do not hardcode `localhost` in production-facing code.
- UI components should be simple, accessible, and predictable.
- Command approval must be visually explicit.

## FastAPI / Python

- Validate inputs with Pydantic.
- Keep route handlers thin.
- Place business logic in services/modules.
- Use environment variables for configuration.
- Do not hardcode secrets.
- Return consistent API shapes.
- Use async endpoints where appropriate.

## LLM / Agent

- Never trust raw LLM output.
- Validate all LLM output with Pydantic.
- Use retries and safe fallbacks.
- Block dangerous commands after LLM generation.
- Keep provider code isolated so Anthropic/OpenAI can be swapped later.

## Execution

- Never use `subprocess.Popen(shell=True)` for production command execution.
- Never run commands on the host.
- Use Docker sandbox execution.
- Require approval before execution.
- Disable execution in production unless a safe sandbox is configured.

## Database

- Store metadata in PostgreSQL.
- Do not store secrets in the database.
- Store command outputs only if reasonable size; large outputs move to blob storage later.
- Use migrations once the schema stabilizes.

## Git

- Use feature branches.
- Commit after each working vertical slice.
- Use meaningful commit messages:
  - `feat: add command proposal API`
  - `fix: validate llm command output`
  - `chore: prepare railway deployment`
