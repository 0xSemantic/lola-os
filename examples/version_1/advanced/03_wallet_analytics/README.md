# Wallet Analytics (Advanced Example 3)

A LOLA OS agent for analyzing wallet balance and contract interactions.

## Overview
Uses PlanExecuteAgent with Wallet and ContractCallTool to analyze wallet data on Sepolia. Ideal for advanced users building analytics workflows.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/advanced/03_wallet_analytics
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
- Or: `poetry run lola run --query "Analyze balance and token holdings for 0x... on Sepolia"`.
- Expected: Agent response with balance and token data.

## Walkthrough
- `agent.py`: Uses PlanExecuteAgent for wallet and contract analytics.
- `config.yaml`: Sets Gemini Pro model and Sepolia RPC.
- Exercise: Add support for multiple token contracts in `_build_prompt`.

## Troubleshooting
- Analysis fail? Check address or RPC in `.env`.
- JSON error? Verify LLM response format.

## Best Practices
- Plan analytics steps carefully.
- Log all tool actions and results.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 04_web_blockchain_integrator for web-blockchain tasks.
- Explore tutorials in docs/ for more.