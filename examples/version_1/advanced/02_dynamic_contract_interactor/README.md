# Dynamic Contract Interactor (Advanced Example 2)

A LOLA OS agent for dynamic contract calls and transactions.

## Overview
Uses PlanExecuteAgent with SupervisedStateGraph to plan, simulate, and execute contract interactions on Sepolia. Ideal for advanced users mastering contract workflows.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC and private key (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/advanced/02_dynamic_contract_interactor
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
- Or: `poetry run lola run --query "Simulate and execute transfer 0.1 ETH to 0x... on Sepolia"`.
- Expected: Agent response with simulation and execution results.

## Walkthrough
- `agent.py`: Uses PlanExecuteAgent with state graph for contract interactions.
- `config.yaml`: Sets Gemini Pro model and Sepolia RPC.
- Exercise: Add gas estimation to `_build_prompt` for safer execution.

## Troubleshooting
- Simulation fail? Check contract address or RPC in `.env`.
- JSON error? Verify LLM response format.

## Best Practices
- Simulate calls before execution.
- Log all planning and execution steps.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 03_wallet_analytics for wallet analytics.
- Explore tutorials in docs/ for more.