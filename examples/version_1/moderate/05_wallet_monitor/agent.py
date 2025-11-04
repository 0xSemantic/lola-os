import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.chains.wallet import Wallet
from lola.agents.react import ReActAgent

"""
File: Wallet monitor agent.
Purpose: Monitors wallet balance and alerts on changes.
How: Extends ReActAgent with LOLAWallet, uses Gemini LLM.
Why: Demonstrates wallet monitoring for moderate users in LOLA OS v1.
Full Path: lola-os/examples/version_1/moderate/05_wallet_monitor/agent.py
"""

logger = setup_logger("wallet_monitor")

class Agent(ReActAgent):
    """Wallet monitor agent for checking and alerting on balance changes."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        self.wallet = Wallet()
        self.last_balance = None
        logger.info("Wallet monitor agent initialized", extra={"model": model})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run ReAct loop to check wallet balance and alert on changes.

        Args:
            query: User query string (e.g., "Monitor balance for 0x... on Sepolia").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        max_turns = 2  # Check balance and compare
        for turn in range(max_turns):
            prompt = self._build_prompt(state)
            response = self.call_llm(prompt)
            state.messages.append({"role": "assistant", "content": response})
            action = self._parse_action(response)
            if action["action"] == "finish":
                break
            tool_result = self._execute_tool(action)
            state.messages.append({"role": "tool", "content": tool_result})
            state.tool_results[action["tool"]] = tool_result
            logger.info("ReAct turn completed", extra={"turn": turn + 1, "action": action["action"]})
        state.tool_results["summary"] = self.memory.summarize_history(state.messages)
        return state

    def _build_prompt(self, state: State) -> str:
        """Build prompt for wallet monitoring."""
        history = self.memory.summarize_history(state.messages)
        last_balance = f"Last balance: {self.last_balance}" if self.last_balance else "No prior balance"
        return f"History: {history}\n{last_balance}\nQuery: {state.messages[-1]['content']}\nTools: Wallet\nRespond with JSON: {{'thought': 'reasoning', 'action': 'check_balance or finish', 'input': {{'address': '0x...', 'chain': 'sepolia'}} or 'output'}}"

    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for action and tool input."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON response", extra={"response": response})
            return {"action": "finish", "output": "Invalid response format"}

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """Execute wallet balance check and compare."""
        try:
            if action["action"] == "check_balance":
                balance = self.wallet.get_balance(**action["input"])
                result = str(balance)
                if self.last_balance is not None and balance != self.last_balance:
                    result += f" (changed from {self.last_balance})"
                self.last_balance = balance
                return result
            return "No action executed"
        except Exception as e:
            logger.error("Tool execution failed", extra={"action": action["action"], "error": str(e)})
            return f"Error: {str(e)}"

__all__ = ["Agent"]