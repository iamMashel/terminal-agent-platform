# API Contracts

## Health

### GET `/health`

Response:

```json
{
  "status": "ok",
  "service": "terminal-agent-api"
}
```

## Sessions

### POST `/sessions`

Response:

```json
{
  "success": true,
  "data": {
    "session_id": "uuid"
  }
}
```

### GET `/sessions`

Response:

```json
{
  "success": true,
  "data": [
    { "id": "uuid" }
  ]
}
```

### GET `/sessions/{session_id}`

Response:

```json
{
  "success": true,
  "data": {
    "messages": [
      { "role": "user", "content": "find all txt files" }
    ],
    "commands": [
      {
        "id": "uuid",
        "cmd": "find . -name '*.txt'",
        "risk": "low",
        "status": "proposed",
        "output": null
      }
    ]
  }
}
```

Session detail data is persisted in Phase 12 with SQLAlchemy models backed by
PostgreSQL in local Docker Compose.

## Chat

### POST `/chat`

Request:

```json
{
  "session_id": "uuid",
  "message": "find all txt files"
}
```

Response:

```json
{
  "message": "Here is a command proposal.",
  "commands": [
    {
      "id": "uuid",
      "cmd": "find . -name '*.txt'",
      "risk": "low",
      "explanation": "Finds all .txt files recursively.",
      "status": "proposed"
    }
  ]
}
```

## Command Approval

### POST `/commands/{command_id}/approval`

Request:

```json
{
  "decision": "approved"
}
```

Response:

```json
{
  "command_id": "uuid",
  "status": "approved",
  "message": "Command approved."
}
```

Valid decisions:

- `approved`
- `rejected`

Approval only changes command status. It must not execute commands.

## Command Execution

### POST `/commands/{command_id}/execute`

Response:

```json
{
  "command_id": "uuid",
  "status": "completed",
  "exit_code": 0,
  "output": "./notes.txt\n"
}
```

Execution requires prior approval. If the command is not approved, the API returns `409`.
Execution must run through Docker and must not run directly on the host.

## Streaming Chat

### GET `/chat/stream?session_id=uuid&message=...`

SSE events:

```txt
event: status
data: Understanding request...

event: reasoning
data: This is a read-only file discovery task.

event: command
data: {"id":"uuid","cmd":"find . -name '*.txt'","risk":"low","explanation":"..."}

event: done
data: complete
```

## Execution

### GET `/execute/stream?command_id=uuid`

SSE events:

```txt
event: status
data: Executing inside Docker sandbox...

event: output
data: ./notes.txt

event: done
data: Execution complete
```

If production execution is disabled:

```txt
event: error
data: Execution is disabled in production demo.
```
