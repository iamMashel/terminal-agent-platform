import anyio
from httpx import ASGITransport, AsyncClient
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ReadTimeout

from app.main import app
from app.schemas.commands import CommandExecutionResponse
from app.services.execution import ExecutionResult


def test_execute_endpoint_runs_approved_command(monkeypatch) -> None:
    def mock_execute_approved_command(command_id, settings):
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
        id="runner-test-command-persistence",
        cmd="pwd",
        risk="low",
        explanation="Prints current directory.",
    )
    register_command_proposal(proposal, "runner-test-session")
    record_command_approval(proposal.id, "approved")

    result = execute_approved_command(proposal.id, Settings(), FakeRunner())

    assert result.status == "completed"
    assert result.output == "/workspace\n"


def test_docker_runner_uses_hardened_container_options(monkeypatch) -> None:
    from app.core.config import Settings
    from app.services.execution import DockerCommandRunner

    captured_options = {}

    class FakeContainer:
        def wait(self, timeout):
            assert timeout == 9
            return {"StatusCode": 0}

        def logs(self, stdout, stderr):
            assert stdout is True
            assert stderr is True
            return b"ok\n"

        def remove(self, force):
            assert force is True

    class FakeContainers:
        def run(self, **options):
            captured_options.update(options)
            return FakeContainer()

    class FakeClient:
        containers = FakeContainers()

    monkeypatch.setattr("docker.from_env", lambda: FakeClient())

    settings = Settings(
        execution_timeout_seconds=9,
        execution_memory_limit="64m",
        execution_cpu_quota=25000,
        execution_cpu_period=100000,
        execution_user="65534:65534",
    )

    result = DockerCommandRunner().run("pwd", settings)

    assert result.exit_code == 0
    assert result.output == "ok\n"
    assert captured_options == {
        "image": "alpine:3.20",
        "command": ["sh", "-lc", "pwd"],
        "cap_drop": ["ALL"],
        "cpu_period": 100000,
        "cpu_quota": 25000,
        "detach": True,
        "mem_limit": "64m",
        "network_disabled": True,
        "read_only": True,
        "stderr": True,
        "stdout": True,
        "tmpfs": {"/tmp": "rw,noexec,nosuid,size=16m"},
        "user": "65534:65534",
        "working_dir": "/tmp",
    }


def test_docker_runner_terminates_timed_out_container(monkeypatch) -> None:
    from app.core.config import Settings
    from app.services.execution import DockerCommandRunner

    events = []

    class FakeContainer:
        def wait(self, timeout):
            assert timeout == 1
            raise ReadTimeout

        def kill(self):
            events.append("killed")

        def remove(self, force):
            assert force is True
            events.append("removed")

    class FakeContainers:
        def run(self, **options):
            return FakeContainer()

    class FakeClient:
        containers = FakeContainers()

    monkeypatch.setattr("docker.from_env", lambda: FakeClient())

    result = DockerCommandRunner().run(
        "sleep 30",
        Settings(execution_timeout_seconds=1),
    )

    assert result.exit_code == 124
    assert result.output == "Command timed out and was terminated.\n"
    assert events == ["killed", "removed"]


def test_docker_runner_handles_docker_wait_connection_timeout(monkeypatch) -> None:
    from app.core.config import Settings
    from app.services.execution import DockerCommandRunner

    events = []

    class FakeContainer:
        def wait(self, timeout):
            raise RequestsConnectionError("Read timed out.")

        def kill(self):
            events.append("killed")

        def remove(self, force):
            events.append("removed")

    class FakeContainers:
        def run(self, **options):
            return FakeContainer()

    class FakeClient:
        containers = FakeContainers()

    monkeypatch.setattr("docker.from_env", lambda: FakeClient())

    result = DockerCommandRunner().run(
        "sleep 30",
        Settings(execution_timeout_seconds=1),
    )

    assert result.exit_code == 124
    assert result.output == "Command timed out and was terminated.\n"
    assert events == ["killed", "removed"]
