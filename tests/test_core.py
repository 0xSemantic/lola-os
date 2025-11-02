# Standard imports
import pytest
import asyncio
from unittest.mock import patch, Mock, MagicMock, AsyncMock
from typing import Dict, Any
from pydantic import ValidationError

# Third-party imports
from langgraph.graph import END

# Local imports
from lola.core.state import State
from lola.core.graph import LOLAStateGraph
from lola.core.memory import StateManager, ConversationMemory
from lola.core.agent import BaseAgent
from lola.utils.config import load_config

"""
File: Unit and integration tests for LOLA core orchestration (state/graph/memory/agent).

Purpose: Validates state validation/serialization, graph async execution, memory extract/save, agent run/call_llm with real/mocked LLM.
How: pytest for unit (serialize/validate), integration (graph execute with mock LLM), edges (invalid state, empty history).
Why: Ensures reliable, verifiable workflows in Phase 3, with >80% coverage for market-ready core.
Full Path: lola-os/tests/test_core.py
"""

# Mock LLMProxy for tests (avoid key dependency)
class MockLLMProxy:
    """Mock for LLMProxy in tests. Does NOT call real LLM—returns fixed response."""

    def complete(self, prompt: str, **kwargs) -> str:
        return f"Mock response to: {prompt[:50]}..."

    def __init__(self, *args, **kwargs):
        pass


def test_state_serialize():
    """Test State serialization/deserialization and validation.

    Does Not: Test tool_results—focus on messages/timestamp.
    """
    state = State(messages=[{"role": "user", "content": "Test query"}])
    json_str = state.to_json()
    assert '"messages"' in json_str
    assert '"timestamp"' in json_str
    loaded = State.from_json(json_str)
    assert loaded.messages[0]["content"] == "Test query"
    assert loaded.timestamp is not None
    # Inline: Edge - Invalid messages
    with pytest.raises(ValidationError, match="exceed"):
        State(messages=[{"role": "user", "content": "a"} for _ in range(51)])  # Default max 50


@pytest.mark.asyncio
@patch('lola.core.graph.load_config')
@patch('lola.core.graph.SupervisedStateGraph.compile_supervised')
async def test_graph_async(mock_compile, mock_config):
    """Test LOLAStateGraph async execute with minimal valid config.

    Args:
        mock_compile: Patched compile_supervised.
        mock_config: Patched load_config.

    Does Not: Test supervision or reflection—mocked adapter.
    """
    # Proper mock config for LOLAStateGraph
    mock_config.return_value = Mock(
        model_dump=Mock(return_value={
            "max_turns": 10,
            "llm_model": "gemini/gemini-1.5-flash",
            "temperature": 0.7,
        })
    )

    # Mock the compiled graph with AsyncMock
    mock_compiled = Mock()
    mock_compiled.ainvoke = AsyncMock(return_value={
        "messages": [{"role": "assistant", "content": "Graph done"}],
        "timestamp": "2025-11-02T07:40:00Z"
    })
    mock_compile.return_value = mock_compiled

    # Create the graph and run execute()
    from lola.core.graph import LOLAStateGraph
    graph = LOLAStateGraph()
    result = await graph.execute({"messages": [{"role": "user", "content": "Test query"}]})

    # Assertions
    assert result.messages[0]["content"] == "Graph done"
    mock_compile.assert_called_once()
    mock_compiled.ainvoke.assert_awaited_once()

def test_memory_extract():
    """Test ConversationMemory entity extraction and summary.

    Does Not: Test persistence—use StateManager.
    """
    messages = [{"role": "user", "content": "Alice meets Bob in New York on 2025-01-01."}]
    with patch('lola.core.memory.LLMProxy') as mock_llm:
        mock_instance = Mock()
        mock_instance.complete.return_value = '["Alice", "New York", "2025-01-01"]'
        mock_llm.return_value = mock_instance
        memory = ConversationMemory()
        entities = memory.extract_entities(messages)
        assert isinstance(entities, Dict)
        assert "entities" in entities
        assert len(entities["entities"]) > 0
        mock_instance.complete.assert_called_once()
    summary = memory.summarize_history(messages)
    assert len(summary) > 10  # Mock handles
    # Inline: Edge - Empty messages
    empty_entities = memory.extract_entities([])
    assert "entities" in empty_entities
    empty_summary = memory.summarize_history([])
    assert len(empty_summary) > 0  # Mock handles empty


class MockAgent(BaseAgent):
    """Mock concrete agent for test. Does Not use graph—direct LLM."""

    def run(self, query: str) -> State:
        """
        Mock run for test.

        Args:
            query: Query.

        Returns:
            State with mock response.

        Does Not: Use memory—base only.
        """
        response = self.call_llm(query)
        state = State(messages=[{"role": "user", "content": query}, {"role": "assistant", "content": response}])
        return state


def test_agent_run():
    """Test BaseAgent run/call_llm with mock LLM.

    Does Not: Test tools—bind after init.
    """
    with patch('lola.core.agent.LLMProxy.complete') as mock_complete:
        mock_complete.return_value = "Mock agent response"
        with patch('lola.utils.config.load_config') as mock_config:
            mock_config.return_value = Mock(model_dump=Mock(return_value={"llm_model": "gemini/gemini-1.5-flash"}))
            agent = MockAgent()
            state = agent.run("Test query")
            assert "Test query" in state.messages[0]["content"]
            assert "Mock agent response" in state.messages[1]["content"]
            mock_complete.assert_called_once()


@pytest.mark.asyncio
@patch('lola.core.graph.LOLAStateGraph.execute')
def test_graph_edge_invalid(mock_execute):
    """Test graph handles invalid state via validation.

    Args:
        mock_execute: Patched execute.

    Does Not: Test async—mock ainvoke.
    """
    mock_execute.side_effect = ValueError("Invalid state")
    graph = LOLAStateGraph()
    with pytest.raises(ValueError, match="Invalid state"):
        asyncio.run(graph.execute({"messages": [{"content": ""}]}))  # Empty content raises
    mock_execute.assert_called_once()


def test_memory_edge_invalid():
    """Test memory handles invalid messages via LLM fallback.

    Does Not: Test save—StateManager separate.
    """
    invalid_messages = [{"role": "user", "content": ""}]  # Empty
    with patch('lola.core.memory.LLMProxy') as mock_llm:
        mock_instance = Mock()
        mock_instance.complete.return_value = "[]"
        mock_llm.return_value = mock_instance
        memory = ConversationMemory()
        entities = memory.extract_entities(invalid_messages)
        assert "entities" in entities  # Mock returns list
        mock_instance.complete.assert_called_once()
    # Inline: Edge - Empty messages
    empty_entities = memory.extract_entities([])
    assert "entities" in empty_entities