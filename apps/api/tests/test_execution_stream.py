import anyio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.commands import CommandNotApprovedError, CommandNotFoundError
from app.services.execution import ExecutionStreamUpdate


def test_execute_stream_returns_output_events(monkeypatch) -> None:
    def mock_execute_approved_command(command_id, settings):
        assert command_id == "stream-command"
        yield ExecutionStreamUpdate(kind="output", data="./notes.txt\n")
        yield ExecutionStreamUpdate(kind="output", data="./todo.txt\n")
        yield ExecutionStreamUpdate(kind="result", data="", exit_code=0)

    monkeypatch.setattr(
        "app.core.sse.execute_approved_command_stream",
        mock_execute_approved_command,
    )

    async def request_stream() -> tuple[str, str]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/execute/stream",
                params={"command_id": "stream-command"},
            )

        assert response.status_code == 200
        return response.headers["content-type"], response.text

    content_type, body = anyio.run(request_stream)

    assert content_type.startswith("text/event-stream")
    assert body.startswith(
        "event: status\ndata: Executing inside Docker sandbox...\n\n"
    )
    assert "event: output\ndata: ./notes.txt\n\n" in body
    assert "event: output\ndata: ./todo.txt\n\n" in body
    assert body.endswith("event: done\ndata: Execution complete\n\n")


def test_execute_stream_returns_error_event_for_missing_command(monkeypatch) -> None:
    def mock_execute_approved_command(command_id, settings):
        raise CommandNotFoundError

    monkeypatch.setattr(
        "app.core.sse.execute_approved_command_stream",
        mock_execute_approved_command,
    )

    async def request_stream() -> str:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/execute/stream",
                params={"command_id": "missing-command"},
            )

        assert response.status_code == 200
        return response.text

    body = anyio.run(request_stream)

    assert "event: error\ndata: Command proposal not found.\n\n" in body
    assert "event: done" not in body


def test_execute_stream_returns_error_event_for_unapproved_command(monkeypatch) -> None:
    def mock_execute_approved_command(command_id, settings):
        raise CommandNotApprovedError

    monkeypatch.setattr(
        "app.core.sse.execute_approved_command_stream",
        mock_execute_approved_command,
    )

    async def request_stream() -> str:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/execute/stream",
                params={"command_id": "unapproved-command"},
            )

        assert response.status_code == 200
        return response.text

    body = anyio.run(request_stream)

    assert (
        "event: error\ndata: Command must be approved before execution.\n\n" in body
    )
    assert "event: done" not in body


def test_execute_stream_rejects_empty_command_id() -> None:
    async def request_stream() -> int:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/execute/stream",
                params={"command_id": ""},
            )

        return response.status_code

    assert anyio.run(request_stream) == 422
