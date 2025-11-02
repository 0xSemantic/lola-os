# Standard imports
from typing import Dict, str

# Third-party imports
# None

# Local imports
from lola.chains.connection import Web3Connection
from lola.chains.wallet import LOLAWallet
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Standalone example: EVM balance read with Web3Connection and LOLAWallet.

Purpose: Demonstrates chains in isolation: Load config RPC/key, connect chain, read balance.
How: Init connection/wallet with config, fetch balance, log/print.
Why: Onboarding to Phase 4—shows multi-RPC interop without tools/agents.
Full Path: lola-os/examples/version_1/chains_standalone/agent.py
"""

if __name__ == "__main__":
    # Inline: Load config for RPCs/key
    config = load_config()
    logger = setup_logger()
    if not config.evm_rpcs or not config.evm_private_key:
        print("No RPCs/key in config; set EVM_RPCS_SEPOLIA and EVM_PRIVATE_KEY in .env.")
        exit(1)
    conn = Web3Connection("sepolia")
    wallet = LOLAWallet()
    balance = wallet.balance()
    logger.info("Standalone balance read", extra={"wei": balance, "eth": wallet.connection.w3.from_wei(balance, "ether")})
    print(f"Wallet: {wallet.account.address}")
    print(f"Balance: {balance} wei ({wallet.connection.w3.from_wei(balance, 'ether')} ETH)")