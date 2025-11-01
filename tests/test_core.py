# Standard imports
import asyncio
from pathlib import Path
from typing import Any

# Third-party imports
import pytest
from langchain_core.runnables import RunnableConfig

# Local imports
from lola.core.agent import BaseAgent
from lola.core.graph import StateGraph
from lola.core.memory import ConversationMemory, EntityMemory, StateManager
from lola.core.state import State

"""
File: Comprehensive test suite for Phase-1 core components.

Purpose: Verify that State, Graph, Memory, and BaseAgent behave exactly as specified.
How: Uses pytest for unit, integration, and edge-case coverage; async tests are marked.
Why: Guarantees >80% coverage, prevents regressions, and serves as executable documentation.
Full Path: lola-os/tests/test_core.py
"""

# ----------------------------------------------------------------------
# State tests
# ----------------------------------------------------------------------
def test_state_validation() -> None:
    """
    Unit: Validate State creation and Pydantic enforcement.

    Does Not: Test persistence – that belongs to memory tests.
    """
    # Inline: Valid payload
    state = State(messages=[{"role": "user", "content": "test"}])
    assert len(state.messages) == 1

    # Inline: Edge – wrong type should raise ValidationError
    with pytest.raises(ValueError):
        State(messages="not a list")  # type: ignore[arg-type]


# ----------------------------------------------------------------------
# Graph tests (async)
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_graph_execute_simple() -> None:
    """Integration: Single node runs once and stops."""
    graph = StateGraph()

    def node_func(state: State) -> State:
        state.messages.append({"role": "system", "content": "processed"})
        return state

    graph.add_node("test_node", node_func)
    graph.add_edge("test_node", "__end__")
    graph.set_entry_point("test_node")

    final_state = await graph.execute(State())
    assert len(final_state.messages) == 1
    assert final_state.messages[0]["content"] == "processed"
    assert final_state.reflection is None

@pytest.mark.asyncio
async def test_graph_supervision_limits() -> None:
    """Edge: Infinite loop halts with reflection on raise."""
    graph = StateGraph()
    graph.max_turns = 3

    def loop_node(state: State) -> State:
        state.messages.append({"content": f"turn {len(state.messages) + 1}"})
        return state

    graph.add_node("loop", loop_node)
    graph.add_edge("loop", "loop")
    graph.set_entry_point("loop")

    final = await graph.execute(State())
    assert final.reflection == "Max turns reached; halting execution to prevent loops."
    assert len(final.messages) == 0  # Since raise, initial state returned

@pytest.mark.asyncio
async def test_graph_reflection_threshold() -> None:
    """Unit: Reflection added post if threshold exceeded in multi-step."""
    graph = StateGraph()
    graph.reflection_threshold = 2
    graph.max_turns = 100

    def node1(state: State) -> State:
        state.messages.append({"content": "step1"})
        return state

    def node2(state: State) -> State:
        state.messages.append({"content": "step2"})
        return state

    def node3(state: State) -> State:
        state.messages.append({"content": "step3"})
        return state

    graph.add_node("node1", node1)
    graph.add_node("node2", node2)
    graph.add_node("node3", node3)

    graph.set_entry_point("node1")
    graph.add_edge("node1", "node2")
    graph.add_edge("node2", "node3")
    graph.add_edge("node3", "__end__")

    final = await graph.execute(State())
    assert len(final.messages) == 3
    assert final.reflection is not None
    assert "Reflection: Processed 3 steps" in final.reflection


# ----------------------------------------------------------------------
# Memory tests
# ----------------------------------------------------------------------
def test_memory_save_load(tmp_path: Path) -> None:
    """
    Integration: Save a State to JSON and load it back unchanged.

    Args:
        tmp_path: Pytest fixture providing a temporary directory.

    Does Not: Test concurrent writes – out of Phase-1 scope.
    """
    path = tmp_path / "state.json"
    original = State(
        messages=[{"role": "user", "content": "test"}],
        tools_results={"tool": "result"},
    )
    StateManager.save(original, path)
    loaded = StateManager.load(path)

    assert loaded.messages == original.messages
    assert loaded.tools_results == original.tools_results


def test_conversation_memory() -> None:
    """
    Unit: Append messages and retrieve full or partial history.

    Does Not: Test persistence – that belongs to StateManager.
    """
    mem = ConversationMemory()
    mem.append({"role": "user", "content": "hello"})
    mem.append({"role": "system", "content": "response"})

    assert len(mem.retrieve()) == 2
    assert len(mem.retrieve(1)) == 1
    assert mem.retrieve(1)[0]["content"] == "response"


def test_entity_memory_stub() -> None:
    """
    Unit: Confirm the stub entity extractor returns an empty dict.

    Does Not: Perform real NLP – stub is intentional for V1.
    """
    mem = EntityMemory()
    result = mem.extract("Sample text with entities")
    assert result == {"entities": []}


# ----------------------------------------------------------------------
# Agent tests
# ----------------------------------------------------------------------
def test_agent_init_and_stub() -> None:
    """
    Unit: Initialise BaseAgent, bind tools, and verify LLM stub.

    Does Not: Call a real LLM – stubbed for Phase-1.
    """
    # Inline: Concrete subclass to satisfy abstract run
    class TestAgent(BaseAgent):
        def run(self, query: str) -> State:
            self.state.messages.append({"content": query})
            return self.state

    agent = TestAgent(model="test-model")
    assert agent.model == "test-model"
    assert len(agent.tools) == 0

    agent.bind_tools(["tool1", "tool2"])
    assert len(agent.tools) == 2

    response = agent.call_llm("test prompt")
    assert response.startswith("Stub LLM response")

    final_state = agent.run("query")
    assert len(final_state.messages) == 1
    assert final_state.messages[0]["content"] == "query"


def test_agent_abstract_enforcement() -> None:
    """
    Edge: Ensure BaseAgent cannot be instantiated without implementing run.

    Does Not: Test any other abstract methods – none exist in V1.
    """
    # Inline: Python 3.12 raises TypeError on instantiation of abstract class
    with pytest.raises(TypeError):
        BaseAgent(model="stub")


# ----------------------------------------------------------------------
# Export list for static analysis tools
# ----------------------------------------------------------------------
__all__ = [
    "test_state_validation",
    "test_graph_execute_simple",
    "test_graph_supervision_limits",
    "test_graph_reflection_threshold",
    "test_memory_save_load",
    "test_conversation_memory",
    "test_entity_memory_stub",
    "test_agent_init_and_stub",
    "test_agent_abstract_enforcement",
]