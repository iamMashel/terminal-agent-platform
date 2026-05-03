from typing import Literal, TypedDict


RiskLevel = Literal["low", "medium", "high"]


class CommandPlan(TypedDict):
    intent: str
    command: str
    risk: RiskLevel
    explanation: str


class AgentState(TypedDict, total=False):
    user_message: str
    normalized_message: str
    intent: str
    blocked: bool
    command_plan: CommandPlan
    response_message: str
