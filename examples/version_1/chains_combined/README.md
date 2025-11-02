# Chains Combined: Contract Call + Wallet Sim (LOLA OS V1 Example)

## Overview
Integrates chains: Connect, load contract ABI, call function, sim TX with gas est. Why? Phase 4 full EVM—read/write flow for V1. Run: <1min. Output: Balance/gas/sim + log.

## Prerequisites
- Poetry.
- Infura RPC, testnet key (Sepolia).

## Setup
1. `cd examples/version_1/chains_combined`
2. `cp .env.sample .env` & fill RPC/key.
3. `poetry install`.

## Run
`python agent.py`

Expected: "Balance: 0 tokens" + "Gas est: 65000" + "Sim: 0x..." or "revert..."

## Walkthrough
agent.py self-doc: Docblock explains. Key lines:
1. `conn = Web3Connection("sepolia")`: Multi-RPC from config.
2. `contract = LOLAContract(...)`: ABI load, call "balanceOf".
3. `gas = gas_estimate(...)`: Pre-TX est.
4. `sim = simulate_call(...)`: Dry-run check.

**Exercise 1:** Real contract. Change address/ABI to USDC, rerun (add tokens via faucet).
**Exercise 2:** Sign TX. Add signed = wallet.sign_tx(tx); print(signed.hex()).

## Troubleshooting
- Connection error? Check RPC in .env. Log: "Failed to connect".
- Invalid ABI? ValueError; use valid JSON.
- No balance? Faucet tokens.

Best: Utils for safe TX before sign/broadcast.

## Next Steps
Extend: Phase 5 tools use chains (e.g., onchain tool with contract call). Phase 6: Agents bind tools for EVM.

Files: agent.py (self-doc), config.yaml, .env.sample, README.