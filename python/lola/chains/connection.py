# Standard imports
from typing import Dict, Optional, List
from pathlib import Path
import requests 

# Third-party imports
from web3 import Web3
from web3.providers import HTTPProvider
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Web3 connection abstraction for LOLA with multi-RPC pooling and interop.

Purpose: Manages EVM connections across chains with config RPCs, retries, and switch for interoperability.
How: Pools providers from config.evm_rpcs, retries on fail with requests adapter, switches chains dynamically.
Why: Enables seamless multi-chain read/write in V1 agents/tools, no lock-in (config-driven RPCs).
Full Path: lola-os/python/lola/chains/connection.py
"""

logger = setup_logger("lola.chains.connection")

class Web3Connection:
    """Web3Connection: Abstraction for EVM connections with multi-RPC support. Does NOT sign TX—use wallet.py."""

    def __init__(self, chain: Optional[str] = None):
        """
        Initialize Web3Connection for chain, pooling RPCs from config.

        Args:
            chain: Chain name (e.g., "sepolia"; uses first from config if None).

        Does Not: Load private key—use wallet.py for signing.
        """
        config = load_config()
        self.chains = config.evm_rpcs
        if not self.chains:
            raise ValueError("No RPCs configured in config.evm_rpcs; add to yaml/.env.")
        self.chain = chain or list(self.chains.keys())[0]
        if self.chain not in self.chains:
            raise ValueError(f"Unknown chain: {self.chain}. Available: {list(self.chains)}")
        self.rpc_url = self.chains[self.chain]
        self.w3 = self._create_w3_with_retries(self.rpc_url)
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {self.rpc_url}; check config.")
        logger.info("Web3Connection init", extra={"chain": self.chain, "rpc": self.rpc_url[:50] + "..."})

    def _create_w3_with_retries(self, rpc_url: str) -> Web3:
        """Creates Web3 with retry session for RPC stability."""
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return Web3(HTTPProvider(rpc_url, session=session))

    def switch_chain(self, chain: str) -> None:
        """
        Switches to another chain from config.

        Args:
            chain: New chain name (must be in config.evm_rpcs).

        Does Not: Validate TX—connect only.
        """
        if chain not in self.chains:
            raise ValueError(f"Unknown chain: {chain}. Available: {list(self.chains)}")
        old_chain = self.chain
        self.chain = chain
        self.rpc_url = self.chains[chain]
        self.w3 = self._create_w3_with_retries(self.rpc_url)
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to switch to {chain}; check RPC.")
        logger.info("Chain switched", extra={"from": old_chain, "to": chain})

__all__ = ["Web3Connection"]