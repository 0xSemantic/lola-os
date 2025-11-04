# Standard imports
import asyncio
from typing import List, Dict, Any

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
File: Market-ready template for a ReAct agent in LOLA OS.

Purpose: Provides a robust, extensible ReAct agent with LLM reasoning, tool execution, memory, error handling, and logging.
How: Extends BaseAgent with a supervised loop: LLM generates thought/action, parses structured output, executes tools, observes results; uses memory for context and limits turns to prevent infinite loops.
Why: Enables production-grade dynamic agents for V1, suitable for tasks like web research + on-chain actions, with verifiable traces.
Full Path: lola-os/templates/react/agent.py
"""

logger = setup_logger("react_agent")

class Agent(BaseAgent):
    """ReActAgent template: Robust reasoning-action loop with tools and memory. Bind tools for market-ready use."""

    def __init__(self, model: str = None, tools: List[BaseTool] = None, max_turns: int = 10):
        """
        Initialize ReAct agent with model, tools, and max turns.

        Args:
            model: LLM model (default from config).
            tools: List of tools (default: web_crawl example).
            max_turns: Max reasoning loops to prevent hangs (default 10).

        Does Not: Start loop—call run().
        """
        super().__init__(model, tools or [WebCrawlTool()])
        self.memory = ConversationMemory(self.llm_proxy)
        self.max_turns = max_turns
        logger.info("ReActAgent initialized", extra={"tools": [t.name for t in self.tools], "max_turns": max_turns})

    def run(self, query: str) -> State:
        """
        Execute ReAct loop: Thought → Action → Observation until resolution or max turns.

        Args:
            query: Initial user query.

        Returns:
            Final State with messages, tool_results, and summary.

        Does Not: Persist state—caller handles.
        """
        state = State(messages=[{"role": "user", "content": query}])
        try:
            for turn in range(self.max_turns):
                prompt = self._build_prompt(state)
                response = self.call_llm(prompt)
                state.messages.append({"role": "assistant", "content": response})
                action = self._parse_response(response)
                if action["action"] == "finish":
                    break
                tool_result = self._execute_tool(action)
                state.messages.append({"role": "observation", "content": tool_result})
                state.tool_results[action["tool"]] = tool_result
                logger.info("ReAct turn complete", extra={"turn": turn + 1, "action": action["action"]})
            state.tool_results["summary"] = self.memory.summarize_history(state.messages)
        except Exception as e:
            logger.error("ReAct run error", extra={"error": str(e)})
            state.messages.append({"role": "error", "content": str(e)})
        return state

    def _build_prompt(self, state: State) -> str:
        """Build structured prompt with history, tools, and format instructions."""
        history = self.memory.summarize_history(state.messages)
        tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
        return f"""History: {history}
Query: {state.messages[-1]['content']}
Tools: {tools_desc}

Respond in JSON:
{{"thought": "Your reasoning",
 "action": "tool_name or finish",
 "input": {{tool inputs}} or "final output if finish"}}"""

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response safely with error handling."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Parse failed, defaulting to finish")
            return {"action": "finish", "output": "Invalid response format"}

    def _execute_tool(self, action: Dict[str, Any]) -> str:
        """Execute tool with input, handle errors."""
        tool_name = action.get("tool")
        tool_input = action.get("input", {})
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return "Tool not found"
        try:
            return tool.execute(**tool_input)
        except Exception as e:
            return f"Tool error: {str(e)}"

__all__ = ["Agent"]