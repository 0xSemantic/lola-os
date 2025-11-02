# Standard imports
from typing import Dict, str, Any

# Third-party imports
# None

# Local imports
from lola.chains.connection import Web3Connection
from lola.chains.contract import LOLAContract
from lola.chains.wallet import LOLAWallet
from lola.chains.utils import gas_estimate, simulate_call
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Combined example: EVM contract call with wallet and sim.

Purpose: Demonstrates chains integration: Connect, load contract, call function, sign/sim TX, gas est.
How: Init connection/wallet/contract, call query, sim TX, log/print.
Why: Previews Phase 4 full EVM flow for V1 tools/agents.
Full Path: lola-os/examples/version_1/chains_combined/agent.py
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
    # Example: ERC20 balance call
    abi = [{"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}]
    contract = LOLAContract("0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238", abi, conn)  # Testnet USDC
    balance = contract.call("balanceOf", wallet.account.address)
    # Sim TX (e.g., transfer)
    tx = {"to": contract.address, "value": 0, "data": contract.contract.functions.transfer("0xdead...", 100).build_transaction()["data"], "from": wallet.account.address}
    gas = gas_estimate(conn, tx)
    sim = simulate_call(conn, tx)
    logger.info("Combined EVM flow", extra={"balance": balance, "gas": gas, "sim": "success" if isinstance(sim, bytes) else "revert"})
    print(f"Balance: {balance} tokens")
    print(f"Gas est: {gas}")
    print(f"Sim: {sim if isinstance(sim, bytes) else sim['revert'][:50]}...")