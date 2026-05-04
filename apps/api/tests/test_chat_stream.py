import json
from uuid import UUID

import anyio
from httpx import ASGITransport, AsyncClient

from app.main import app


def test_chat_stream_returns_sse_command_events() -> None:
    async def request_stream() -> tuple[str, str]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/chat/stream",
                params={
                    "session_id": "stream-session",
                    "message": "list files",
                },
            )

        assert response.status_code == 200
        return response.headers["content-type"], response.text

    content_type, body = anyio.run(request_stream)

    assert content_type.startswith("text/event-stream")
    assert body.startswith("event: status\ndata: Understanding request...\n\n")
    assert (
        "event: reasoning\ndata: This is a read-only file discovery task.\n\n" in body
    )
    assert body.endswith("event: done\ndata: complete\n\n")

    command_data = body.split("event: command\ndata: ", 1)[1].split("\n\n", 1)[0]
    command = json.loads(command_data)
    UUID(command["id"])
    assert command == {
        "id": command["id"],
        "cmd": "ls -la",
        "risk": "low",
        "explanation": "Lists files in the current directory, including hidden entries.",
        "status": "proposed",
    }


def test_chat_stream_omits_command_event_for_dangerous_request() -> None:
    async def request_stream() -> str:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/chat/stream",
                params={
                    "session_id": "stream-session",
                    "message": "please rm -rf this project",
                },
            )

        assert response.status_code == 200
        return response.text

    body = anyio.run(request_stream)

    assert "event: status" in body
    assert "event: reasoning" in body
    assert "event: command" not in body
    assert body.endswith("event: done\ndata: complete\n\n")


def test_chat_stream_rejects_empty_message() -> None:
    async def request_stream() -> int:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/chat/stream",
                params={
                    "session_id": "stream-session",
                    "message": "",
                },
            )

        return response.status_code

    assert anyio.run(request_stream) == 422
