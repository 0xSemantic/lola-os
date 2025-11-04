# Standard imports
from typing import List, Dict, Any, Optional

# Third-party imports
import json

# Local imports
from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.core.memory import ConversationMemory
from lola.libs.litellm.proxy import LLMProxy
from lola.tools.base import BaseTool
from lola.tools.web_crawl import WebCrawlTool  # Example tool
from lola.core.agent import BaseAgent 

"""
File: Market-ready template for a Conversational agent in LOLA OS.

Purpose: Provides a robust multi-turn agent with memory context, tool actions, error handling, and logging.
How: Extends BaseAgent: Summarizes history, LLM generates response/action, parses/executes tools if needed, updates memory/state.
Why: Enables persistent chat agents for V1, like customer support or interactive on-chain bots, with verifiable history.
Full Path: lola-os/templates/conversational/agent.py
"""

logger = setup_logger("conversational_agent")

class Agent(BaseAgent):
    """ConversationalAgent template: Multi-turn with memory and tools. Bind tools for market-ready use."""

    def __init__(self, model: str = None, tools: List[BaseTool] = None):
        """
        Initialize Conversational agent with model and tools.

        Args:
            model: LLM model (default from config).
            tools: List of tools (default: web_crawl example).

        Does Not: Load history—pass to run().
        """
        super().__init__(model, tools or [WebCrawlTool()])
        self.memory = ConversationMemory(self.llm_proxy)
        logger.info("ConversationalAgent initialized", extra={"tools": [t.name for t in self.tools]})

    def run(self, query: str, history: Optional[List[Dict[str, Any]]] = None) -> State:
        """
        Process conversational turn: Summarize history → LLM respond/act → execute tool if needed → update state/memory.

        Args:
            query: Current user query.
            history: Prior messages (list of dicts; default empty).

        Returns:
            Updated State with response, tool_results, summary.

        Does Not: Persist across sessions—caller manages history.
        """
        messages = history or []
        messages.append({"role": "user", "content": query})
        state = State(messages=messages)
        try:
            summary = self.memory.summarize_history(state.messages)
            prompt = self._build_prompt(query, summary)
            response = self.call_llm(prompt)
            state.messages.append({"role": "assistant", "content": response})
            action = self._parse_action(response)
            if action:
                tool_result = self._execute_tool(action)
                state.messages.append({"role": "tool", "content": tool_result})
                state.tool_results[action["tool"]] = tool_result
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
            logger.info("Conversational turn complete", extra={"history_len": len(messages), "tools_used": bool(action)})
        except Exception as e:
            logger.error("Conversational run error", extra={"error": str(e)})
            state.messages.append({"role": "error", "content": str(e)})
        return state

    def _build_prompt(self, query: str, summary: str) -> str:
        """Build prompt with summary, query, tools, and format."""
        tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
        return f"""Summary: {summary}
Query: {query}
Tools: {tools_desc}

Respond directly or use tool in JSON:
{{"response": "Your answer",
 "action": "tool_name" (optional),
 "input": {{tool inputs}} (if action)}}"""

    def _parse_action(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM JSON for action/input, handle invalid."""
        try:
            data = json.loads(response)
            return {"tool": data.get("action"), "input": data.get("input")} if data.get("action") else None
        except json.JSONDecodeError:
            logger.warning("Parse failed")
            return None

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """Execute tool with input, handle errors."""
        tool_name = action.get("tool")
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return "Tool not found"
        try:
            return tool.execute(**action.get("input", {}))
        except Exception as e:
            return f"Error: {str(e)}"

__all__ = ["Agent"]