# Standard imports
from typing import Dict, str, Any

# Third-party imports
# None

# Local imports
from lola.tools.base import BaseTool
from lola.tools.web_crawl import WebCrawlTool
from lola.tools.onchain.contract_call import ContractCallTool
from lola.tools.onchain.transact import TransactTool
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Combined example: BaseTool + web_crawl + onchain call/transact.

Purpose: Demonstrates tools integration: Base validate/bind, web crawl, onchain read/write.
How: Init tools, validate/bind to mock agent, execute crawl/call/transact, log/print.
Why: Previews phase 5 full tools layer for V1 agents.
Full Path: lola-os/examples/version_1/tools_combined/agent.py
"""

class MockAgent:
    """Mock agent for bind demo. Does Not run—tools only."""

    def __init__(self):
        self.tools = []

if __name__ == "__main__":
    # Inline: Load config for RPCs/key
    config = load_config()
    logger = setup_logger()
    if not config.evm_rpcs or not config.evm_private_key:
        print("No RPCs/key; skip onchain.")
    # Init tools
    crawl_tool = WebCrawlTool()
    call_tool = ContractCallTool()
    transact_tool = TransactTool()
    # Validate/bind
    crawl_tool.bind_to_agent(MockAgent())
    call_tool.bind_to_agent(MockAgent())
    transact_tool.bind_to_agent(MockAgent())
    # Execute
    crawl_result = crawl_tool.execute(url="https://example.com")
    logger.info("Combined crawl", extra={"title": crawl_result["metadata"]["title"]})
    print(f"Crawl: {crawl_result['content'][:100]}...")
    if config.evm_private_key:
        call_result = call_tool.execute(address="0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238", abi='[{"name": "balanceOf", "inputs": [{"type": "address"}], "outputs": [{"type": "uint256"}]}]', function_name="balanceOf", *["0xuser"])
        print(f"Contract call: {call_result}")
        tx_result = transact_tool.execute(to="0xdeadbeef", value=0, chain="sepolia")
        print(f"Transact: {tx_result['tx_hash']}")
    else:
        print("Skip onchain—no key.")