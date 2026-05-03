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
      "explanation": "Finds all .txt files recursively."
    }
  ]
}
```

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
