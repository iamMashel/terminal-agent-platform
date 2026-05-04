import logging

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from app.core.observability import get_trace_context, log_event
from app.core.sse import stream_chat_response
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


@router.get("/chat/stream")
async def stream_chat(
    fastapi_request: Request,
    session_id: str = Query(min_length=1),
    message: str = Query(min_length=1, max_length=4000),
) -> StreamingResponse:
    context = get_trace_context(fastapi_request)
    response = create_mock_chat_response(
        ChatRequest(session_id=session_id, message=message)
    )
    log_event(
        logger,
        "chat.stream_created",
        context,
        f"Created chat stream with {len(response.commands)} command proposals",
    )
    return StreamingResponse(
        stream_chat_response(response),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
