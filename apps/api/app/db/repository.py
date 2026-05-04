from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CommandModel, ExecutionLogModel, MessageModel, SessionModel
from app.schemas.chat import CommandProposal
from app.schemas.commands import CommandStatus, ExecutionStatus


def create_session(db: Session) -> SessionModel:
    session = SessionModel(id=str(uuid4()))
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def ensure_session(db: Session, session_id: str) -> SessionModel:
    session = db.get(SessionModel, session_id)

    if session is not None:
        return session

    session = SessionModel(id=session_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: Session) -> list[SessionModel]:
    return list(db.scalars(select(SessionModel).order_by(SessionModel.created_at)))


def add_message(db: Session, session_id: str, role: str, content: str) -> MessageModel:
    ensure_session(db, session_id)
    message = MessageModel(session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def add_command(
    db: Session,
    session_id: str,
    proposal: CommandProposal,
) -> CommandModel:
    ensure_session(db, session_id)
    command = db.get(CommandModel, proposal.id)

    if command is None:
        command = CommandModel(
            id=proposal.id,
            session_id=session_id,
            cmd=proposal.cmd,
            risk=proposal.risk,
            explanation=proposal.explanation,
            status=proposal.status,
        )
        db.add(command)
    else:
        command.session_id = session_id
        command.cmd = proposal.cmd
        command.risk = proposal.risk
        command.explanation = proposal.explanation
        command.status = proposal.status

    db.commit()
    db.refresh(command)
    return command


def get_command(db: Session, command_id: str) -> CommandModel | None:
    return db.get(CommandModel, command_id)


def update_command_status(
    db: Session,
    command: CommandModel,
    status: CommandStatus,
) -> CommandModel:
    command.status = status
    db.commit()
    db.refresh(command)
    return command


def add_execution_log(
    db: Session,
    command_id: str,
    status: ExecutionStatus,
    exit_code: int,
    output: str,
) -> ExecutionLogModel:
    execution_log = ExecutionLogModel(
        command_id=command_id,
        status=status,
        exit_code=exit_code,
        output=output,
    )
    db.add(execution_log)
    db.commit()
    db.refresh(execution_log)
    return execution_log


def get_session_snapshot(db: Session, session_id: str) -> SessionModel | None:
    return db.get(SessionModel, session_id)
