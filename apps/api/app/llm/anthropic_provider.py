import json

from pydantic import TypeAdapter, ValidationError

from app.agent.state import CommandPlan
from app.core.config import Settings

COMMAND_PLAN_ADAPTER = TypeAdapter(CommandPlan)

SYSTEM_PROMPT = """You help developers propose safe terminal commands.
Return only JSON with these keys: intent, command, risk, explanation.
Use risk as one of: low, medium, high.
Prefer safe read-only commands.
If the request is ambiguous or dangerous, return an empty command.
Never claim a command was executed."""


class LlmProviderError(Exception):
    pass


class AnthropicCommandPlanner:
    def __init__(self, settings: Settings) -> None:
        from anthropic import Anthropic

        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model
        self._max_tokens = settings.anthropic_max_tokens

    def create_command_plan(self, message: str) -> CommandPlan:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
        )

        text = _extract_text(response)

        try:
            payload = json.loads(text)
            return COMMAND_PLAN_ADAPTER.validate_python(payload)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise LlmProviderError("Claude returned an invalid command plan.") from exc


def _extract_text(response) -> str:
    chunks = [
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    ]

    if not chunks:
        raise LlmProviderError("Claude response did not include text content.")

    return "".join(chunks).strip()
