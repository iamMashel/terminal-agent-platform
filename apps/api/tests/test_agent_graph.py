from app.agent.graph import run_terminal_agent
from app.core.config import get_settings
from app.llm.anthropic_provider import LlmProviderError


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


def test_agent_graph_falls_back_when_llm_provider_fails(monkeypatch) -> None:
    class FailingProvider:
        def create_command_plan(self, message):
            raise LlmProviderError("provider failed")

    monkeypatch.setattr(
        "app.agent.graph.build_llm_provider",
        lambda settings: FailingProvider(),
    )

    state = run_terminal_agent("list files")

    assert state["command_plan"] == {
        "intent": "list files",
        "command": "ls -la",
        "risk": "low",
        "explanation": "Lists files in the current directory, including hidden entries.",
    }


def test_agent_graph_blocks_dangerous_llm_command(monkeypatch) -> None:
    class DangerousProvider:
        def create_command_plan(self, message):
            return {
                "intent": message,
                "command": "rm -rf .",
                "risk": "low",
                "explanation": "Bad provider output.",
            }

    monkeypatch.setattr(
        "app.agent.graph.build_llm_provider",
        lambda settings: DangerousProvider(),
    )

    state = run_terminal_agent("clean the project")

    assert state["command_plan"] == {
        "intent": "clean the project",
        "command": "",
        "risk": "high",
        "explanation": "No command is proposed because the generated command is dangerous.",
    }
