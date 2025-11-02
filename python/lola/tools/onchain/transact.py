# Standard imports
from typing import Dict, Any, Optional

# Third-party imports
# None (uses phase 4 wallet/utils)

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger
from lola.chains.wallet import LOLAWallet
from lola.chains.utils import gas_estimate, simulate_call
from lola.tools.base import BaseTool
from lola.chains.connection import Web3Connection

"""
File: Onchain transact tool for LOLA EVM write operations with sim/sign/broadcast.

Purpose: Enables agents to send EVM TX (write) with pre-sim/gas est, for V1 tools.
How: Extends BaseTool with execute via wallet.sign_tx/broadcast, sim/gas via phase 4 utils, config for chain.
Why: Provides safe TX in V1 agents, no lock-in (config chain/key), prevents failed broadcasts.
Full Path: lola-os/python/lola/tools/onchain/transact.py
"""

logger = setup_logger("lola.tools.onchain.transact")

class TransactTool(BaseTool):
    """TransactTool: Tool for EVM TX send with sim/gas. Does NOT read—use ContractCallTool for call."""

    def __init__(self):
        """
        Init TransactTool with base name/description.

        Does Not: Load config in init—via execute.
        """
        super().__init__(
            name="transact",
            description="Sends EVM TX with pre-simulation/gas estimation for safe broadcast."
        )

    def execute(self, to: str, value: int = 0, data: Optional[str] = None, chain: str = "sepolia") -> Dict[str, Any]:
        """
        Builds, sims, signs, and broadcasts TX for write.

        Args:
            to: Recipient address (str).
            value: Value in wei (int, default 0).
            data: Function data/string (optional for call).
            chain: Chain name (via config.evm_rpcs, default "sepolia").

        Returns:
            Dict {"tx_hash": str, "gas_used": int, "status": str ("success"/"revert"/"pending")}.

        Does Not: Validate ABI—raw data for transfer/call.
        """
        if not self.validate(to=to, value=value, data=data, chain=chain)["valid"]:
            raise ValueError("Invalid params for transact.")
        conn = Web3Connection(chain)
        wallet = LOLAWallet(connection=conn)
        nonce = conn.w3.eth.get_transaction_count(wallet.account.address)
        tx = {
            "to": to,
            "value": value,
            "gas": gas_estimate(conn, {"to": to, "value": value, "data": data.encode() if data else b""}),
            "nonce": nonce,
            "data": data.encode() if data else b"",
            "gasPrice": conn.w3.eth.gas_price
        }
        # Inline: Sim before sign
        sim_result = simulate_call(conn, tx)
        if isinstance(sim_result, dict) and "revert" in sim_result:
            raise ValueError(f"TX simulation reverted: {sim_result['revert']}")
        signed_tx = wallet.sign_tx(tx)
        tx_hash = conn.w3.eth.send_raw_transaction(signed_tx).hex()
        logger.info("TX broadcast", extra={"tx_hash": tx_hash, "gas": tx["gas"], "chain": chain})
        return {"tx_hash": tx_hash, "gas_used": tx["gas"], "status": "pending"}

__all__ = ["TransactTool"]