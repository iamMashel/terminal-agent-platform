from dataclasses import dataclass

from app.schemas.chat import CommandProposal
from app.schemas.commands import ApprovalDecision, CommandApprovalResponse, CommandStatus


class CommandNotFoundError(Exception):
    pass


class CommandStatusConflictError(Exception):
    pass


@dataclass
class StoredCommand:
    command_id: str
    cmd: str
    risk: str
    explanation: str
    status: CommandStatus = "proposed"


_commands: dict[str, StoredCommand] = {}


def register_command_proposal(proposal: CommandProposal) -> None:
    _commands[proposal.id] = StoredCommand(
        command_id=proposal.id,
        cmd=proposal.cmd,
        risk=proposal.risk,
        explanation=proposal.explanation,
        status=proposal.status,
    )


def record_command_approval(
    command_id: str,
    decision: ApprovalDecision,
) -> CommandApprovalResponse:
    command = _commands.get(command_id)

    if command is None:
        raise CommandNotFoundError

    if command.status != "proposed" and command.status != decision:
        raise CommandStatusConflictError

    command.status = decision

    return CommandApprovalResponse(
        command_id=command.command_id,
        status=command.status,
        message=f"Command {command.status}. Execution is not implemented in this phase.",
    )
