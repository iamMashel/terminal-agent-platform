from app.agent.graph import run_terminal_agent
from app.core.config import get_settings


def test_agent_graph_generates_file_listing_plan() -> None:
    state = run_terminal_agent("list files")

    assert state["response_message"] == "Here is a command proposal."
    assert state["command_plan"] == {
        "intent": "list files",
        "command": "ls -la",
        "risk": "low",
        "explanation": "Lists files in the current directory, including hidden entries.",
    }


def test_agent_graph_blocks_dangerous_command_request() -> None:
    state = run_terminal_agent("please rm -rf everything")

    assert state["blocked"] is True
    assert state["response_message"] == (
        "I cannot propose a command for that request because it appears dangerous."
    )
    assert state["command_plan"] == {
        "intent": "please rm -rf everything",
        "command": "",
        "risk": "high",
        "explanation": "No command is proposed because the request is dangerous.",
    }


def test_agent_graph_uses_configured_llm_provider(monkeypatch) -> None:
    class FakeProvider:
        def create_command_plan(self, message):
            assert message == "show current directory"
            return {
                "intent": message,
                "command": "pwd",
                "risk": "low",
                "explanation": "Prints the current working directory.",
            }

    monkeypatch.setattr("app.agent.graph.build_llm_provider", lambda settings: FakeProvider())
    get_settings.cache_clear()

    try:
        state = run_terminal_agent("show current directory")
    finally:
        get_settings.cache_clear()

    assert state["command_plan"] == {
        "intent": "show current directory",
        "command": "pwd",
        "risk": "low",
        "explanation": "Prints the current working directory.",
    }
