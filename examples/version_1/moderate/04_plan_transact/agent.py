import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.onchain.transact import TransactTool
from lola.agents.plan_execute import PlanExecuteAgent

"""
File: Plan-execute transaction agent.
Purpose: Plans and executes EVM transactions with validation.
How: Extends PlanExecuteAgent with TransactTool, uses Gemini LLM.
Why: Demonstrates planning for transactions for moderate users in LOLA OS v1.
Full Path: lola-os/examples/version_1/moderate/04_plan_transact/agent.py
"""

logger = setup_logger("plan_transact")

class Agent(PlanExecuteAgent):
    """Plan-execute agent for sending EVM transactions with planning."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        self.tools = [TransactTool()]
        logger.info("Plan-transact agent initialized", extra={"model": model, "tools": [t.name for t in self.tools]})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run plan-execute loop to plan and send a transaction.

        Args:
            query: User query string (e.g., "Plan to send 0.1 ETH to 0x... on Sepolia").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        max_turns = 2  # Plan and execute
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
            logger.info("Plan-execute turn completed", extra={"turn": turn + 1, "action": action["action"]})
        state.tool_results["summary"] = self.memory.summarize_history(state.messages)
        return state

    def _build_prompt(self, state: State) -> str:
        """Build prompt for planning and executing transactions."""
        history = self.memory.summarize_history(state.messages)
        tools = ", ".join([t.name for t in self.tools])
        return f"History: {history}\nQuery: {state.messages[-1]['content']}\nTools: {tools}\nRespond with JSON: {{'plan': 'steps', 'action': 'transact or finish', 'input': {{'to': '0x...', 'value': 0.1, 'chain': 'sepolia'}} or 'output'}}"

    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for action and tool input."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON response", extra={"response": response})
            return {"action": "finish", "output": "Invalid response format"}

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """Execute transaction tool if needed."""
        try:
            if action["action"] == "transact":
                tool = TransactTool()
                return tool.execute(**action["input"])
            return "No action executed"
        except Exception as e:
            logger.error("Tool execution failed", extra={"action": action["action"], "error": str(e)})
            return f"Error: {str(e)}"

__all__ = ["Agent"]