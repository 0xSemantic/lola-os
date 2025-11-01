# python/lola/agents/react.py
# Standard imports
import typing as tp

# Third-party imports
# None

# Local imports
from lola.core.state import State
from lola.core.graph import StateGraph
from lola.core.agent import BaseAgent

"""
File: ReAct agent template for reasoning-action loops.

Purpose: Implements a ReAct (Reason-Act) pattern for iterative problem-solving.
How: Uses a StateGraph with nodes for reasoning (stubbed LLM), acting (stubbed tools), and reflection.
Why: Enables complex task resolution with supervision in V1.
Full Path: lola-os/python/lola/agents/react.py
"""

class ReActAgent(BaseAgent):
    """ReActAgent: Executes iterative reason-act loops. Does NOT call real LLMs/tools."""

    def __init__(
        self,
        model: str = "mock-model",
        tools: tp.List[tp.Any] = None,
        graph: tp.Optional[StateGraph] = None
    ):
        """
        Initializes ReAct agent with reasoning loop.

        Args:
            model: LLM model name (stubbed).
            tools: List of tools (stubbed or real).
            graph: StateGraph (defaults to ReAct-specific).

        Does Not: Connect to external APIs.
        """
        super().__init__(model, tools, graph)
        # Inline: Build ReAct graph if none provided
        if not graph:
            self.graph = self._build_react_graph()
        self.max_iterations = 10  # Default to high for normal runs

    def _build_react_graph(self) -> StateGraph:
        """
        Builds the ReAct workflow graph.

        Returns:
            StateGraph with reason-act-reflect nodes.

        Does Not: Execute the graph (run-time only).
        """
        graph = StateGraph(State)

        def reason(state: State) -> State:
            prompt = f"Reason about: {state.messages[-1]['content']}"
            state.messages.append({"role": "system", "content": self.call_llm(prompt)})
            return state

        def act(state: State) -> State:
            # Inline: Simulate tool call if tools exist
            if self.tools:
                state.tools_results["mock_tool"] = "Mock tool executed"
            state.messages.append({"role": "system", "content": "Action taken"})
            return state

        def should_continue(state: State) -> str:
            # Inline: Stop after max iterations or if resolved
            if len(state.messages) >= self.max_iterations * 2 + 1:  # Query + (reason + act) * max_iterations
                state.reflection = "Max turns reached; halting execution to prevent loops."
                return "__end__"
            return "act"

        graph.add_node("reason", reason)
        graph.add_node("act", act)
        graph.set_entry_point("reason")
        graph.add_edge("reason", "act")
        graph.add_conditional_edges("act", should_continue, {"act": "reason", "__end__": "__end__"})
        return graph

    async def run(self, query: str) -> State:
        """
        Executes the ReAct loop for a query.

        Args:
            query: User input or task.

        Returns:
            Final State after loop.

        Does Not: Use real LLMs/tools.
        """
        # Inline: Initialize state with query
        self.state = State(messages=[{"role": "user", "content": query}])
        # Inline: Run graph with supervision
        final_state = await self.graph.execute(self.state)
        return final_state

__all__ = ["ReActAgent"]