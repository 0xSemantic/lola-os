
import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.onchain.transact import TransactTool
from lola.tools.onchain.utils import gas_estimate
from lola.agents.plan_execute import PlanExecuteAgent
from lola.libs.langgraph.adapter import SupervisedStateGraph

"""
File: Gas-optimized workflow agent.
Purpose: Optimizes transactions with gas estimation and simulation.
How: Uses PlanExecuteAgent with SupervisedStateGraph for gas-aware transactions.
Why: Demonstrates advanced gas optimization in LOLA OS v1.
Full Path: lola-os/examples/version_1/advanced/06_gas_optimized_workflow/agent.py
"""

logger = setup_logger("gas_optimized_workflow")

class Agent(PlanExecuteAgent):
    """Agent for gas-optimized transactions with planning and simulation."""

    def __init__(self, model: str = "gemini/gemini-1.5-pro"):
        """
        Initialize agent with LLM model and state graph.

        Args:
            model: LLM model string (default: Gemini Pro for advanced tasks).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        self.tools = [TransactTool()]
        self.graph = SupervisedStateGraph()
        self.graph.add_node("plan", self._plan)
        self.graph.add_node("estimate", self._estimate)
        self.graph.add_node("execute", self._execute)
        self.graph.set_entry_point("plan")
        self.graph.add_edge("plan", "estimate")
        self.graph.add_conditional_edge("estimate", self._should_execute)
        logger.info("Gas-optimized workflow initialized", extra={"model": model, "tools": [t.name for t in self.tools]})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run gas-optimized transaction workflow.

        Args:
            query: User query string (e.g., "Send 0.1 ETH to 0x... on Sepolia with gas optimization").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            state = self.graph.invoke(state)
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
            logger.info("Gas-optimized workflow completed", extra={"query": query})
        except Exception as e:
            error_msg = f"Error in gas optimization: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Gas optimization failed", extra={"error": str(e)})
        return state

    def _plan(self, state: State) -> State:
        """Plan gas-optimized transaction steps."""
        prompt = self._build_prompt(state, "plan")
        response = self.call_llm(prompt)
        state.messages.append({"role": "assistant", "content": response})
        state.tool_results["plan"] = response
        return state

    def _estimate(self, state: State) -> State:
        """Estimate gas for transaction."""
        action = self._parse_action(state.messages[-1]["content"])
        if action["action"] == "gas_estimate":
            result = gas_estimate(**action["input"])
            state.messages.append({"role": "tool", "content": str(result)})
            state.tool_results["gas_estimate"] = result
        return state

    def _execute(self, state: State) -> State:
        """Execute transaction with optimized gas."""
        action = self._parse_action(state.messages[-1]["content"])
        if action["action"] == "transact":
            tool_result = self._execute_tool(action)
            state.messages.append({"role": "tool", "content": tool_result})
            state.tool_results["transact"] = tool_result
        return state

    def _should_execute(self, state: State) -> str:
        """Determine if transaction should proceed."""
        action = self._parse_action(state.messages[-1]["content"])
        return "execute" if action["action"] == "transact" else None

    def _build_prompt(self, state: State, stage: str) -> str:
        """Build prompt for gas-optimized workflow."""
        history = self.memory.summarize_history(state.messages)
        tools = ", ".join([t.name for t in self.tools] + ["gas_estimate"])
        return f"History: {history}\nStage: {stage}\nQuery: {state.messages[-1]['content']}\nTools: {tools}\nRespond with JSON: {{'thought': 'reasoning', 'action': 'gas_estimate or transact or finish', 'tool': 'tool_name', 'input': {{'to': '0x...', 'value': 0.1, 'chain': 'sepolia'}} or 'output'}}"

    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for action and tool input."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON response", extra={"response": response})
            return {"action": "finish", "output": "Invalid response format"}

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """Execute transaction tool."""
        try:
            for tool in self.tools:
                if tool.name == action["tool"]:
                    return tool.execute(**action["input"])
            return "No valid tool executed"
        except Exception as e:
            logger.error("Tool execution failed", extra={"tool": action["tool"], "error": str(e)})
            return f"Error: {str(e)}"

__all__ = ["Agent"]