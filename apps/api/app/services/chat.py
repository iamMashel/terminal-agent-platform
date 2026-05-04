from uuid import uuid4

from app.agent.graph import run_terminal_agent
from app.agent.state import AgentState, CommandPlan
from app.db.repository import add_message
from app.db.session import get_session
from app.schemas.chat import ChatRequest, ChatResponse, CommandProposal
from app.services.commands import register_command_proposal


def create_mock_chat_response(request: ChatRequest) -> ChatResponse:
    agent_state = run_terminal_agent(request.message)
    persist_user_message(request.session_id, request.message)
    return create_chat_response_from_agent_state(request.session_id, agent_state)


def persist_user_message(session_id: str, message: str) -> None:
    with get_session() as db:
        add_message(db, session_id, "user", message)


def persist_assistant_message(session_id: str, message: str) -> None:
    with get_session() as db:
        add_message(db, session_id, "assistant", message)


def create_chat_response_from_agent_state(
    session_id: str,
    agent_state: AgentState,
) -> ChatResponse:
    command_plan = agent_state["command_plan"]

    if command_plan["command"] == "":
        persist_assistant_message(session_id, agent_state["response_message"])

        return ChatResponse(
            message=agent_state["response_message"],
            commands=[],
        )

    command = create_command_proposal(command_plan)
    register_command_proposal(command, session_id)
    persist_assistant_message(session_id, agent_state["response_message"])

    return ChatResponse(
        message=agent_state["response_message"],
        commands=[command],
    )


def create_command_proposal(command_plan: CommandPlan) -> CommandProposal:
    return CommandProposal(
        id=str(uuid4()),
        cmd=command_plan["command"],
        risk=command_plan["risk"],
        explanation=command_plan["explanation"],
    )
