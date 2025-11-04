import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.chains.wallet import Wallet
from lola.tools.onchain.transact import TransactTool
from lola.agents.react import ReActAgent
from lola.libs.langgraph.adapter import SupervisedStateGraph

"""
File: Monitor and act agent.
Purpose: Monitors wallet and triggers transactions based on conditions.
How: Uses ReActAgent with SupervisedStateGraph for monitoring and actions.
Why: Demonstrates advanced monitoring and action workflows in LOLA OS v1.
Full Path: lola-os/examples/version_1/advanced/08_monitor_and_act/agent.py
"""

logger = setup_logger("monitor_and_act")

class Agent(ReActAgent):
    """Agent for monitoring wallet and triggering transactions."""

    def __init__(self, model: str = "gemini/gemini-1.5-pro"):
        """
        Initialize agent with LLM model and state graph.

        Args:
            model: LLM model string (default: Gemini Pro for advanced tasks).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        self.wallet = Wallet()
        self.tools = [TransactTool()]
        self.graph = SupervisedStateGraph()
        self.graph.add_node("monitor", self._monitor)
        self.graph.add_node("reason", self._reason)
        self.graph.add_node("execute", self._execute)
        self.graph.set_entry_point("monitor")
        self.graph.add_edge("monitor", "reason")
        self.graph.add_conditional_edge("reason", self._should_execute)
        logger.info("Monitor and act agent initialized", extra={"model": model, "tools": [t.name for t in self.tools]})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run monitoring and action workflow.

        Args:
            query: User query string (e.g., "Monitor 0x... balance and send 0.1 ETH if balance > 1 ETH").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            state = self.graph.invoke(state)
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
            logger.info("Monitor and act workflow completed", extra={"query": query})
        except Exception as e:
            error_msg = f"Error in monitor and act: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Monitor and act failed", extra={"error": str(e)})
        return state

    def _monitor(self, state: State) -> State:
        """Monitor wallet balance."""
        action = self._parse_query(state.messages[-1]["content"])
        if action["action"] == "check_balance":
            result = self.wallet.get_balance(**action["input"])
            state.messages.append({"role": "tool", "content": str(result)})
            state.tool_results["balance"] = result
        return state

    def _reason(self, state: State) -> State:
        """Reason about transaction action."""
        prompt = self._build_prompt(state)
        response = self.call_llm(prompt)
        state.messages.append({"role": "assistant", "content": response})
        state.tool_results["reasoning"] = response
        return state

    def _execute(self, state: State) -> State:
        """Execute transaction if conditions met."""
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

    def _build_prompt(self, state: State) -> str:
        """Build prompt for monitoring and action."""
        history = self.memory.summarize_history(state.messages)
        tools = ", ".join([t.name for t in self.tools] + ["check_balance"])
        return f"History: {history}\nQuery: {state.messages[-1]['content']}\nTools: {tools}\nRespond with JSON: {{'thought': 'reasoning', 'action': 'transact or finish', 'tool': 'tool_name', 'input': {{'to': '0x...', 'value': 0.1, 'chain': 'sepolia'}} or 'output'}}"

    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for action and tool input."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON response", extra={"response": response})
            return {"action": "finish", "output": "Invalid response format"}

    def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse query for monitoring action."""
        return {"action": "check_balance", "input": {"address": query.split(" ")[1], "chain": "sepolia"}}

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