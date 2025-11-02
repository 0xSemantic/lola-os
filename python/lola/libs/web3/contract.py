# Standard imports
from typing import Optional, Any
import json  # Inline: For ABI load

# Third-party imports
from web3 import Web3

# Local imports
from lola.utils.logging import setup_logger
from .connection import Web3Connection

"""
File: Web3 contract adapter for LOLA ABI calls.

Purpose: Loads ABIs and calls contract functions for read ops.
How: Uses Web3Connection, loads ABI from file/string, calls functions.
Why: Simplifies EVM reads in V1 tools/agents.
Full Path: lola-os/python/lola/libs/web3/contract.py
"""

logger = setup_logger("lola.web3.contract")

class LOLAContract:
    """LOLAContract: Web3 contract wrapper. Does NOT handle writes—use transact.py."""

    def __init__(self, address: str, abi: Optional[Any] = None, connection: Optional[Web3Connection] = None):
        """
        Initialize LOLAContract.

        Args:
            address: Contract address.
            abi: ABI list/dict (loads from file if str path).
            connection: Web3Connection (uses default if None).

        Does Not: Deploy contracts—existing only.
        """
        self.connection = connection or Web3Connection()
        self.address = address
        if isinstance(abi, str) and abi.endswith(".json"):
            with open(abi, "r") as f:
                self.abi = json.load(f)["abi"]  # Assume standard artifact
        else:
            self.abi = abi
        self.contract = self.connection.w3.eth.contract(address=address, abi=self.abi)
        logger.info("LOLAContract init", extra={"address": address, "functions": len(self.abi)})

    def call(self, function_name: str, *args, **kwargs) -> Any:
        """
        Calls contract function (read-only).

        Args:
            function_name: Function name.
            *args, **kwargs: Function params.

        Returns:
            Call result.

        Does Not: Estimate gas—use utils/gas_estimate.
        """
        func = self.contract.functions[function_name]
        result = func(*args, **kwargs).call()
        logger.debug("Contract call", extra={"function": function_name, "result_type": type(result)})
        return result

__all__ = ["LOLAContract"]