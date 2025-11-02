# python/lola/agents/conversational.py
# Standard imports
from typing import Dict, Any, Optional, List

# Third-party imports
import json

# Local imports
from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.base import BaseTool
from lola.core.agent import BaseAgent  # Import from core (Phase 3), no duplication

"""
File: Conversational agent template for LOLA OS with memory context.

Purpose: Implements conversational agent for multi-turn chat with tools, maintaining context via memory.
How: Extends core BaseAgent with run: Memory summarize history → LLM respond with tool action if needed → update state/memory.
Why: Supports chat-like agents in V1 (e.g., "What's Alice's balance? Transfer 1 ETH."), verifiable via memory/state.
Full Path: lola-os/python/lola/agents/conversational.py
"""

logger = setup_logger("lola.agents.conversational")

class ConversationalAgent(BaseAgent):
    """ConversationalAgent: Memory-driven multi-turn agent. Does NOT use graph—linear with tools."""

    def __init__(self, model: str = None, tools: List[BaseTool] = None):
        """
        Init ConversationalAgent with model/tools/memory.

        Args:
            model: LLM model (default config).
            tools: List of BaseTool for action.

        Does Not: Auto-bind—call bind_tools.
        """
        super().__init__(model, tools)
        self.memory = ConversationMemory(self.llm_proxy)

    def run(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> State:
        """
        Runs conversational turn: Summarize history → LLM respond/act → update state/memory.

        Args:
            query: Current user query string.
            history: Optional prior messages for memory.

        Returns:
            State with response/tool_result/summary.

        Does Not: Persist memory—use StateManager in caller.
        """
        messages = history or []
        messages.append({"role": "user", "content": query})
        state = State(messages=messages)
        # Memory context
        summary = self.memory.summarize_history(state.messages)
        context_prompt = f"History summary: {summary}\nQuery: {query}\nRespond or act with tools."
        response = self.call_llm(context_prompt)
        # Parse for tool action
        action = self._parse_tool_action(response)
        if action:
            tool_name = action["tool"]
            tool_input = action["input"]
            tool = next((t for t in self.tools if t.name == tool_name), None)
            if tool:
                tool_result = tool.execute(**tool_input)
                response += f"\nTool result: {tool_result}"
                state.tool_results[tool_name] = tool_result
        state.messages.append({"role": "assistant", "content": response})
        state.tool_results["summary"] = self.memory.summarize_history(state.messages)
        logger.info("Conversational turn", extra={"history_len": len(state.messages) - 1, "tools_used": len(state.tool_results) - 1})
        return state

    def _parse_tool_action(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parses LLM response for tool action (simple keyword; subclass for LLM parse).

        Args:
            response: LLM response string.

        Returns:
            Dict {"tool": str, "input": Dict} or None.

        Does Not: Handle complex parse—basic for V1.
        """
        # Inline: Basic keyword parse; real: Use LLM for structured output
        for tool in self.tools:
            if tool.name.lower() in response.lower():
                return {"tool": tool.name, "input": {"url": "default" if tool.name == "web_crawl" else {}}}
        return None

__all__ = ["ConversationalAgent"]