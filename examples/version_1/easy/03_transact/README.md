# Transact (Easy Example 3)

A LOLA OS agent for sending simple EVM transactions.

## Overview
Uses BaseAgent with TransactTool to send ETH on Sepolia. Ideal for beginners learning blockchain writes.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC and private key (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/easy/03_transact
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
- Or: `poetry run lola run --query "Send 0.1 ETH to 0x... on Sepolia"`.
- Expected: Agent response with transaction hash.

## Walkthrough
- `agent.py`: Simple BaseAgent using TransactTool for ETH transfers.
- `config.yaml`: Sets Gemini model and Sepolia RPC.
- Exercise: Try sending a different amount (e.g., "Send 0.01 ETH to 0x...").

## Troubleshooting
- TX fail? Check balance or gas in `.env`.
- Key error? Verify `PRIVATE_KEY`.

## Best Practices
- Test with small amounts on testnets.
- Log transaction details.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 04_conversational for chat-based tasks.
- Explore tutorials in docs/ for more.