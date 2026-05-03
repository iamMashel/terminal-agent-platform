from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=4000)


class CommandProposal(BaseModel):
    id: str
    cmd: str
    risk: Literal["low", "medium", "high"]
    explanation: str
    status: Literal["proposed", "approved", "rejected"] = "proposed"


class ChatResponse(BaseModel):
    message: str
    commands: list[CommandProposal] = Field(default_factory=list)
