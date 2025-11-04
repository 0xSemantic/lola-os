# Gas-Aware Transact (Moderate Example 6)

A LOLA OS agent for sending transactions with gas estimation.

## Overview
Uses ReActAgent with TransactTool and gas_estimate to send gas-aware transactions on Sepolia. Ideal for intermediate users learning gas optimization.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC and private key (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/moderate/06_gas_aware_transact
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
- Or: `poetry run lola run --query "Send 0.1 ETH to 0x... on Sepolia with gas check"`.
- Expected: Agent response with gas estimate and transaction hash.

## Walkthrough
- `agent.py`: Uses ReActAgent for gas estimation and transaction.
- `config.yaml`: Sets Gemini model and Sepolia RPC.
- Exercise: Add gas limit validation in `_execute_tool`.

## Troubleshooting
- TX fail? Check balance or gas in `.env`.
- Gas fail? Verify RPC in `.env`.

## Best Practices
- Estimate gas before transactions.
- Log gas and transaction details.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 07_stateful_conversation for stateful chat.
- Explore tutorials in docs/ for more.