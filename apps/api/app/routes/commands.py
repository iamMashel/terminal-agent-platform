from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
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


@router.post(
    "/commands/{command_id}/approval",
    response_model=CommandApprovalResponse,
)
async def approve_command(
    command_id: str,
    request: CommandApprovalRequest,
) -> CommandApprovalResponse:
    try:
        return record_command_approval(command_id, request.decision)
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
async def execute_command(command_id: str) -> CommandExecutionResponse:
    try:
        return execute_approved_command(command_id, get_settings())
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
