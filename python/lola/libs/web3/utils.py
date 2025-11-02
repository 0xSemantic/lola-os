# Standard imports
from typing import Dict, Any

# Third-party imports
from web3 import Web3

# Local imports
from lola.utils.logging import setup_logger
from .connection import Web3Connection

"""
File: Web3 utils for LOLA gas estimation and simulation.

Purpose: Helpers for gas/TX sim in V1 chains/tools.
How: Uses w3.eth.estimate_gas/call for sim.
Why: Prevents failed TX in agents (dry-run).
Full Path: lola-os/python/lola/libs/web3/utils.py
"""

logger = setup_logger("lola.web3.utils")

def gas_estimate(connection: Web3Connection, tx: Dict[str, Any]) -> int:
    """
    Estimates gas for TX.

    Args:
        connection: Web3Connection.
        tx: TX dict (to/value/data/gasPrice etc.).

    Returns:
        Estimated gas.

    Does Not: Sign TX—unsigned only.
    """
    try:
        gas = connection.w3.eth.estimate_gas(tx)
        logger.debug("Gas estimated", extra={"gas": gas})
        return gas
    except Exception as e:
        logger.error("Gas estimation failed", extra={"error": str(e)})
        raise

def simulate_call(connection: Web3Connection, tx: Dict[str, Any]) -> Any:
    """
    Simulates TX call (dry-run).

    Args:
        connection: Web3Connection.
        tx: TX dict.

    Returns:
        Call result or revert reason.

    Does Not: Broadcast—sim only.
    """
    try:
        result = connection.w3.eth.call(tx)
        logger.debug("TX simulated success")
        return result
    except Exception as e:
        logger.warning("TX sim revert", extra={"reason": str(e)})
        return {"revert": str(e)}

__all__ = ["gas_estimate", "simulate_call"]