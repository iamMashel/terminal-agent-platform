# Security Model

## Threats

- LLM suggests dangerous command.
- User asks for destructive command.
- Command injection through shell strings.
- Agent bypasses approval.
- Production server exposes Docker socket.
- Command runs forever or consumes resources.
- Command accesses network unexpectedly.

## Controls

### Human Approval
Every command requires explicit user approval before execution.

### Validation
All LLM outputs are validated with Pydantic before use.

### Safety Filtering
Backend blocks dangerous commands using denylist and future allowlist/risk policy.

### Sandbox Execution
Commands run only in Docker containers with:
- network disabled
- read-only filesystem
- non-root user
- capabilities dropped
- memory limit
- CPU limit
- timeout

### Production Demo Mode
Production deployment must set:

```env
EXECUTION_MODE=disabled
```

### Secrets
All secrets must be environment variables. Never commit `.env`.

### Future Hardening
- Add auth
- Add per-user rate limits
- Add command allowlist for MVP
- Use remote sandbox provider
- Add audit trail for command approvals
