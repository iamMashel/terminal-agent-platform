from dataclasses import dataclass

from app.db.repository import add_command, get_command, update_command_status
from app.db.session import get_session
from app.schemas.chat import CommandProposal
from app.schemas.commands import ApprovalDecision, CommandApprovalResponse, CommandStatus


class CommandNotFoundError(Exception):
    pass


class CommandStatusConflictError(Exception):
    pass


class CommandNotApprovedError(Exception):
    pass


@dataclass
class StoredCommand:
    command_id: str
    cmd: str
    risk: str
    explanation: str
    status: CommandStatus = "proposed"


def register_command_proposal(proposal: CommandProposal, session_id: str) -> None:
    with get_session() as db:
        add_command(db, session_id, proposal)


def record_command_approval(
    command_id: str,
    decision: ApprovalDecision,
) -> CommandApprovalResponse:
    with get_session() as db:
        command = get_command(db, command_id)

        if command is None:
            raise CommandNotFoundError

        if command.status != "proposed" and command.status != decision:
            raise CommandStatusConflictError

        command = update_command_status(db, command, decision)

        return CommandApprovalResponse(
            command_id=command.id,
            status=command.status,
            message=f"Command {command.status}.",
        )


def get_approved_command(command_id: str) -> StoredCommand:
    with get_session() as db:
        command = get_command(db, command_id)

        if command is None:
            raise CommandNotFoundError

        if command.status != "approved":
            raise CommandNotApprovedError

        return StoredCommand(
            command_id=command.id,
            cmd=command.cmd,
            risk=command.risk,
            explanation=command.explanation,
            status=command.status,
        )
