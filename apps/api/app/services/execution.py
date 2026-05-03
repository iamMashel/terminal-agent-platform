from dataclasses import dataclass
from typing import Protocol

from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ReadTimeout

from app.core.config import Settings
from app.db.repository import add_execution_log
from app.db.session import get_session
from app.schemas.commands import CommandExecutionResponse, ExecutionStatus
from app.services.commands import get_approved_command


@dataclass(frozen=True)
class ExecutionResult:
    exit_code: int
    output: str


class CommandRunner(Protocol):
    def run(self, command: str, settings: Settings) -> ExecutionResult:
        pass


class DockerCommandRunner:
    def run(self, command: str, settings: Settings) -> ExecutionResult:
        import docker

        client = docker.from_env()
        container = client.containers.run(
            image=settings.execution_image,
            command=["sh", "-lc", command],
            cap_drop=["ALL"],
            cpu_period=settings.execution_cpu_period,
            cpu_quota=settings.execution_cpu_quota,
            detach=True,
            mem_limit=settings.execution_memory_limit,
            network_disabled=True,
            read_only=True,
            stderr=True,
            stdout=True,
            tmpfs={"/tmp": "rw,noexec,nosuid,size=16m"},
            user=settings.execution_user,
            working_dir="/tmp",
        )

        try:
            try:
                wait_result = container.wait(timeout=settings.execution_timeout_seconds)
                raw_output = container.logs(stdout=True, stderr=True)
            except (ReadTimeout, RequestsConnectionError):
                container.kill()
                return ExecutionResult(
                    exit_code=124,
                    output="Command timed out and was terminated.\n",
                )
        finally:
            container.remove(force=True)

        output = raw_output.decode("utf-8", errors="replace")
        return ExecutionResult(exit_code=wait_result["StatusCode"], output=output)


def execute_approved_command(
    command_id: str,
    settings: Settings,
    runner: CommandRunner | None = None,
) -> CommandExecutionResponse:
    command = get_approved_command(command_id)
    execution_runner = runner or DockerCommandRunner()
    result = execution_runner.run(command.cmd, settings)
    status: ExecutionStatus = "completed" if result.exit_code == 0 else "failed"

    with get_session() as db:
        add_execution_log(
            db,
            command.command_id,
            status,
            result.exit_code,
            result.output,
        )

    return CommandExecutionResponse(
        command_id=command.command_id,
        status=status,
        exit_code=result.exit_code,
        output=result.output,
    )
