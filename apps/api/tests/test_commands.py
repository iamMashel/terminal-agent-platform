import anyio
from httpx import ASGITransport, AsyncClient

from app.main import app


def test_command_approval_marks_proposed_command_approved() -> None:
    async def approve_command() -> dict[str, str]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            chat_response = await client.post(
                "/chat",
                json={
                    "session_id": "local-session",
                    "message": "list files",
                },
            )
            command_id = chat_response.json()["commands"][0]["id"]

            approval_response = await client.post(
                f"/commands/{command_id}/approval",
                json={"decision": "approved"},
            )

        assert approval_response.status_code == 200
        return approval_response.json()

    payload = anyio.run(approve_command)

    assert payload["status"] == "approved"
    assert payload["message"] == "Command approved."


def test_command_approval_can_reject_proposed_command() -> None:
    async def reject_command() -> dict[str, str]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            chat_response = await client.post(
                "/chat",
                json={
                    "session_id": "local-session",
                    "message": "print current directory",
                },
            )
            command_id = chat_response.json()["commands"][0]["id"]

            approval_response = await client.post(
                f"/commands/{command_id}/approval",
                json={"decision": "rejected"},
            )

        assert approval_response.status_code == 200
        return approval_response.json()

    payload = anyio.run(reject_command)

    assert payload["status"] == "rejected"
    assert payload["message"] == "Command rejected."


def test_command_approval_rejects_unknown_command() -> None:
    async def approve_missing_command() -> int:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/commands/missing-command/approval",
                json={"decision": "approved"},
            )

        return response.status_code

    assert anyio.run(approve_missing_command) == 404


def test_command_approval_rejects_invalid_decision() -> None:
    async def approve_with_invalid_decision() -> int:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/commands/missing-command/approval",
                json={"decision": "maybe"},
            )

        return response.status_code

    assert anyio.run(approve_with_invalid_decision) == 422
