# Transact with Check (Moderate Example 2)

A LOLA OS agent for checking balance before sending a transaction.

## Overview
Uses ReActAgent with ContractCallTool and TransactTool to validate balance before a transaction on Sepolia. Ideal for intermediate users learning validation workflows.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC and private key (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/moderate/02_transact_with_check
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
- Or: `poetry run lola run --query "Check balanceOf 0x... and send 0.1 ETH on Sepolia"`.
- Expected: Agent response with balance and transaction hash.

## Walkthrough
- `agent.py`: Uses ReActAgent to check balance before transacting.
- `config.yaml`: Sets Gemini model and Sepolia RPC.
- Exercise: Add gas estimation before transaction using `gas_estimate`.

## Troubleshooting
- TX fail? Check balance or gas in `.env`.
- Contract fail? Verify address and RPC.

## Best Practices
- Validate balance before transactions.
- Log tool actions and errors.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 03_conversational_with_tools for chat-based tasks.
- Explore tutorials in docs/ for more.