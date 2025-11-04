import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.onchain.utils import simulate_call
from lola.agents.react import ReActAgent

"""
File: Contract simulator agent.
Purpose: Simulates EVM contract calls for testing.
How: Extends ReActAgent with simulate_call utility, uses Gemini LLM.
Why: Demonstrates contract simulation for moderate users in LOLA OS v1.
Full Path: lola-os/examples/version_1/moderate/08_contract_simulator/agent.py
"""

logger = setup_logger("contract_simulator")

class Agent(ReActAgent):
    """Agent for simulating EVM contract calls using ReAct loop."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        logger.info("Contract simulator agent initialized", extra={"model": model})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run ReAct loop to simulate contract calls.

        Args:
            query: User query string (e.g., "Simulate balanceOf 0x... on Sepolia").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        max_turns = 2  # Simulate and report
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
        """Build prompt for contract simulation."""
        history = self.memory.summarize_history(state.messages)
        return f"History: {history}\nQuery: {state.messages[-1]['content']}\nTools: simulate_call\nRespond with JSON: {{'thought': 'reasoning', 'action': 'simulate_call or finish', 'input': {{'contract_address': '0x...', 'function_name': 'balanceOf', 'chain': 'sepolia'}} or 'output'}}"

    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for action and tool input."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON response", extra={"response": response})
            return {"action": "finish", "output": "Invalid response format"}

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """Execute contract simulation."""
        try:
            if action["action"] == "simulate_call":
                return str(simulate_call(**action["input"]))
            return "No action executed"
        except Exception as e:
            logger.error("Tool execution failed", extra={"action": action["action"], "error": str(e)})
            return f"Error: {str(e)}"

__all__ = ["Agent"]