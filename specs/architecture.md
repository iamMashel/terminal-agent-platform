# Architecture Context

## Primary Invariant
The agent may propose terminal commands, but it must never execute commands directly on the host machine.

All command execution must happen inside an isolated sandbox, require explicit user approval, include timeouts, resource limits, structured logs, and auditable output.

## Stack

| Layer | Technology | Role |
|---|---|---|
| Frontend | Nuxt 4 + TypeScript | UI, chat, session management, command approval |
| Backend | FastAPI | API, orchestration, validation, persistence |
| Agent | LangGraph | Stateful agent workflow |
| LLM | Anthropic Claude | Command planning and explanation |
| Sandbox | Docker | Isolated command execution |
| Database | PostgreSQL | Sessions, messages, commands, logs |
| ORM | SQLAlchemy | Database access |
| Realtime | SSE | Streaming agent/execution output |
| Observability | Langfuse + logging | Traces and debugging |
| Local Infra | Docker Compose | Local development |

## System Boundaries

- `apps/web` owns UI, session sidebar, chat interface, command preview cards, approval actions, and streamed output rendering.
- `apps/api` owns API routes, request validation, agent orchestration, persistence, execution orchestration, and observability.
- `apps/api/app/agent` owns LangGraph state and nodes.
- `apps/api/app/llm` owns provider wrappers and schema validation.
- `apps/api/app/execution` owns sandbox execution and streaming.
- `apps/api/app/db` owns database engine, sessions, and ORM models.
- `infra` owns Docker and deployment-related configuration.
- `specs` owns product, architecture, standards, and progress tracking.

## Storage Model

### PostgreSQL
Stores:
- sessions
- messages
- command proposals
- approval status
- execution output
- execution status

### Redis
Reserved for:
- live execution state
- future job queues
- session cache

### Blob/Object Storage
Future use for:
- large command outputs
- uploaded files
- generated artifacts

## Auth and Access Model

Initial MVP may run without auth for local development.

Production/SaaS version must enforce:
- each user owns sessions
- only owners can mutate sessions
- only owners can approve commands
- execution is rate-limited

## Command Lifecycle

```txt
proposed → approved → executing → executed | failed | blocked
```

## Execution Rules

Docker execution must use:
- network disabled
- read-only filesystem where possible
- non-root user
- dropped Linux capabilities
- memory limit
- CPU limit
- timeout
- structured output capture

## Production Deployment Rule
Do not expose local Docker socket execution in production.

Production demo should use:

```env
EXECUTION_MODE=disabled
```

Future production execution should use a secure remote sandbox provider such as E2B, Firecracker, or isolated runner infrastructure.
