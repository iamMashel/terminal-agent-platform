from typing import Literal

from pydantic import BaseModel


CommandStatus = Literal["proposed", "approved", "rejected"]
ApprovalDecision = Literal["approved", "rejected"]
ExecutionStatus = Literal["completed", "failed"]


class CommandApprovalRequest(BaseModel):
    decision: ApprovalDecision


class CommandApprovalResponse(BaseModel):
    command_id: str
    status: CommandStatus
    message: str


class CommandExecutionResponse(BaseModel):
    command_id: str
    status: ExecutionStatus
    exit_code: int
    output: str
