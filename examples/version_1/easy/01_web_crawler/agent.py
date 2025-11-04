from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.tools.web_crawl import WebCrawlTool
from lola.core.agent import BaseAgent

"""
File: Simple web crawler agent.
Purpose: Crawls a website and returns content.
How: Extends BaseAgent with WebCrawlTool, uses Gemini LLM.
Why: Introduces beginners to web crawling in LOLA OS v1.
Full Path: lola-os/examples/version_1/easy/01_web_crawler/agent.py
"""

logger = setup_logger("web_crawler")

class Agent(BaseAgent):
    """Simple web crawler agent. Binds WebCrawlTool for basic web scraping."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize web crawler agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.tool = WebCrawlTool()
        logger.info("Web crawler agent initialized", extra={"model": model})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run agent to crawl website and return content.

        Args:
            query: User query string (e.g., "Crawl https://example.com").
            history: Optional prior messages for context (unused here).

        Returns:
            State with messages and tool results.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            result = self.tool.execute(url=query.split(" ")[1])  # Extract URL from query
            state.messages.append({"role": "assistant", "content": result})
            state.tool_results["web_crawl"] = result
            logger.info("Web crawl completed", extra={"url": query.split(" ")[1]})
        except Exception as e:
            error_msg = f"Error crawling: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Web crawl failed", extra={"error": str(e)})
        return state

__all__ = ["Agent"]