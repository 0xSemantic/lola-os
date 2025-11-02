# Standard imports
from typing import Dict, str

# Third-party imports
# None

# Local imports
from lola.agents.plan_execute import PlanExecuteAgent
from lola.tools.web_crawl import WebCrawlTool
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Standalone example: PlanExecuteAgent with planning + execute.

Purpose: Demonstrates PlanExecuteAgent run with LLM plan, graph execute, and tool use.
How: Init agent, bind tool, run query, log/print plan/state.
Why: Onboarding to Phase 6—shows structured reasoning for V1.
Full Path: lola-os/examples/version_1/agents_standalone/agent.py
"""

if __name__ == "__main__":
    # Inline: Load config for model
    config = load_config()
    logger = setup_logger()
    agent = PlanExecuteAgent()
    agent.bind_tools([WebCrawlTool()])
    state = agent.run("Plan and research a trip to New York.")
    logger.info("Standalone PlanExecute", extra={"plan_len": len(state.messages[0]["content"]), "tools_used": len(state.tool_results)})
    print(f"Plan: {state.messages[0]['content'][:200]}...")
    print(f"Results: {state.tool_results}")