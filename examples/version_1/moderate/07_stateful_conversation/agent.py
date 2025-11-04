import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.web_crawl import WebCrawlTool
from lola.agents.conversational import ConversationalAgent

"""
File: Stateful conversational agent.
Purpose: Maintains conversation state with web tool support.
How: Extends ConversationalAgent with WebCrawlTool and ConversationMemory, uses Gemini LLM.
Why: Demonstrates stateful conversations for moderate users in LOLA OS v1.
Full Path: lola-os/examples/version_1/moderate/07_stateful_conversation/agent.py
"""

logger = setup_logger("stateful_conversation")

class Agent(ConversationalAgent):
    """Stateful conversational agent with web crawling capabilities."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.memory = ConversationMemory(LLMProxy(model))
        self.tools = [WebCrawlTool()]
        logger.info("Stateful conversational agent initialized", extra={"model": model, "tools": [t.name for t in self.tools]})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run stateful conversational agent with web tool support.

        Args:
            query: User query string (e.g., "Crawl https://example.com and summarize it").
            history: Optional prior messages for context.

        Returns:
            State with messages, tool results, and summary.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            prompt = self._build_prompt(state)
            response = self.call_llm(prompt)
            state.messages.append({"role": "assistant", "content": response})
            action = self._parse_action(response)
            if action["action"] != "finish":
                tool_result = self._execute_tool(action)
                state.messages.append({"role": "tool", "content": tool_result})
                state.tool_results[action["tool"]] = tool_result
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
            logger.info("Conversational turn completed", extra={"query": query})
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Conversational failed", extra={"error": str(e)})
        return state

    def _build_prompt(self, state: State) -> str:
        """Build prompt for stateful conversation with web tool."""
        history = self.memory.summarize_history(state.messages)
        tools = ", ".join([t.name for t in self.tools])
        return f"History: {history}\nQuery: {state.messages[-1]['content']}\nTools: {tools}\nRespond with JSON: {{'thought': 'reasoning', 'action': 'web_crawl or finish', 'input': {{'url': 'site', 'selectors': ['.content']}} or 'output'}}"

    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for action and tool input."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON response", extra={"response": response})
            return {"action": "finish", "output": "Invalid response format"}

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """Execute web crawl tool if needed."""
        try:
            if action["action"] == "web_crawl":
                tool = WebCrawlTool()
                return tool.execute(**action["input"])
            return "No action executed"
        except Exception as e:
            logger.error("Tool execution failed", extra={"action": action["action"], "error": str(e)})
            return f"Error: {str(e)}"

__all__ = ["Agent"]