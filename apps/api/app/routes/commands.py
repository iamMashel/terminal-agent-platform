from fastapi import APIRouter, HTTPException, status

from app.schemas.commands import CommandApprovalRequest, CommandApprovalResponse
from app.services.commands import (
    CommandNotFoundError,
    CommandStatusConflictError,
    record_command_approval,
)

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
