# Standard imports
from typing import Dict, Any, Optional

# Third-party imports
# None (uses phase 4 contract)

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger
from lola.chains.contract import LOLAContract
from lola.tools.base import BaseTool
from lola.chains.connection import Web3Connection

"""
File: Onchain contract call tool for LOLA EVM read operations.

Purpose: Enables agents to call EVM contract functions (read-only) via phase 4 LOLAContract, for V1 tools.
How: Extends BaseTool with execute via contract.call, config for ABI/address, logs call/result.
Why: Provides safe, verifiable EVM reads in V1 agents, no lock-in (config ABI/address).
Full Path: lola-os/python/lola/tools/onchain/contract_call.py
"""

logger = setup_logger("lola.tools.onchain.contract_call")

class ContractCallTool(BaseTool):
    """ContractCallTool: Tool for EVM contract read calls. Does NOT write—use TransactTool for TX."""

    def __init__(self):
        """
        Init ContractCallTool with base name/description.

        Does Not: Load config in init—via execute.
        """
        super().__init__(
            name="contract_call",
            description="Calls EVM contract function (read-only) with ABI/address/function/params for data query."
        )

    def execute(self, address: str, abi: str, function_name: str, *args) -> Any:
        """
        Calls contract function with params for read.

        Args:
            address: Contract address (str).
            abi: ABI string/list (str for JSON).
            function_name: Function name (str).
            *args: Function params (e.g., address for balanceOf).

        Returns:
            Call result (e.g., int for balance).

        Does Not: Estimate gas—read-only call.
        """
        # Basic param sanity (fast-fail). BaseTool.validate remains authoritative
        if not isinstance(address, str) or not address.startswith("0x"):
            raise ValueError("Invalid params for contract call: address must be hex string starting with 0x.")
        if not isinstance(function_name, str) or not function_name:
            raise ValueError("Invalid params for contract call: function_name required.")

        validated = self.validate(address=address, abi=abi, function_name=function_name)
        if not validated or not validated.get("valid", False):
            raise ValueError("Invalid params for contract call.")

        # Default chain via Web3Connection (reads config inside)
        conn = Web3Connection()  # Default chain
        contract = LOLAContract(address, abi, conn)
        result = contract.call(function_name, *args)
        logger.info(
            "Contract call executed",
            extra={
                "address": address[:10] + "...",
                "function": function_name,
                "result_type": type(result).__name__
            }
        )
        return result

__all__ = ["ContractCallTool"]
