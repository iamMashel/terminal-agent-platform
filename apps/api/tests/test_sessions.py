import anyio
from httpx import ASGITransport, AsyncClient

from app.main import app


def test_sessions_endpoint_creates_and_lists_session() -> None:
    async def create_and_list_session() -> tuple[str, list[dict[str, str]]]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            create_response = await client.post("/sessions")
            session_id = create_response.json()["data"]["session_id"]

            list_response = await client.get("/sessions")

        assert create_response.status_code == 200
        assert list_response.status_code == 200
        return session_id, list_response.json()["data"]

    session_id, sessions = anyio.run(create_and_list_session)

    assert {"id": session_id} in sessions


def test_session_detail_includes_messages_and_command_proposals() -> None:
    async def run_chat_and_get_session() -> dict[str, object]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            create_response = await client.post("/sessions")
            session_id = create_response.json()["data"]["session_id"]

            await client.post(
                "/chat",
                json={
                    "session_id": session_id,
                    "message": "list files",
                },
            )
            session_response = await client.get(f"/sessions/{session_id}")

        assert session_response.status_code == 200
        return session_response.json()["data"]

    session = anyio.run(run_chat_and_get_session)

    assert session["messages"] == [
        {
            "role": "user",
            "content": "list files",
        },
        {
            "role": "assistant",
            "content": "Here is a command proposal.",
        },
    ]
    assert len(session["commands"]) == 1
    assert session["commands"][0]["cmd"] == "ls -la"
    assert session["commands"][0]["status"] == "proposed"
    assert session["commands"][0]["output"] is None


def test_session_detail_returns_404_for_unknown_session() -> None:
    async def get_missing_session() -> int:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/sessions/missing-session")

        return response.status_code

    assert anyio.run(get_missing_session) == 404


def test_session_detail_includes_execution_output(monkeypatch) -> None:
    from app.schemas.commands import CommandExecutionResponse

    def mock_execute_approved_command(command_id, settings):
        from app.db.repository import add_execution_log
        from app.db.session import get_session

        with get_session() as db:
            add_execution_log(db, command_id, "completed", 0, "total 0\n")

        return CommandExecutionResponse(
            command_id=command_id,
            status="completed",
            exit_code=0,
            output="total 0\n",
        )

    monkeypatch.setattr(
        "app.routes.commands.execute_approved_command",
        mock_execute_approved_command,
    )

    async def run_execution_and_get_session() -> dict[str, object]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            create_response = await client.post("/sessions")
            session_id = create_response.json()["data"]["session_id"]

            chat_response = await client.post(
                "/chat",
                json={
                    "session_id": session_id,
                    "message": "list files",
                },
            )
            command_id = chat_response.json()["commands"][0]["id"]

            await client.post(
                f"/commands/{command_id}/approval",
                json={"decision": "approved"},
            )
            await client.post(f"/commands/{command_id}/execute")
            session_response = await client.get(f"/sessions/{session_id}")

        assert session_response.status_code == 200
        return session_response.json()["data"]

    session = anyio.run(run_execution_and_get_session)

    assert session["commands"][0]["status"] == "approved"
    assert session["commands"][0]["output"] == "total 0\n"
