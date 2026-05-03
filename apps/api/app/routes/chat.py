import logging

from fastapi import APIRouter, Request

from app.core.observability import get_trace_context, log_event
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import create_mock_chat_response

router = APIRouter()
logger = logging.getLogger("app.chat")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, fastapi_request: Request) -> ChatResponse:
    context = get_trace_context(fastapi_request)
    response = create_mock_chat_response(request)
    log_event(
        logger,
        "chat.response_created",
        context,
        f"Created chat response with {len(response.commands)} command proposals",
    )
    return response
