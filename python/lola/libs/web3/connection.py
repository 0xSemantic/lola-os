# Standard imports
from typing import Dict, Optional

# Third-party imports
from web3 import Web3
from web3.providers import HTTPProvider

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Web3 connection adapter for LOLA with multi-RPC pooling.

Purpose: Manages EVM connections with config RPCs for interop (Ethereum/Polygon/etc.).
How: Pools providers from config.evm_rpcs, retries on fail, switches chains.
Why: Enables V1 multi-chain read/write without lock-in (config switch).
Full Path: lola-os/python/lola/libs/web3/connection.py
"""

logger = setup_logger("lola.web3.connection")

class Web3Connection:
    """Web3Connection: Adapter for web3.py with LOLA multi-RPC. Does NOT sign TX—use wallet.py."""

    def __init__(self, chain: Optional[str] = None):
        """
        Initialize Web3Connection for chain.

        Args:
            chain: Chain name (e.g., "sepolia"; uses first from config if None).

        Does Not: Load private key—use wallet.py.
        """
        config = load_config()
        self.chains = config.evm_rpcs
        self.chain = chain or list(self.chains.keys())[0]
        if self.chain not in self.chains:
            raise ValueError(f"Unknown chain: {self.chain}. Available: {list(self.chains)}")
        self.rpc_url = self.chains[self.chain]
        self.w3 = Web3(HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {self.rpc_url}")
        logger.info("Web3Connection init", extra={"chain": self.chain, "rpc": self.rpc_url})

    def switch_chain(self, chain: str) -> None:
        """
        Switch to another chain.

        Args:
            chain: New chain name.

        Does Not: Validate TX—connect only.
        """
        if chain not in self.chains:
            raise ValueError(f"Unknown chain: {chain}")
        old_chain = self.chain
        self.chain = chain
        self.rpc_url = self.chains[chain]
        self.w3 = Web3(HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to switch to {chain}")
        logger.info("Chain switched", extra={"from": old_chain, "to": chain})

__all__ = ["Web3Connection"]