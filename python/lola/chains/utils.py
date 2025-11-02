# Standard imports
from typing import Dict, Any

# Third-party imports
from web3 import Web3

# Local imports
from lola.utils.logging import setup_logger
from .connection import Web3Connection

"""
File: Utility functions for LOLA EVM gas estimation and TX simulation.

Purpose: Provides gas estimation and call simulation for safe EVM interactions in V1.
How: Uses w3.eth.estimate_gas/call with connection, logs estimates/reverts.
Why: Prevents failed TX in agents/tools (dry-run), no lock-in (connection-based).
Full Path: lola-os/python/lola/chains/utils.py
"""

logger = setup_logger("lola.chains.utils")

def gas_estimate(connection: Web3Connection, tx: Dict[str, Any]) -> int:
    """
    Estimates gas for TX using connection.

    Args:
        connection: Web3Connection for chain.
        tx: TX dict (e.g., {"to": addr, "value": wei, "data": bytes}).

    Returns:
        Estimated gas units.

    Does Not: Sign TX—unsigned only.
    """
    try:
        gas = connection.w3.eth.estimate_gas(tx)
        logger.debug("Gas estimated", extra={"gas": gas, "chain": connection.chain})
        return gas
    except Exception as e:
        logger.error("Gas estimation failed", extra={"error": str(e), "tx": str(tx)[:50] + "..."})
        raise ValueError(f"Gas estimation failed: {e}") from e


def simulate_call(connection: Web3Connection, tx: Dict[str, Any]) -> Any:
    """
    Simulates TX call (dry-run) to check revert/success.

    Args:
        connection: Web3Connection for chain.
        tx: TX dict for call (no nonce/gas).

    Returns:
        Call result (bytes on success, dict with 'revert' reason on fail).

    Does Not: Broadcast—simulation only.
    """
    try:
        result = connection.w3.eth.call(tx)
        logger.debug("TX simulated success", extra={"chain": connection.chain, "result_len": len(result)})
        return result
    except Exception as e:
        revert_reason = str(e).lower()
        logger.warning("TX simulation revert", extra={"reason": revert_reason, "chain": connection.chain})
        return {"revert": revert_reason}

__all__ = ["gas_estimate", "simulate_call"]