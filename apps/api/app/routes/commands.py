import logging

from fastapi import APIRouter, HTTPException, status
from fastapi import Request

from app.core.config import get_settings
from app.core.observability import get_trace_context, log_event
from app.schemas.commands import (
    CommandApprovalRequest,
    CommandApprovalResponse,
    CommandExecutionResponse,
)
from app.services.commands import (
    CommandNotApprovedError,
    CommandNotFoundError,
    CommandStatusConflictError,
    record_command_approval,
)
from app.services.execution import execute_approved_command

router = APIRouter()
logger = logging.getLogger("app.commands")


@router.post(
    "/commands/{command_id}/approval",
    response_model=CommandApprovalResponse,
)
async def approve_command(
    command_id: str,
    request: CommandApprovalRequest,
    fastapi_request: Request,
) -> CommandApprovalResponse:
    context = get_trace_context(fastapi_request)
    try:
        response = record_command_approval(command_id, request.decision)
        log_event(
            logger,
            "command.approval_recorded",
            context,
            f"Command {command_id} marked {response.status}",
        )
        return response
    except CommandNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Command proposal not found.",
        ) from exc
    except CommandStatusConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Command has already received a different approval decision.",
        ) from exc


@router.post(
    "/commands/{command_id}/execute",
    response_model=CommandExecutionResponse,
)
async def execute_command(
    command_id: str,
    request: Request,
) -> CommandExecutionResponse:
    context = get_trace_context(request)
    try:
        response = execute_approved_command(command_id, get_settings())
        log_event(
            logger,
            "command.execution_completed",
            context,
            f"Command {command_id} execution {response.status}",
        )
        return response
    except CommandNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Command proposal not found.",
        ) from exc
    except CommandNotApprovedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Command must be approved before execution.",
        ) from exc
