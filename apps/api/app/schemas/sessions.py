from pydantic import BaseModel


class SessionCreateData(BaseModel):
    session_id: str


class SessionCreateResponse(BaseModel):
    success: bool = True
    data: SessionCreateData


class SessionListItem(BaseModel):
    id: str


class SessionListResponse(BaseModel):
    success: bool = True
    data: list[SessionListItem]


class SessionMessage(BaseModel):
    role: str
    content: str


class SessionCommand(BaseModel):
    id: str
    cmd: str
    risk: str
    status: str
    output: str | None


class SessionDetailData(BaseModel):
    messages: list[SessionMessage]
    commands: list[SessionCommand]


class SessionDetailResponse(BaseModel):
    success: bool = True
    data: SessionDetailData
