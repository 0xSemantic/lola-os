import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.chains.wallet import LOLAWallet
from lola.tools.onchain.contract_call import ContractCallTool
from lola.agents.plan_execute import PlanExecuteAgent
from lola.libs.langgraph.adapter import SupervisedStateGraph

"""
File: Wallet analytics agent.
Purpose: Analyzes wallet balance and contract interactions.
How: Uses PlanExecuteAgent with Wallet and ContractCallTool for analytics.
Why: Demonstrates advanced wallet analytics in LOLA OS v1.
Full Path: lola-os/examples/version_1/advanced/03_wallet_analytics/agent.py
"""

logger = setup_logger("wallet_analytics")

class Agent(PlanExecuteAgent):
    """Agent for analyzing wallet balance and contract interactions."""

    def __init__(self, model: str = "gemini/gemini-1.5-pro"):
        """
        Initialize agent with LLM model and state graph.

        Args:
            model: LLM model string (default: Gemini Pro for advanced tasks).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        self.tools = [ContractCallTool()]
        self.wallet = LOLAWallet()
        self.graph = SupervisedStateGraph()
        self.graph.add_node("plan", self._plan)
        self.graph.add_node("analyze", self._analyze)
        self.graph.set_entry_point("plan")
        self.graph.add_edge("plan", "analyze")
        logger.info("Wallet analytics agent initialized", extra={"model": model, "tools": [t.name for t in self.tools]})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run planned workflow for wallet analytics.

        Args:
            query: User query string (e.g., "Analyze balance and token holdings for 0x... on Sepolia").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            state = self.graph.invoke(state)
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
            logger.info("Wallet analytics completed", extra={"query": query})
        except Exception as e:
            error_msg = f"Error in wallet analytics: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Wallet analytics failed", extra={"error": str(e)})
        return state

    def _plan(self, state: State) -> State:
        """Plan wallet analytics steps."""
        prompt = self._build_prompt(state, "plan")
        response = self.call_llm(prompt)
        state.messages.append({"role": "assistant", "content": response})
        state.tool_results["plan"] = response
        return state

    def _analyze(self, state: State) -> State:
        """Analyze wallet balance and contract interactions."""
        action = self._parse_action(state.messages[-1]["content"])
        if action["action"] == "check_balance":
            result = self.wallet.get_balance(**action["input"])
            state.messages.append({"role": "tool", "content": str(result)})
            state.tool_results["balance"] = result
        elif action["action"] == "contract_call":
            tool_result = self._execute_tool(action)
            state.messages.append({"role": "tool", "content": tool_result})
            state.tool_results["contract_call"] = tool_result
        return state

    def _build_prompt(self, state: State, stage: str) -> str:
        """Build prompt for wallet analytics."""
        history = self.memory.summarize_history(state.messages)
        tools = ", ".join([t.name for t in self.tools] + ["check_balance"])
        return f"History: {history}\nStage: {stage}\nQuery: {state.messages[-1]['content']}\nTools: {tools}\nRespond with JSON: {{'thought': 'reasoning', 'action': 'check_balance or contract_call or finish', 'tool': 'tool_name', 'input': {{'address': '0x...', 'chain': 'sepolia'}} or {'contract_address': '0x...', 'function_name': 'balanceOf', 'chain': 'sepolia'} or 'output'}}"

    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for action and tool input."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON response", extra={"response": response})
            return {"action": "finish", "output": "Invalid response format"}

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """Execute selected tool."""
        try:
            for tool in self.tools:
                if tool.name == action["tool"]:
                    return tool.execute(**action["input"])
            return "No valid tool executed"
        except Exception as e:
            logger.error("Tool execution failed", extra={"tool": action["tool"], "error": str(e)})
            return f"Error: {str(e)}"

__all__ = ["Agent"]