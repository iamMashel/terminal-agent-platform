from collections.abc import AsyncIterator

from app.agent.graph import stream_terminal_agent
from app.agent.state import AgentState
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import (
    create_command_proposal,
    persist_assistant_message,
    persist_user_message,
)
from app.services.commands import register_command_proposal


def format_sse_event(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


async def stream_chat_response(response: ChatResponse) -> AsyncIterator[str]:
    yield format_sse_event("status", "Understanding request...")
    yield format_sse_event("reasoning", "This is a read-only file discovery task.")

    for command in response.commands:
        yield format_sse_event("command", command.model_dump_json())

    yield format_sse_event("done", "complete")


async def stream_agent_chat_response(request: ChatRequest) -> AsyncIterator[str]:
    persist_user_message(request.session_id, request.message)
    agent_state: AgentState = {"user_message": request.message}

    yield format_sse_event("status", "Planning request...")

    for update in stream_terminal_agent(request.message):
        node_name, node_state = next(iter(update.items()))
        agent_state.update(node_state)

        if node_name == "planner":
            yield format_sse_event("reasoning", f"Intent: {agent_state['intent']}")
            yield format_sse_event("status", "Checking command safety...")
        elif node_name == "safety_validator":
            if agent_state["blocked"]:
                yield format_sse_event("reasoning", "Request blocked by safety rules.")
            else:
                yield format_sse_event("reasoning", "Request passed safety validation.")
            yield format_sse_event("status", "Generating command proposal...")
        elif node_name == "command_generator":
            command_plan = agent_state["command_plan"]
            yield format_sse_event("reasoning", command_plan["explanation"])

            if command_plan["command"] != "":
                command = create_command_proposal(command_plan)
                register_command_proposal(command, request.session_id)
                yield format_sse_event("command", command.model_dump_json())
        elif node_name == "explanation":
            persist_assistant_message(request.session_id, agent_state["response_message"])
            yield format_sse_event("status", "Response ready.")

    yield format_sse_event("done", "complete")
