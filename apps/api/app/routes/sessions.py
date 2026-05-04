from fastapi import APIRouter, HTTPException, status

from app.db.repository import create_session, get_session_snapshot, list_sessions
from app.db.session import get_session
from app.schemas.sessions import (
    SessionCommand,
    SessionCreateData,
    SessionCreateResponse,
    SessionDetailData,
    SessionDetailResponse,
    SessionListItem,
    SessionListResponse,
    SessionMessage,
)

router = APIRouter()


@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session_route() -> SessionCreateResponse:
    with get_session() as db:
        session = create_session(db)

    return SessionCreateResponse(data=SessionCreateData(session_id=session.id))


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions_route() -> SessionListResponse:
    with get_session() as db:
        sessions = list_sessions(db)

    return SessionListResponse(
        data=[SessionListItem(id=session.id) for session in sessions]
    )


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session_route(session_id: str) -> SessionDetailResponse:
    with get_session() as db:
        session = get_session_snapshot(db, session_id)

        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found.",
            )

        messages = [
            SessionMessage(role=message.role, content=message.content)
            for message in sorted(session.messages, key=lambda item: item.created_at)
        ]
        commands = [
            SessionCommand(
                id=command.id,
                cmd=command.cmd,
                risk=command.risk,
                status=command.status,
                output=command.execution_logs[-1].output
                if command.execution_logs
                else None,
            )
            for command in sorted(session.commands, key=lambda item: item.created_at)
        ]

    return SessionDetailResponse(
        data=SessionDetailData(messages=messages, commands=commands)
    )
