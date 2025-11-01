# tests/test_agents.py
# Standard imports
import pytest
import asyncio
import typing as tp

# Third-party imports
# None

# Local imports
from lola.core.state import State
from lola.core.graph import StateGraph
from lola.core.agent import BaseAgent
from lola.agents.react import ReActAgent
from lola.agents.plan_execute import PlanExecuteAgent
from lola.agents.conversational import ConversationalAgent
from lola.core.memory import ConversationMemory

"""
File: Tests for LOLA agent templates.

Purpose: Validates ReAct, Plan-Execute, and Conversational agent behavior.
How: Tests unit (single runs), integration (graphs), and edge cases (max loops, empty inputs).
Why: Ensures robust agent templates for V1 workflows.
Full Path: lola-os/tests/test_agents.py
"""

@pytest.mark.asyncio
async def test_react_loop() -> None:
    """Unit: ReActAgent executes reason-act loop."""
    agent = ReActAgent(model="mock-model")
    agent.max_iterations = 1  # One full cycle
    final = await agent.run("Solve a math problem")
    assert len(final.messages) == 3  # Query + reason + act
    assert final.messages[1]["content"].startswith("Stub LLM response")
    assert final.messages[2]["content"] == "Action taken"
    assert final.reflection is None

@pytest.mark.asyncio
async def test_react_max_loops() -> None:
    """Edge: ReActAgent stops at max iterations."""
    agent = ReActAgent(model="mock-model")
    agent.max_iterations = 0  # Halt immediately after query
    final = await agent.run("Infinite task")
    assert len(final.messages) == 1  # Query only
    assert final.reflection == "Max turns reached; halting execution to prevent loops."

@pytest.mark.asyncio
async def test_plan_execute() -> None:
    """Unit: PlanExecuteAgent plans and executes."""
    agent = PlanExecuteAgent(model="mock-model")
    final = await agent.run("Plan a trip")
    assert len(final.messages) == 3  # Query + plan + execute
    assert final.messages[1]["content"].startswith("Stub LLM response")
    assert final.messages[2]["content"] == "Executing plan"
    assert final.reflection is None

@pytest.mark.asyncio
async def test_conversational_context() -> None:
    """Integration: ConversationalAgent retains context."""
    memory = ConversationMemory()
    memory.append({"role": "user", "content": "Hi, I'm Alice"})
    agent = ConversationalAgent(model="mock-model", memory=memory)
    final = await agent.run("What's my name?")
    assert len(final.messages) == 3  # Memory + query + response
    assert final.messages[2]["content"].startswith("Stub LLM response")
    assert "Alice" in final.messages[2]["content"]
    assert len(memory.retrieve()) == 3  # Original + query + response
    assert final.reflection is None

@pytest.mark.asyncio
async def test_conversational_empty() -> None:
    """Edge: ConversationalAgent handles empty memory."""
    agent = ConversationalAgent(model="mock-model")
    final = await agent.run("Hello")
    assert len(final.messages) == 2  # Query + response
    assert final.reflection is None

__all__ = []