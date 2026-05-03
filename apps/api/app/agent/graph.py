from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.agent.state import AgentState, CommandPlan
from app.core.config import get_settings
from app.llm.provider import build_llm_provider

DANGEROUS_PATTERNS = (
    "rm -rf",
    "mkfs",
    "shutdown",
    "reboot",
    ":(){",
    "fork bomb",
)


def planner_node(state: AgentState) -> AgentState:
    message = state["user_message"].strip()
    return {
        "normalized_message": message.lower(),
        "intent": message,
    }


def safety_validator_node(state: AgentState) -> AgentState:
    normalized_message = state["normalized_message"]
    blocked = any(pattern in normalized_message for pattern in DANGEROUS_PATTERNS)

    return {"blocked": blocked}


def command_generator_node(state: AgentState) -> AgentState:
    if state["blocked"]:
        return {
            "command_plan": CommandPlan(
                intent=state["intent"],
                command="",
                risk="high",
                explanation="No command is proposed because the request is dangerous.",
            )
        }

    provider = build_llm_provider(get_settings())

    if provider is not None:
        command_plan = provider.create_command_plan(state["intent"])
        return {
            "command_plan": CommandPlan(
                intent=command_plan["intent"],
                command=command_plan["command"],
                risk=command_plan["risk"],
                explanation=command_plan["explanation"],
            )
        }

    normalized_message = state["normalized_message"]

    if "txt" in normalized_message or "text" in normalized_message:
        return {
            "command_plan": CommandPlan(
                intent=state["intent"],
                command="find . -name '*.txt'",
                risk="low",
                explanation=(
                    "Finds all .txt files recursively from the current directory."
                ),
            )
        }

    if "file" in normalized_message or "list" in normalized_message:
        return {
            "command_plan": CommandPlan(
                intent=state["intent"],
                command="ls -la",
                risk="low",
                explanation=(
                    "Lists files in the current directory, including hidden entries."
                ),
            )
        }

    return {
        "command_plan": CommandPlan(
            intent=state["intent"],
            command="pwd",
            risk="low",
            explanation="Prints the current working directory without changing any files.",
        )
    }


def explanation_node(state: AgentState) -> AgentState:
    if state["blocked"]:
        return {
            "response_message": (
                "I cannot propose a command for that request because it appears dangerous."
            )
        }

    return {"response_message": "Here is a command proposal."}


@lru_cache
def build_terminal_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("safety_validator", safety_validator_node)
    graph.add_node("command_generator", command_generator_node)
    graph.add_node("explanation", explanation_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "safety_validator")
    graph.add_edge("safety_validator", "command_generator")
    graph.add_edge("command_generator", "explanation")
    graph.add_edge("explanation", END)

    return graph.compile()


def run_terminal_agent(message: str) -> AgentState:
    graph = build_terminal_agent_graph()
    return graph.invoke({"user_message": message})
