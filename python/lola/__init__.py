# Standard imports
# None

# Third-party imports
# None

# Local imports
from .utils.config import Config, load_config
from .utils.logging import setup_logger, JSONFormatter
from .tools.base import BaseTool
from .tools.web_crawl import WebCrawlTool
from .tools.onchain.contract_call import ContractCallTool
from .tools.onchain.transact import TransactTool
from .tools.onchain.utils import gas_helper
from .libs.langgraph.adapter import SupervisedStateGraph
from .libs.litellm.proxy import LLMProxy
from .libs.crawl4ai.crawler import LOLAWebCrawler
from .libs.web3.connection import Web3Connection
from .libs.web3.contract import LOLAContract
from .libs.web3.wallet import LOLAWallet
from .libs.web3.utils import gas_estimate, simulate_call
from .core.state import State
from .core.graph import LOLAStateGraph
from .core.memory import StateManager, ConversationMemory
from .core.agent import BaseAgent
from .chains.connection import Web3Connection as ChainConnection
from .chains.contract import LOLAContract as Contract
from .chains.wallet import LOLAWallet as Wallet
from .chains.key_manager import KeyManager
from .chains.utils import gas_estimate, simulate_call
from .agents.react import ReActAgent
from .agents.plan_execute import PlanExecuteAgent
from .agents.conversational import ConversationalAgent
from .cli.main import cli

"""
File: Top-level package init for LOLA OS.

Purpose: Exports all public interfaces from submodules for easy import.
How: Aggregates exports from utils, tools, libs, core, chains, agents, and cli.
Why: Simplifies user imports (e.g., from lola import BaseAgent, cli) and supports Sphinx autodoc.
Full Path: lola-os/python/lola/__init__.py
"""

__all__ = [
    # Utils
    "Config", "load_config", "setup_logger", "JSONFormatter",
    # Tools
    "BaseTool", "WebCrawlTool", "ContractCallTool", "TransactTool", "gas_helper",
    # Libs
    "SupervisedStateGraph", "LLMProxy", "LOLAWebCrawler", "Web3Connection", "LOLAContract", "LOLAWallet", "gas_estimate", "simulate_call",
    # Core
    "State", "LOLAStateGraph", "StateManager", "ConversationMemory", "BaseAgent",
    # Chains
    "ChainConnection", "Contract", "Wallet", "KeyManager", "gas_estimate", "simulate_call",
    # Agents
    "BaseAgent", "ReActAgent", "PlanExecuteAgent", "ConversationalAgent",
    # CLI
    "cli"
]