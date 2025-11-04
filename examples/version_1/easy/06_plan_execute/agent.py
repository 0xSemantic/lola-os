import json
from typing import List, Dict, Any

from lola.utils.logging import setup_logger
from lola.core.state import State
from lola.tools.web_crawl import WebCrawlTool
from lola.agents.plan_execute import PlanExecuteAgent

"""
File: Basic plan-execute agent for web crawling.
Purpose: Plans and executes a web crawl task.
How: Extends PlanExecuteAgent with WebCrawlTool, uses Gemini LLM.
Why: Introduces beginners to planning workflows in LOLA OS v1.
Full Path: lola-os/examples/version_1/easy/06_plan_execute/agent.py
"""

logger = setup_logger("plan_execute")

class Agent(PlanExecuteAgent):
    """Basic plan-execute agent for web crawling. Binds WebCrawlTool."""

    def __init__(self, model: str = "gemini/gemini-1.5-flash"):
        """
        Initialize plan-execute agent with LLM model.

        Args:
            model: LLM model string (default: Gemini free tier).
        """
        super().__init__(model)
        self.tools = [WebCrawlTool()]
        logger.info("Plan-execute agent initialized", extra={"model": model})

    def run(self, query: str, history: List[Dict[str, Any]] = None) -> State:
        """
        Run plan-execute loop to crawl website with planning.

        Args:
            query: User query string (e.g., "Crawl https://example.com").
            history: Optional prior messages for context.

        Returns:
            State with messages and tool results.
        """
        state = State(messages=history or [])
        state.messages.append({"role": "user", "content": query})
        try:
            prompt = f"Plan to: {query}\nTools: WebCrawlTool\nRespond with JSON: {{'plan': 'steps', 'action': 'web_crawl or finish', 'input': {{'url': 'site'}} or 'output'}}"
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
            error_msg = f"Error in plan-execute: {str(e)}"
            state.messages.append({"role": "assistant", "content": error_msg})
            logger.error("Plan-execute failed", extra={"error": str(e)})
        return state

__all__ = ["Agent"]