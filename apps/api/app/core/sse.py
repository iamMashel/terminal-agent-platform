from collections.abc import AsyncIterator

from app.schemas.chat import ChatResponse


def format_sse_event(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


async def stream_chat_response(response: ChatResponse) -> AsyncIterator[str]:
    yield format_sse_event("status", "Understanding request...")
    yield format_sse_event("reasoning", "This is a read-only file discovery task.")

    for command in response.commands:
        yield format_sse_event("command", command.model_dump_json())

    yield format_sse_event("done", "complete")
