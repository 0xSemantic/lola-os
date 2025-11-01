# Standard imports
import abc
import typing as tp

# Third-party imports
# None (LLM calls stubbed for Phase 1)

# Local imports
from .state import State
from .graph import StateGraph

"""
File: Defines the abstract BaseAgent for LOLA OS agents.

Purpose: Provides a standardized interface for agent templates to initialize and run workflows.
How: Initializes with model/tools/graph/state, stubs LLM calls, and requires subclasses to implement run.
Why: Enables developer-extensible agents in V1 with consistent orchestration, avoiding vendor lock-in.
Full Path: lola-os/python/lola/core/agent.py
"""

class BaseAgent(abc.ABC):
    """BaseAgent: Abstract base class for all LOLA agents. Does NOT handle tool execution or LLM integration."""

    def __init__(self, model: str, tools: tp.List[tp.Any] = None, graph: tp.Optional[StateGraph] = None):
        """
        Initializes the agent with model, tools, and optional graph.

        Args:
            model: LLM model identifier (e.g., 'gpt-4o'; stubbed in V1).
            tools: List of tools to bind (optional).
            graph: Optional StateGraph for workflow (creates default if None).

        Does Not: Validate model or tools; defer to runtime.
        """
        self.model = model
        self.tools = tools or []
        self.graph = graph or StateGraph()
        # Inline: Start with empty validated state
        self.state = State()

    def call_llm(self, prompt: str) -> str:
        """
        Stubs an LLM call for reasoning (full implementation in Phase 5).

        Args:
            prompt: Input prompt string.

        Returns:
            Stubbed response string for testing.

        Does Not: Make real API calls; use for simulation only.
        """
        # Inline: Return deterministic stub to enable reliable testing
        return f"Stub LLM response for prompt: {prompt[:50]}..."  # Truncate for brevity

    @abc.abstractmethod
    def run(self, query: str) -> State:
        """
        Abstract method to run the agent's workflow.

        Args:
            query: User input query string.

        Returns:
            Updated State after execution.

        Does Not: Define specific logic; must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement run method.")

    def bind_tools(self, tools: tp.List[tp.Any]) -> None:
        """
        Binds additional tools to the agent.

        Args:
            tools: List of tools to add.

        Does Not: Validate or duplicate-check tools; append only.
        """
        self.tools.extend(tools)

__all__ = ["BaseAgent"]