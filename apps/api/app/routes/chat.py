from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import create_mock_chat_response

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return create_mock_chat_response(request)
