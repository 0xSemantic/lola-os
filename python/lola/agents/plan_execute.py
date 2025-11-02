# python/lola/agents/plan_execute.py
# Standard imports
import asyncio
import json
from typing import Dict, Any, List 

# Third-party imports
from langgraph.graph import StateGraph, START, END

# Local imports
from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.graph import LOLAStateGraph
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.base import BaseTool
from lola.core.agent import BaseAgent 

"""
File: Plan-Execute agent template for LOLA OS with planning + graph execution.

Purpose: Implements Plan-Execute pattern: LLM plan steps, then execute via graph/tools for structured tasks.
How: Extends BaseAgent with run: LLM plan → build graph nodes/edges → execute graph with tools/memory.
Why: Supports complex tasks in V1 (e.g., "plan trip + book flight" → plan steps + execute), verifiable via state/graph.
Full Path: lola-os/python/lola/agents/plan_execute.py
"""

logger = setup_logger("lola.agents.plan_execute")

class PlanExecuteAgent(BaseAgent):
    """PlanExecuteAgent: Plan-Execute template with LLM plan + graph execute. Does NOT auto-bind—call bind_tools."""

    def __init__(self, model: str = None, tools: List[BaseTool] = None):
        """
        Init PlanExecuteAgent with model/tools.

        Args:
            model: LLM model (default config).
            tools: List of BaseTool for execute.

        Does Not: Build graph—per run.
        """
        super().__init__(model, tools)
        self.memory = ConversationMemory(self.llm_proxy)

    def run(self, query: str) -> State:
        """
        Runs Plan-Execute: LLM plan steps → build/execute graph → memory summary.

        Args:
            query: User query (e.g., "Plan and book trip to NY").

        Returns:
            State with plan/messages/tool_results/summary.

        Does Not: Limit steps—LLM plans.
        """
        state = State(messages=[{"role": "user", "content": query}])
        # Plan with LLM
        plan_prompt = f"Plan steps for: {query}\nTools: {', '.join(t.name for t in self.tools)}\nOutput numbered steps."
        plan = self.call_llm(plan_prompt)
        state.messages.append({"role": "assistant", "content": f"Plan: {plan}"})
        steps = self._parse_plan(plan)
        logger.info("Plan generated", extra={"steps_count": len(steps)})
        # Build/execute graph
        graph = self._build_plan_graph(steps)
        if not steps:
            state.tool_results["summary"] = "No plan generated."
            return state
        final_state_dict = asyncio.run(graph.execute(state.model_dump()))
        final_state = State(**final_state_dict)
        # Memory summary
        final_state.tool_results["summary"] = self.memory.summarize_history(final_state.messages)
        logger.info("Plan-Execute run", extra={"plan_len": len(plan), "tools_used": len(final_state.tool_results) - 1})
        return final_state

    def _parse_plan(self, plan: str) -> List[str]:
        """Parses LLM plan into list of steps."""
        return [s.strip() for s in plan.split("\n") if s.strip().startswith(tuple('1234567890.'))]

    def _build_plan_graph(self, steps: List[str]) -> LOLAStateGraph:
        """Builds graph from plan steps (one node per step)."""
        graph = LOLAStateGraph()
        prev_node = START
        for i, step in enumerate(steps):
            def step_func(state: Dict, i=i, step=step):
                prompt = f"Execute step {i+1}: {step}\nUse tools if needed."
                result = self.call_llm(prompt)
                return {"messages": [{"role": "assistant", "content": f"Step {i+1}: {result}"}]}
            node_name = f"step_{i}"
            graph.add_node(node_name, step_func)
            graph.add_edge(prev_node, node_name)
            prev_node = node_name
        graph.add_edge(prev_node, END)
        logger.debug("Plan graph built", extra={"nodes": len(steps)})
        return graph

__all__ = ["PlanExecuteAgent"]