import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.web_crawl import WebCrawlTool
from lola.tools.onchain.transact import TransactTool
from lola.agents.react import ReActAgent
from lola.libs.langgraph.adapter import SupervisedStateGraph

"""
File: Web-blockchain integrator agent.
Purpose: Integrates web data with blockchain transactions.
How: Uses ReActAgent with SupervisedStateGraph for web and transaction workflows.
Why: Demonstrates advanced web-blockchain integration in LOLA OS v1.
Full Path: lola-os/examples/version_1/advanced/04_web_blockchain_integrator/agent.py
"""

logger = setup_logger("web_blockchain_integrator")

class Agent(ReActAgent):
    """Agent for integrating web data with blockchain transactions."""

    def __init__(self, model: str = "gemini/gemini-1.5-pro"):
        """
        Initialize agent with LLM model and state graph.

        Args:
            model: LLM model string (default: Gemini Pro for advanced tasks).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        self.tools = [WebCrawlTool(), TransactTool()]
        self.graph = SupervisedStateGraph()
        self.graph.add_node("reason", self._reason)
        self.graph.add_node("execute", self._execute)
        self.graph.set_entry_point("reason")
        self.graph.add_conditional_edge("reason", self._should_execute)
        logger.info("Web-blockchain integrator initialized", extra={"model": model, "tools": [t.name for t in self.tools]})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run integrated workflow for web and blockchain tasks.

        Args:
            query: User query string (e.g., "Crawl https://coingecko.com for ETH price and send 0.1 ETH to 0x... if price > $2000").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            state = self.graph.invoke(state)
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
            logger.info("Web-blockchain integration completed", extra={"query": query})
        except Exception as e:
            error_msg = f"Error in integration: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Integration failed", extra={"error": str(e)})
        return state

    def _reason(self, state: State) -> State:
        """Reason about web and blockchain actions."""
        prompt = self._build_prompt(state)
        response = self.call_llm(prompt)
        state.messages.append({"role": "assistant", "content": response})
        state.tool_results["reasoning"] = response
        return state

    def _execute(self, state: State) -> State:
        """Execute web or blockchain tool."""
        action = self._parse_action(state.messages[-1]["content"])
        if action["action"] != "finish":
            tool_result = self._execute_tool(action)
            state.messages.append({"role": "tool", "content": tool_result})
            state.tool_results[action["tool"]] = tool_result
        return state

    def _should_execute(self, state: State) -> str:
        """Determine if execution is needed."""
        action = self._parse_action(state.messages[-1]["content"])
        return "execute" if action["action"] != "finish" else None

    def _build_prompt(self, state: State) -> str:
        """Build prompt for web-blockchain integration."""
        history = self.memory.summarize_history(state.messages)
        tools = ", ".join([t.name for t in self.tools])
        return f"History: {history}\nQuery: {state.messages[-1]['content']}\nTools: {tools}\nRespond with JSON: {{'thought': 'reasoning', 'action': 'web_crawl or transact or finish', 'tool': 'tool_name', 'input': {{'url': 'site', 'selectors': ['.price']}} or {'to': '0x...', 'value': 0.1, 'chain': 'sepolia'} or 'output'}}"

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