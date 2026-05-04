from dataclasses import dataclass
from queue import Empty, Queue
from threading import Thread
from time import monotonic
from typing import Literal
from collections.abc import Iterator
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


@dataclass(frozen=True)
class ExecutionStreamUpdate:
    kind: Literal["output", "result"]
    data: str
    exit_code: int | None = None


class CommandRunner(Protocol):
    def run(self, command: str, settings: Settings) -> ExecutionResult:
        pass


class StreamingCommandRunner(CommandRunner, Protocol):
    def stream(self, command: str, settings: Settings) -> Iterator[ExecutionStreamUpdate]:
        pass


class DockerCommandRunner:
    def run(self, command: str, settings: Settings) -> ExecutionResult:
        output_parts = []
        exit_code = 1

        for update in self.stream(command, settings):
            if update.kind == "output":
                output_parts.append(update.data)
            else:
                exit_code = update.exit_code if update.exit_code is not None else 1

        return ExecutionResult(exit_code=exit_code, output="".join(output_parts))

    def stream(self, command: str, settings: Settings) -> Iterator[ExecutionStreamUpdate]:
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

        output_queue: Queue[bytes | None] = Queue()
        wait_queue: Queue[dict[str, int] | Exception] = Queue(maxsize=1)

        def read_logs() -> None:
            try:
                for raw_chunk in container.logs(
                    stdout=True,
                    stderr=True,
                    stream=True,
                    follow=True,
                ):
                    output_queue.put(raw_chunk)
            finally:
                output_queue.put(None)

        def wait_for_container() -> None:
            try:
                wait_queue.put(container.wait())
            except Exception as exc:
                wait_queue.put(exc)

        log_thread = Thread(target=read_logs, daemon=True)
        wait_thread = Thread(target=wait_for_container, daemon=True)
        log_thread.start()
        wait_thread.start()
        deadline = monotonic() + settings.execution_timeout_seconds
        wait_result: dict[str, int] | None = None

        try:
            while wait_result is None:
                try:
                    raw_chunk = output_queue.get(timeout=0.05)
                    if raw_chunk is not None:
                        yield ExecutionStreamUpdate(
                            kind="output",
                            data=raw_chunk.decode("utf-8", errors="replace"),
                        )
                except Empty:
                    pass

                try:
                    wait_update = wait_queue.get_nowait()
                except Empty:
                    wait_update = None

                if isinstance(wait_update, (ReadTimeout, RequestsConnectionError)):
                    container.kill()
                    timeout_output = "Command timed out and was terminated.\n"
                    yield ExecutionStreamUpdate(kind="output", data=timeout_output)
                    yield ExecutionStreamUpdate(
                        kind="result",
                        data="",
                        exit_code=124,
                    )
                    return

                if isinstance(wait_update, Exception):
                    raise wait_update

                if wait_update is not None:
                    wait_result = wait_update

                if monotonic() >= deadline:
                    container.kill()
                    timeout_output = "Command timed out and was terminated.\n"
                    yield ExecutionStreamUpdate(kind="output", data=timeout_output)
                    yield ExecutionStreamUpdate(
                        kind="result",
                        data="",
                        exit_code=124,
                    )
                    return

            while True:
                raw_chunk = output_queue.get()
                if raw_chunk is None:
                    break
                yield ExecutionStreamUpdate(
                    kind="output",
                    data=raw_chunk.decode("utf-8", errors="replace"),
                )
        except (ReadTimeout, RequestsConnectionError):
            try:
                container.kill()
            finally:
                timeout_output = "Command timed out and was terminated.\n"
                yield ExecutionStreamUpdate(kind="output", data=timeout_output)
                yield ExecutionStreamUpdate(
                    kind="result",
                    data="",
                    exit_code=124,
                )
        finally:
            container.remove(force=True)

        yield ExecutionStreamUpdate(
            kind="result",
            data="",
            exit_code=wait_result["StatusCode"],
        )


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


def execute_approved_command_stream(
    command_id: str,
    settings: Settings,
    runner: StreamingCommandRunner | None = None,
) -> Iterator[ExecutionStreamUpdate]:
    command = get_approved_command(command_id)
    execution_runner = runner or DockerCommandRunner()
    output_parts = []
    exit_code = 1

    for update in execution_runner.stream(command.cmd, settings):
        if update.kind == "output":
            output_parts.append(update.data)
            yield update
        else:
            exit_code = update.exit_code if update.exit_code is not None else 1

    output = "".join(output_parts)
    status: ExecutionStatus = "completed" if exit_code == 0 else "failed"

    with get_session() as db:
        add_execution_log(
            db,
            command.command_id,
            status,
            exit_code,
            output,
        )

    yield ExecutionStreamUpdate(kind="result", data="", exit_code=exit_code)
