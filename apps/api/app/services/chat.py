from uuid import uuid4

from app.agent.graph import run_terminal_agent
from app.db.repository import add_message
from app.db.session import get_session
from app.schemas.chat import ChatRequest, ChatResponse, CommandProposal
from app.services.commands import register_command_proposal


def create_mock_chat_response(request: ChatRequest) -> ChatResponse:
    agent_state = run_terminal_agent(request.message)
    command_plan = agent_state["command_plan"]

    with get_session() as db:
        add_message(db, request.session_id, "user", request.message)

    if command_plan["command"] == "":
        with get_session() as db:
            add_message(
                db,
                request.session_id,
                "assistant",
                agent_state["response_message"],
            )

        return ChatResponse(
            message=agent_state["response_message"],
            commands=[],
        )

    command = CommandProposal(
        id=str(uuid4()),
        cmd=command_plan["command"],
        risk=command_plan["risk"],
        explanation=command_plan["explanation"],
    )

    register_command_proposal(command, request.session_id)

    with get_session() as db:
        add_message(
            db,
            request.session_id,
            "assistant",
            agent_state["response_message"],
        )

    return ChatResponse(
        message=agent_state["response_message"],
        commands=[command],
    )
