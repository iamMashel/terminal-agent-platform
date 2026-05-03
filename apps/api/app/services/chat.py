from uuid import uuid4

from app.schemas.chat import ChatRequest, ChatResponse, CommandProposal
from app.services.commands import register_command_proposal


def create_mock_chat_response(request: ChatRequest) -> ChatResponse:
    clean_message = request.message.strip()
    command = create_mock_command_proposal(clean_message)
    register_command_proposal(command)

    return ChatResponse(
        message="Here is a command proposal.",
        commands=[command],
    )


def create_mock_command_proposal(message: str) -> CommandProposal:
    normalized_message = message.lower()

    if "txt" in normalized_message or "text" in normalized_message:
        return CommandProposal(
            id=str(uuid4()),
            cmd="find . -name '*.txt'",
            risk="low",
            explanation="Finds all .txt files recursively from the current directory.",
        )

    if "file" in normalized_message or "list" in normalized_message:
        return CommandProposal(
            id=str(uuid4()),
            cmd="ls -la",
            risk="low",
            explanation="Lists files in the current directory, including hidden entries.",
        )

    return CommandProposal(
        id=str(uuid4()),
        cmd="pwd",
        risk="low",
        explanation="Prints the current working directory without changing any files.",
    )
