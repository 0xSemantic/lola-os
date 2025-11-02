# Standard imports
from typing import Dict, str

# Third-party imports
# None

# Local imports
from lola.agents.conversational import ConversationalAgent
from lola.tools.web_crawl import WebCrawlTool
from lola.tools.onchain.contract_call import ContractCallTool
from lola.chains.wallet import LOLAWallet
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Combined example: ConversationalAgent with tools and EVM query.

Purpose: Demonstrates ConversationalAgent multi-turn with tools, memory, and onchain for chat-like EVM interaction.
How: Init agent, bind tools, run query, log/print state/summary.
Why: Previews Phase 6 full templates for V1—conversational onchain.
Full Path: lola-os/examples/version_1/agents_combined/agent.py
"""

if __name__ == "__main__":
    # Inline: Load config for model
    config = load_config()
    logger = setup_logger()
    agent = ConversationalAgent()
    agent.bind_tools([WebCrawlTool(), ContractCallTool()])
    history = [{"role": "user", "content": "What's my balance?"}]
    state = agent.run("Check balance on Sepolia and research gas prices.", history)
    logger.info("Combined conversational", extra={"turn_len": len(state.messages), "tools_used": len(state.tool_results)})
    print(f"Response: {state.messages[-1]['content']}")
    print(f"Tools: {state.tool_results}")
    print(f"Summary: {state.tool_results.get('summary', 'None')}")