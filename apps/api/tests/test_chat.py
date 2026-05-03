from uuid import UUID

import anyio
from httpx import ASGITransport, AsyncClient

from app.main import app


def test_chat_endpoint_returns_command_proposal() -> None:
    async def request_chat() -> dict[str, object]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/chat",
                json={
                    "session_id": "local-session",
                    "message": "list files",
                },
            )

        assert response.status_code == 200
        return response.json()

    payload = anyio.run(request_chat)

    assert payload["message"] == "Here is a command proposal."
    commands = payload["commands"]
    assert isinstance(commands, list)
    assert len(commands) == 1

    command = commands[0]
    assert isinstance(command, dict)
    UUID(command["id"])
    assert command == {
        "id": command["id"],
        "cmd": "ls -la",
        "risk": "low",
        "explanation": "Lists files in the current directory, including hidden entries.",
        "status": "proposed",
    }


def test_chat_endpoint_returns_txt_file_command_for_text_file_request() -> None:
    async def request_chat() -> dict[str, object]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/chat",
                json={
                    "session_id": "local-session",
                    "message": "find all txt files",
                },
            )

        assert response.status_code == 200
        return response.json()

    payload = anyio.run(request_chat)
    commands = payload["commands"]
    assert isinstance(commands, list)
    command = commands[0]
    assert isinstance(command, dict)
    assert command["cmd"] == "find . -name '*.txt'"
    assert command["risk"] == "low"
    assert command["status"] == "proposed"


def test_chat_endpoint_rejects_empty_message() -> None:
    async def request_chat() -> int:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/chat",
                json={
                    "session_id": "local-session",
                    "message": "",
                },
            )

        return response.status_code

    assert anyio.run(request_chat) == 422
