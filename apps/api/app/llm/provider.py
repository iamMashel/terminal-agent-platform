from typing import Protocol

from app.agent.state import CommandPlan
from app.core.config import Settings


class LlmProvider(Protocol):
    def create_command_plan(self, message: str) -> CommandPlan:
        pass


def build_llm_provider(settings: Settings) -> LlmProvider | None:
    if settings.llm_provider != "anthropic":
        return None

    if settings.anthropic_api_key is None:
        return None

    from app.llm.anthropic_provider import AnthropicCommandPlanner

    return AnthropicCommandPlanner(settings)
