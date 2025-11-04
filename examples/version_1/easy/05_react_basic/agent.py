import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.tools.web_crawl import WebCrawlTool
from lola.agents.react import ReActAgent

"""
File: Basic ReAct agent for web crawling.
Purpose: Uses ReAct loop to crawl a website with reasoning.
How: Extends ReActAgent with WebCrawlTool, uses Gemini LLM.
Why: Introduces beginners to ReAct logic in LOLA OS v1.
Full Path: lola-os/examples/version_1/easy/05_react_basic/agent.py
"""

logger = setup_logger("react_basic")

class Agent(ReActAgent):
    """Basic ReAct agent for web crawling. Binds WebCrawlTool."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize ReAct agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.tools = [WebCrawlTool()]
        logger.info("ReAct agent initialized", extra={"model": model})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run ReAct loop to crawl website with reasoning.

        Args:
            query: User query string (e.g., "Crawl https://example.com").
            history: Optional prior messages for context.

        Returns:
            State with messages and tool results.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            prompt = f"Query: {query}\nTools: WebCrawlTool\nRespond with JSON: {{'thought': 'reasoning', 'action': 'web_crawl or finish', 'input': {{'url': 'site'}} or 'output'}}"
            response = self.call_llm(prompt)
            action = json.loads(response)
            if action["action"] == "web_crawl":
                tool = WebCrawlTool()
                result = tool.execute(**action["input"])
                state.messages.append({"role": "tool", "content": result})
                state.tool_results["web_crawl"] = result
                logger.info("Web crawl completed", extra={"url": action["input"]["url"]})
            else:
                state.messages.append({"role": "assistant", "content": action.get("output", "Done")})
        except Exception as e:
            error_msg = f"Error in ReAct loop: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("ReAct failed", extra={"error": str(e)})
        return state

__all__ = ["Agent"]