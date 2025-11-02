# Standard imports
from typing import Optional, Any, Dict, List 
import json
from pathlib import Path 

# Third-party imports
from web3 import Web3

# Local imports
from lola.utils.logging import setup_logger
from .connection import Web3Connection

"""
File: EVM contract abstraction for LOLA with ABI load and read calls.

Purpose: Loads ABIs and performs read-only contract calls for V1 agents/tools.
How: Uses Web3Connection, loads ABI from file/string, calls functions with real testnet, logs results.
Why: Simplifies EVM reads (e.g., balance/events) in V1, no lock-in (config ABI path).
Full Path: lola-os/python/lola/chains/contract.py
"""

logger = setup_logger("lola.chains.contract")

class LOLAContract:
    """LOLAContract: Abstraction for EVM contracts with ABI load/call. Does NOT handle writes—use transact.py."""

    def __init__(self, address: str, abi: Optional[Any] = None, connection: Optional[Web3Connection] = None):
        """
        Initialize LOLAContract with address, ABI, and connection.

        Args:
            address: Contract address (e.g., "0x...").
            abi: ABI as list/dict or file path (str, .json).
            connection: Web3Connection (default first chain).

        Does Not: Deploy contracts—existing only.
        """
        self.connection = connection or Web3Connection()
        self.address = address
        self.abi = self._load_abi(abi)
        self.contract = self.connection.w3.eth.contract(address=self.address, abi=self.abi)
        logger.info("LOLAContract init", extra={"address": self.address, "functions": len(self.abi)})

    def _load_abi(self, abi: Optional[Any]) -> List[Dict]:
        """
        Loads ABI from file/string, validates as list of dicts.

        Args:
            abi: ABI data or path.

        Returns:
            ABI list.

        Does Not: Fetch from EVM—local only.
        """
        if isinstance(abi, str):
            if Path(abi).exists():
                with open(abi, "r") as f:
                    abi_data = json.load(f)
                abi = abi_data.get("abi", abi_data) if isinstance(abi_data, dict) else abi_data
            else:
                # Assume str is ABI JSON
                abi = json.loads(abi)
        if not isinstance(abi, list) or not abi or not isinstance(abi[0], dict):
            raise ValueError("Invalid ABI: must be list of dicts.")
        logger.debug("ABI loaded", extra={"len": len(abi)})
        return abi

    def call(self, function_name: str, *args, **kwargs) -> Any:
        """
        Calls contract function (read-only, view/pure).

        Args:
            function_name: Function name (e.g., "balanceOf").
            *args, **kwargs: Function params (e.g., address).

        Returns:
            Call result (e.g., int for balance).

        Does Not: Estimate gas—use utils/gas_estimate for writes.
        """
        if not hasattr(self.contract.functions, function_name):
            raise ValueError(f"Function {function_name} not in ABI.")
        func = getattr(self.contract.functions, function_name)
        result = func(*args, **kwargs).call()
        logger.debug("Contract call", extra={"function": function_name, "result_type": type(result).__name__})
        return result

__all__ = ["LOLAContract"]