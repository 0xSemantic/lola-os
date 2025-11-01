# Standard imports
import typing as tp

# Third-party imports
# None

# Local imports
from lola.core.state import State
from lola.core.graph import StateGraph
from lola.core.agent import BaseAgent

"""
File: Plan-Execute agent template for structured task execution.

Purpose: Plans steps then executes them in sequence.
How: Uses a StateGraph with planning (stub LLM) and execution nodes.
Why: Enables deliberate task breakdown for complex workflows in V1.
Full Path: lola-os/python/lola/agents/plan_execute.py
"""

class PlanExecuteAgent(BaseAgent):
    """PlanExecuteAgent: Plans and executes tasks sequentially. Does NOT call real LLMs/tools."""

    def __init__(
        self,
        model: str = "mock-model",
        tools: tp.List[tp.Any] = None,
        graph: tp.Optional[StateGraph] = None
    ):
        """
        Initializes Plan-Execute agent.

        Args:
            model: LLM model name (stubbed).
            tools: List of tools (stubbed or real).
            graph: StateGraph (defaults to Plan-Execute-specific).

        Does Not: Connect to external APIs.
        """
        super().__init__(model, tools, graph)
        # Inline: Build Plan-Execute graph if none provided
        if not graph:
            self.graph = self._build_plan_execute_graph()

    def _build_plan_execute_graph(self) -> StateGraph:
        """
        Builds the Plan-Execute workflow graph.

        Returns:
            StateGraph with plan and execute nodes.

        Does Not: Execute the graph.
        """
        graph = StateGraph(State)

        def plan(state: State) -> State:
            prompt = f"Plan steps for: {state.messages[-1]['content']}"
            state.messages.append({"role": "system", "content": self.call_llm(prompt)})
            return state

        def execute(state: State) -> State:
            state.messages.append({"role": "system", "content": "Executing plan"})
            if self.tools:
                state.tools_results["mock_tool"] = "Mock plan executed"
            return state

        graph.add_node("plan", plan)
        graph.add_node("execute", execute)
        graph.set_entry_point("plan")
        graph.add_edge("plan", "execute")
        graph.add_edge("execute", "__end__")
        return graph

    async def run(self, query: str) -> State:
        """
        Executes the Plan-Execute workflow.

        Args:
            query: User input or task.

        Returns:
            Final State after execution.

        Does Not: Use real LLMs/tools.
        """
        # Inline: Initialize state with query
        self.state = State(messages=[{"role": "user", "content": query}])
        # Inline: Run graph with supervision
        final_state = await self.graph.execute(self.state)
        return final_state

__all__ = ["PlanExecuteAgent"]