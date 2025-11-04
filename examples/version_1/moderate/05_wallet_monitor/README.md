# Wallet Monitor (Moderate Example 5)

A LOLA OS agent for monitoring wallet balance changes.

## Overview
Uses ReActAgent with LOLAWallet to check and alert on balance changes on Sepolia. Ideal for intermediate users learning monitoring workflows.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/moderate/05_wallet_monitor
   ```
2. Install (if not root):
   ```bash
   poetry install
   ```
3. Copy env:
   ```bash
   cp .env.sample .env
   ```
4. Edit `.env` with `GEMINI_API_KEY`, `EVM_RPC_SEPOLIA`.

## Run
```bash
poetry run python agent.py
```
- Or: `poetry run lola run --query "Monitor balance for 0x... on Sepolia"`.
- Expected: Agent response with balance and change alerts.

## Walkthrough
- `agent.py`: Uses ReActAgent with LOLAWallet for balance monitoring.
- `config.yaml`: Sets Gemini model and Sepolia RPC.
- Exercise: Add threshold-based alerts in `_execute_tool`.

## Troubleshooting
- Balance fail? Check address or RPC in `.env`.
- No alerts? Verify balance changes in wallet.

## Best Practices
- Track balance history for monitoring.
- Log balance checks and alerts.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 06_gas_aware_transact for gas-aware transactions.
- Explore tutorials in docs/ for more.