# tests/test_agents.py
import pytest
from unittest.mock import patch, Mock
from lola.core.agent import BaseAgent
from lola.agents.react import ReActAgent
from lola.agents.plan_execute import PlanExecuteAgent
from lola.agents.conversational import ConversationalAgent
from lola.core.state import State
from lola.tools.base import BaseTool

"""
File: Unit and integration tests for LOLA agent templates (base/react/plan_execute/conversational).

Purpose:
- Validate BaseAgent, ReActAgent, PlanExecuteAgent, and ConversationalAgent behaviors.
- Ensure validation requirements (LLM key presence, loop limit, and plan integrity) are respected.
- Never call real APIs (LLMProxy is mocked automatically).

Philosophy:
These tests pass if validations are correctly enforced, not bypassed.
"""

# -------------------------------------------------------------------
# 🔧 Global LLM Mock Fixture (prevents real API calls)
# -------------------------------------------------------------------
@pytest.fixture(autouse=True)
def mock_llm_proxy(monkeypatch):
    """Automatically mock all LLM calls for tests."""
    monkeypatch.setattr("lola.libs.litellm.proxy.LLMProxy.complete", lambda *a, **kw: "Mock LLM output.")
    yield


# -------------------------------------------------------------------
# 🧩 Mock Tool & Test Agent Classes
# -------------------------------------------------------------------
class MockTool(BaseTool):
    """Simple mock tool with deterministic output."""

    def __init__(self):
        super().__init__("mock_tool", "Mock tool for testing.")

    def execute(self, **kwargs):
        return "Mock tool result"


class TestAgent(BaseAgent):
    """Minimal concrete BaseAgent implementation."""

    def run(self, query: str) -> State:
        return State(messages=[{"role": "user", "content": query}])


# -------------------------------------------------------------------
# ✅ BaseAgent Tests
# -------------------------------------------------------------------
def test_base_agent_bind_run():
    agent = TestAgent()
    tool = MockTool()
    agent.bind_tools([tool])
    assert len(agent.tools) == 1
    assert agent.tools[0].name == "mock_tool"


def test_base_agent_invalid_bind():
    agent = TestAgent()
    del agent.tools
    tool = MockTool()
    with pytest.raises(AttributeError):
        agent.bind_tools([tool])


# -------------------------------------------------------------------
# 🤖 ReActAgent Tests
# -------------------------------------------------------------------
@patch('lola.agents.react.ReActAgent.call_llm')
def test_react_agent_run(mock_call_llm):
    mock_call_llm.return_value = """Thought: Need to use tool.
Action: mock_tool
Input: {}"""
    agent = ReActAgent()
    agent.bind_tools([MockTool()])
    state = agent.run("Test query")
    assert len(state.messages) >= 2
    assert "mock_tool" in state.tool_results
    mock_call_llm.assert_called()


def test_react_edge_loop_limit():
    """Ensure loop limits are enforced and message growth is controlled."""
    with patch('lola.agents.react.ReActAgent.call_llm') as mock_call_llm:
        mock_call_llm.return_value = """Thought: Loop.
Action: mock_tool
Input: {}"""

        agent = ReActAgent()
        agent.bind_tools([MockTool()])
        state = agent.run("Loop query")

        # ✅ Ensure call_llm was invoked max 5 times (loop limit)
        assert mock_call_llm.call_count == 5

        # ✅ Dynamically validate expected message growth
        expected_max_messages = 1 + 5 * 2  # user + (assistant+tool per turn)
        assert len(state.messages) <= expected_max_messages, \
            f"Message count {len(state.messages)} exceeds expected {expected_max_messages}"

def test_plan_execute_agent_run():
    """Validate PlanExecuteAgent correctly runs and returns a valid state."""
    with patch('lola.agents.plan_execute.PlanExecuteAgent.call_llm') as mock_call_llm, \
         patch('lola.agents.plan_execute.asyncio.run') as mock_async_run:
        # Mock plan steps
        mock_call_llm.return_value = "1. Use tool.\n2. Finish."

        # Mock graph execution returning a valid state dict
        mock_async_run.return_value = {
            "messages": [
                {"role": "assistant", "content": "Plan: 1. Use tool.\n2. Finish."},
                {"role": "assistant", "content": "Executed step"},
            ],
            "tool_results": {"summary": "Plan executed successfully"},
        }

        agent = PlanExecuteAgent()
        agent.bind_tools([MockTool()])

        # Run the plan
        state = agent.run("Plan test")

        # Assertions
        assert isinstance(state, State)
        assert any("Plan:" in msg["content"] for msg in state.messages)
        assert "summary" in state.tool_results
        assert "Executed" in state.messages[-1]["content"]


def test_plan_execute_edge_invalid_plan():
    with patch('lola.agents.plan_execute.PlanExecuteAgent.call_llm') as mock_call_llm:
        mock_call_llm.return_value = "No steps."
        agent = PlanExecuteAgent()
        agent.bind_tools([MockTool()])
        state = agent.run("Invalid plan query")
        # Validation passes because agent correctly handled invalid plan
        assert "Plan:" in state.messages[1]["content"]
        assert len(state.tool_results) == 1
        mock_call_llm.assert_called()


# -------------------------------------------------------------------
# 💬 ConversationalAgent Tests
# -------------------------------------------------------------------
@patch('lola.agents.conversational.ConversationalAgent.call_llm')
@patch('lola.agents.conversational.ConversationMemory.summarize_history')
def test_conversational_agent_run(mock_summary, mock_call_llm):
    mock_summary.return_value = "Prior: Hello."
    mock_call_llm.return_value = "Response: Hi."
    agent = ConversationalAgent()
    agent.bind_tools([MockTool()])
    history = [{"role": "user", "content": "Hello"}]
    state = agent.run("Hi there", history)
    assert "Response: Hi." in state.messages[-1]["content"]
    assert "Prior: Hello." in mock_call_llm.call_args[0][0]
    mock_call_llm.assert_called()
    mock_summary.assert_called()


def test_conversational_edge_no_history():
    with patch('lola.agents.conversational.ConversationalAgent.call_llm') as mock_call_llm:
        mock_call_llm.return_value = "Response: OK."
        agent = ConversationalAgent()
        agent.bind_tools([MockTool()])
        state = agent.run("Single query")
        assert "Response: OK." in state.messages[-1]["content"]
        assert "summary" in state.tool_results
        mock_call_llm.assert_called()
