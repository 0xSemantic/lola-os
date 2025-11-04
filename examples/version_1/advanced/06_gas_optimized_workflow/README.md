# Gas-Optimized Workflow (Advanced Example 6)

A LOLA OS agent for gas-optimized transactions.

## Overview
Uses PlanExecuteAgent with SupervisedStateGraph for gas estimation and transactions on Sepolia. Ideal for advanced users optimizing blockchain operations.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC and private key (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/advanced/06_gas_optimized_workflow
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
- Or: `poetry run lola run --query "Send 0.1 ETH to 0x... on Sepolia with gas optimization"`.
- Expected: Agent response with gas estimate and transaction result.

## Walkthrough
- `agent.py`: Uses PlanExecuteAgent for gas-optimized transactions.
- `config.yaml`: Sets Gemini Pro model and Sepolia RPC.
- Exercise: Add gas limit validation in `_should_execute`.

## Troubleshooting
- TX fail? Check balance or RPC in `.env`.
- Gas fail? Verify gas estimation logic.

## Best Practices
- Always estimate gas before transactions.
- Log planning and execution steps.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 07_conversational_blockchain for conversational blockchain tasks.
- Explore tutorials in docs/ for more.