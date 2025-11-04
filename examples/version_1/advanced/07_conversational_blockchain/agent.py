import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.onchain.contract_call import ContractCallTool
from lola.tools.onchain.transact import TransactTool
from lola.agents.conversational import ConversationalAgent
from lola.libs.langgraph.adapter import SupervisedStateGraph

"""
File: Conversational blockchain agent.
Purpose: Handles conversational blockchain tasks with state management.
How: Uses ConversationalAgent with SupervisedStateGraph for contract and transaction tasks.
Why: Demonstrates advanced conversational blockchain workflows in LOLA OS v1.
Full Path: lola-os/examples/version_1/advanced/07_conversational_blockchain/agent.py
"""

logger = setup_logger("conversational_blockchain")

class Agent(ConversationalAgent):
    """Conversational agent for blockchain tasks with state management."""

    def __init__(self, model: str = "gemini/gemini-1.5-pro"):
        """
        Initialize agent with LLM model and state graph.

        Args:
            model: LLM model string (default: Gemini Pro for advanced tasks).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        self.tools = [ContractCallTool(), TransactTool()]
        self.graph = SupervisedStateGraph()
        self.graph.add_node("converse", self._converse)
        self.graph.add_node("execute", self._execute)
        self.graph.set_entry_point("converse")
        self.graph.add_conditional_edge("converse", self._should_execute)
        logger.info("Conversational blockchain agent initialized", extra={"model": model, "tools": [t.name for t in self.tools]})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run conversational blockchain workflow.

        Args:
            query: User query string (e.g., "Check balanceOf 0x... and send 0.1 ETH if sufficient").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            state = self.graph.invoke(state)
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
            logger.info("Conversational blockchain workflow completed", extra={"query": query})
        except Exception as e:
            error_msg = f"Error in conversational blockchain: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Conversational blockchain failed", extra={"error": str(e)})
        return state

    def _converse(self, state: State) -> State:
        """Handle conversational blockchain tasks."""
        prompt = self._build_prompt(state)
        response = self.call_llm(prompt)
        state.messages.append({"role": "assistant", "content": response})
        state.tool_results["conversation"] = response
        return state

    def _execute(self, state: State) -> State:
        """Execute blockchain tool."""
        action = self._parse_action(state.messages[-1]["content"])
        if action["action"] != "finish":
            tool_result = self._execute_tool(action)
            state.messages.append({"role": "tool", "content": tool_result})
            state.tool_results[action["tool"]] = tool_result
        return state

    def _should_execute(self, state: State) -> str:
        """Determine if tool execution is needed."""
        action = self._parse_action(state.messages[-1]["content"])
        return "execute" if action["action"] != "finish" else None

    def _build_prompt(self, state: State) -> str:
        """Build prompt for conversational blockchain tasks."""
        history = self.memory.summarize_history(state.messages)
        tools = ", ".join([t.name for t in self.tools])
        return f"History: {history}\nQuery: {state.messages[-1]['content']}\nTools: {tools}\nRespond with JSON: {{'thought': 'reasoning', 'action': 'contract_call or transact or finish', 'tool': 'tool_name', 'input': {{'contract_address': '0x...', 'function_name': 'balanceOf', 'chain': 'sepolia'}} or {'to': '0x...', 'value': 0.1, 'chain': 'sepolia'} or 'output'}}"

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