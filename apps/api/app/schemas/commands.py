from typing import Literal

from pydantic import BaseModel


CommandStatus = Literal["proposed", "approved", "rejected"]
ApprovalDecision = Literal["approved", "rejected"]


class CommandApprovalRequest(BaseModel):
    decision: ApprovalDecision


class CommandApprovalResponse(BaseModel):
    command_id: str
    status: CommandStatus
    message: str
