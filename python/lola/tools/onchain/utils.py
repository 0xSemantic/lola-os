# Standard imports
from typing import Dict, Any

# Third-party imports
# None (uses phase 4 utils)

# Local imports
from lola.utils.logging import setup_logger
from lola.chains.utils import gas_estimate, simulate_call as chains_simulate_call
from lola.chains.connection import Web3Connection

"""
File: Onchain tool utilities for LOLA, wrapping phase 4 chains utils for tool use.

Purpose: Provides gas estimation and TX simulation helpers for onchain tools in V1.
How: Wraps phase 4 gas_estimate/simulate_call with tool-specific logging/config chain.
Why: Enables safe TX in V1 tools, no lock-in (via chains connection), separate from chains for tool modularity.
Full Path: lola-os/python/lola/tools/onchain/utils.py
"""

logger = setup_logger("lola.tools.onchain.utils")

def gas_helper(chain: str, tx: Dict[str, Any]) -> int:
    """
    Estimates gas for TX via chains connection for tool use.

    Args:
        chain: Chain name (via config.evm_rpcs).
        tx: TX dict (e.g., {"to": addr, "value": wei, "data": bytes}).

    Returns:
        Estimated gas units.

    Does Not: Sign TX—unsigned only.
    """
    conn = Web3Connection(chain)
    return gas_estimate(conn, tx)


def simulate_tx(chain: str, tx: Dict[str, Any]) -> Any:
    """
    Simulates TX call for tool dry-run.

    Args:
        chain: Chain name.
        tx: TX dict for call (no nonce/gas).

    Returns:
        Call result (bytes on success, dict with 'revert' reason on fail).

    Does Not: Broadcast—simulation only.
    """
    conn = Web3Connection(chain)
    return chains_simulate_call(conn, tx)

__all__ = ["gas_helper", "simulate_tx"]