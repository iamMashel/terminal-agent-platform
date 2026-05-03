import anyio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.execution import ExecutionResult


def test_execute_endpoint_runs_approved_command(monkeypatch) -> None:
    def mock_execute_approved_command(command_id, settings):
        return {
            "command_id": command_id,
            "status": "completed",
            "exit_code": 0,
            "output": "total 0\n",
        }

    monkeypatch.setattr(
        "app.routes.commands.execute_approved_command",
        mock_execute_approved_command,
    )

    async def execute_command() -> dict[str, object]:
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

            await client.post(
                f"/commands/{command_id}/approval",
                json={"decision": "approved"},
            )
            execution_response = await client.post(
                f"/commands/{command_id}/execute",
            )

        assert execution_response.status_code == 200
        return execution_response.json()

    payload = anyio.run(execute_command)

    assert payload["status"] == "completed"
    assert payload["exit_code"] == 0
    assert payload["output"] == "total 0\n"


def test_execute_endpoint_requires_approval() -> None:
    async def execute_unapproved_command() -> int:
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

            execution_response = await client.post(
                f"/commands/{command_id}/execute",
            )

        return execution_response.status_code

    assert anyio.run(execute_unapproved_command) == 409


def test_execute_endpoint_rejects_unknown_command() -> None:
    async def execute_missing_command() -> int:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/commands/missing-command/execute")

        return response.status_code

    assert anyio.run(execute_missing_command) == 404


def test_execute_approved_command_maps_runner_result() -> None:
    from app.core.config import Settings
    from app.schemas.chat import CommandProposal
    from app.services.commands import register_command_proposal, record_command_approval
    from app.services.execution import execute_approved_command

    class FakeRunner:
        def run(self, command, settings):
            assert command == "pwd"
            assert settings.execution_image == "alpine:3.20"
            return ExecutionResult(exit_code=0, output="/workspace\n")

    proposal = CommandProposal(
        id="runner-test-command",
        cmd="pwd",
        risk="low",
        explanation="Prints current directory.",
    )
    register_command_proposal(proposal)
    record_command_approval(proposal.id, "approved")

    result = execute_approved_command(proposal.id, Settings(), FakeRunner())

    assert result.status == "completed"
    assert result.output == "/workspace\n"
