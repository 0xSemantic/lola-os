# Standard imports
import asyncio
import json
from typing import List, Dict, Any

# Third-party imports
from langgraph.graph import END

# Local imports
from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.graph import LOLAStateGraph
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.base import BaseTool
from lola.tools.web_crawl import WebCrawlTool  # Example tool
from lola.core.agent import BaseAgent 

"""
File: Market-ready template for a Plan-Execute agent in LOLA OS.

Purpose: Provides a robust Plan-Execute agent with LLM planning, dynamic graph building, tool execution, memory, and error handling.
How: Extends BaseAgent: LLM generates numbered plan, builds graph nodes (each calls LLM/tool), executes async; summarizes with memory.
Why: Suited for structured multi-step tasks in V1, like planning + acting on-chain, with verifiable graph traces.
Full Path: lola-os/templates/plan_execute/agent.py
"""

logger = setup_logger("plan_execute_agent")

class Agent(BaseAgent):
    """PlanExecuteAgent template: LLM plans steps, executes via graph. Bind tools for market-ready use."""

    def __init__(self, model: str = None, tools: List[BaseTool] = None):
        """
        Initialize Plan-Execute agent with model and tools.

        Args:
            model: LLM model (default from config).
            tools: List of tools (default: web_crawl example).

        Does Not: Build graph—done per run.
        """
        super().__init__(model, tools or [WebCrawlTool()])
        self.memory = ConversationMemory(self.llm_proxy)
        logger.info("PlanExecuteAgent initialized", extra={"tools": [t.name for t in self.tools]})

    def run(self, query: str) -> State:
        """
        Execute Plan-Execute: Plan steps → build/execute graph → summarize.

        Args:
            query: User query for planning.

        Returns:
            State with plan, executions, results, summary.

        Does Not: Handle empty plan—returns early.
        """
        state = State(messages=[{"role": "user", "content": query}])
        try:
            plan_prompt = self._build_plan_prompt(query)
            plan = self.call_llm(plan_prompt)
            state.messages.append({"role": "plan", "content": plan})
            steps = self._parse_plan(plan)
            logger.info("Plan generated", extra={"steps_count": len(steps)})
            if not steps:
                state.tool_results["summary"] = "No valid plan generated."
                return state
            graph = self._build_graph(steps)
            final_state_dict = asyncio.run(graph.execute(state.model_dump()))
            state = State(**final_state_dict)
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
        except Exception as e:
            logger.error("Plan-Execute error", extra={"error": str(e)})
            state.messages.append({"role": "error", "content": str(e)})
        return state

    def _build_plan_prompt(self, query: str) -> str:
        """Build prompt for LLM planning with tools."""
        tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
        return f"""Generate a numbered plan for: {query}
Tools available: {tools_desc}
Output: 1. Step one...
2. Step two..."""

    def _parse_plan(self, plan: str) -> List[str]:
        """Parse plan into steps, handle invalid formats."""
        try:
            return [s.strip() for s in plan.split("\n") if s.strip().startswith(tuple("1234567890."))]
        except:
            logger.warning("Plan parse failed")
            return []

    def _build_graph(self, steps: List[str]) -> LOLAStateGraph:
        """Dynamically build graph from steps with tool/LLM nodes."""
        graph = LOLAStateGraph()
        prev = "__start__"
        for i, step in enumerate(steps):
            node_name = f"step_{i}"
            graph.add_node(node_name, self._create_step_func(step))
            graph.add_edge(prev, node_name)
            prev = node_name
        graph.add_edge(prev, END)
        logger.debug("Graph built", extra={"nodes": len(steps)})
        return graph

    def _create_step_func(self, step: str) -> Callable[[Dict], Dict]:
        """Create callable for step: LLM execute with tools."""
        def step_func(state_dict: Dict) -> Dict:
            state = State(**state_dict)
            prompt = f"Execute: {step}\nState: {state.model_dump_json()}"
            response = self.call_llm(prompt)
            action = self._parse_action(response)
            if action["action"] == "tool":
                tool_result = self._execute_tool(action)
                response += f"\nResult: {tool_result}"
            return {"messages": state.messages + [{"role": "step", "content": response}]}
        return step_func

    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse response for potential tool action."""
        try:
            return json.loads(response) if "action" in response else {"action": "none"}
        except:
            return {"action": "none"}

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """Execute tool safely."""
        tool_name = action.get("tool")
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return "Tool not found"
        try:
            return tool.execute(**action.get("input", {}))
        except Exception as e:
            return f"Error: {str(e)}"

__all__ = ["Agent"]