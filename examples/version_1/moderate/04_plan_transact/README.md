# Plan Transact (Moderate Example 4)

A LOLA OS agent for planning and executing EVM transactions.

## Overview
Uses PlanExecuteAgent with TransactTool to plan and send transactions on Sepolia. Ideal for intermediate users learning planning workflows.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC and private key (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/moderate/04_plan_transact
   ```
2. Install (if not root):
   ```bash
   poetry install
   ```
3. Copy env:
   ```bash
   cp .env.sample .env
   ```
4. Edit `.env` with `GEMINI_API_KEY`, `PRIVATE_KEY`, `EVM_RPC_SEPOLIA`.

## Run
```bash
poetry run python agent.py
```
- Or: `poetry run lola run --query "Plan to send 0.1 ETH to 0x... on Sepolia"`.
- Expected: Agent response with plan and transaction hash.

## Walkthrough
- `agent.py`: Uses PlanExecuteAgent for planning and transacting.
- `config.yaml`: Sets Gemini model and Sepolia RPC.
- Exercise: Add balance check before transaction in `_build_prompt`.

## Troubleshooting
- TX fail? Check balance or gas in `.env`.
- Plan fail? Verify LLM response format.

## Best Practices
- Plan critical steps before execution.
- Log planning and transaction details.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 05_wallet_monitor for wallet monitoring.
- Explore tutorials in docs/ for more.