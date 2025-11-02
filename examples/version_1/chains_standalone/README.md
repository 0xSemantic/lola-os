# Chains Standalone: EVM Balance Read (LOLA OS V1 Example)

## Overview
Zero-mastery demo of chains: Load config RPC/key, connect, read wallet balance. Why? Phase 4 EVM basics—no agents/tools. Run: <30s. Output: Address/balance + log.

## Prerequisites
- Poetry/Python 3.12+.
- Free Infura/Alchemy RPC, testnet key (Sepolia faucet).

## Setup
1. `cd examples/version_1/chains_standalone`
2. `cp .env.sample .env` & fill RPC/key.
3. `poetry install`.

## Run
`python agent.py`

Expected: "Wallet: 0x..." + "Balance: 1000000000000000000 wei (1.0 ETH)"

## Walkthrough
agent.py self-doc: Docblock explains. Key lines:
1. `config = load_config()`: RPCs/key from YAML/.env.
2. `conn = Web3Connection("sepolia")`: Multi-RPC switch.
3. `wallet = LOLAWallet()`: Load key, get balance.
4. Print/log: Human-readable ETH.

**Exercise 1:** Switch chain. Change "sepolia" to "polygon", rerun (add EVM_RPCS_POLYGON to .env).
**Exercise 2:** Estimate gas. Add gas = gas_estimate(conn, {"to": wallet.account.address, "value": 0}); print(gas).

## Troubleshooting
- Connection error? Check RPC/key in .env. Log: "Failed to connect".
- Invalid key? ValueError; use 0x64hex (MetaMask export).
- No balance? Faucet ETH.

Best: Config for multi-chain, utils for sim before TX.

## Next Steps
Integrate: See chains_combined for contract call + wallet. Phase 5: Tools use chains for onchain tool.

Files: agent.py (self-doc), config.yaml, .env.sample, README.