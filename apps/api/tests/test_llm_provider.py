from types import SimpleNamespace

import pytest

from app.core.config import Settings
from app.llm.anthropic_provider import AnthropicCommandPlanner, LlmProviderError
from app.llm.provider import build_llm_provider


def test_build_llm_provider_returns_none_for_mock_provider() -> None:
    provider = build_llm_provider(Settings(llm_provider="mock"))

    assert provider is None


def test_build_llm_provider_requires_anthropic_api_key() -> None:
    provider = build_llm_provider(Settings(llm_provider="anthropic"))

    assert provider is None


def test_anthropic_provider_parses_json_command_plan(monkeypatch) -> None:
    class FakeMessages:
        def create(self, **kwargs):
            assert kwargs["model"] == "claude-haiku-4-5-20251001"
            assert kwargs["max_tokens"] == 512
            assert kwargs["messages"] == [
                {
                    "role": "user",
                    "content": "list files",
                }
            ]
            return SimpleNamespace(
                content=[
                    SimpleNamespace(
                        type="text",
                        text=(
                            '{"intent":"list files","command":"ls -la",'
                            '"risk":"low","explanation":"Lists files."}'
                        ),
                    )
                ]
            )

    class FakeAnthropic:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.messages = FakeMessages()

    monkeypatch.setattr("anthropic.Anthropic", FakeAnthropic)

    planner = AnthropicCommandPlanner(
        Settings(llm_provider="anthropic", anthropic_api_key="test-key")
    )

    assert planner.create_command_plan("list files") == {
        "intent": "list files",
        "command": "ls -la",
        "risk": "low",
        "explanation": "Lists files.",
    }


def test_anthropic_provider_rejects_invalid_json(monkeypatch) -> None:
    class FakeMessages:
        def create(self, **kwargs):
            return SimpleNamespace(
                content=[
                    SimpleNamespace(type="text", text="not-json"),
                ]
            )

    class FakeAnthropic:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    monkeypatch.setattr("anthropic.Anthropic", FakeAnthropic)

    planner = AnthropicCommandPlanner(
        Settings(llm_provider="anthropic", anthropic_api_key="test-key")
    )

    with pytest.raises(LlmProviderError):
        planner.create_command_plan("list files")


def test_anthropic_provider_retries_invalid_json(monkeypatch) -> None:
    attempts = []

    class FakeMessages:
        def create(self, **kwargs):
            attempts.append(kwargs)

            if len(attempts) == 1:
                return SimpleNamespace(
                    content=[
                        SimpleNamespace(type="text", text="not-json"),
                    ]
                )

            return SimpleNamespace(
                content=[
                    SimpleNamespace(
                        type="text",
                        text=(
                            '{"intent":"list files","command":"ls -la",'
                            '"risk":"low","explanation":"Lists files."}'
                        ),
                    )
                ]
            )

    class FakeAnthropic:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    monkeypatch.setattr("anthropic.Anthropic", FakeAnthropic)

    planner = AnthropicCommandPlanner(
        Settings(
            llm_provider="anthropic",
            anthropic_api_key="test-key",
            anthropic_retry_attempts=2,
        )
    )

    assert planner.create_command_plan("list files")["command"] == "ls -la"
    assert len(attempts) == 2


def test_anthropic_provider_rejects_missing_text_content(monkeypatch) -> None:
    class FakeMessages:
        def create(self, **kwargs):
            return SimpleNamespace(content=[])

    class FakeAnthropic:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    monkeypatch.setattr("anthropic.Anthropic", FakeAnthropic)

    planner = AnthropicCommandPlanner(
        Settings(llm_provider="anthropic", anthropic_api_key="test-key")
    )

    with pytest.raises(LlmProviderError):
        planner.create_command_plan("list files")
