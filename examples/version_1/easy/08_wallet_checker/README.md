# Wallet Checker (Easy Example 8)

A LOLA OS agent for checking wallet balances on Sepolia.

## Overview
Uses BaseAgent with LOLAWallet to query wallet balances. Ideal for beginners learning wallet operations.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/easy/08_wallet_checker
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
- Or: `poetry run lola run --query "Check balance for 0x... on Sepolia"`.
- Expected: Agent response with wallet balance.

## Walkthrough
- `agent.py`: Uses BaseAgent with LOLAWallet for balance queries.
- `config.yaml`: Sets Gemini model and Sepolia RPC.
- Exercise: Try checking a different wallet address.

## Troubleshooting
- Balance fail? Check address or RPC in `.env`.
- Key error? Verify `GEMINI_API_KEY`.

## Best Practices
- Use valid EVM addresses.
- Log balance results.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Move to moderate examples for multi-tool tasks.
- Explore tutorials in docs/ for more.