# Contract Reader (Easy Example 2)

A LOLA OS agent for reading EVM contract data.

## Overview
Uses BaseAgent with ContractCallTool to read data from Sepolia contracts. Ideal for beginners learning blockchain interactions.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/easy/02_contract_reader
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
- Or: `poetry run lola run --query "Read balanceOf 0x... on Sepolia"`.
- Expected: Agent response with contract data.

## Walkthrough
- `agent.py`: Simple BaseAgent using ContractCallTool for read-only calls.
- `config.yaml`: Sets Gemini model and Sepolia RPC.
- Exercise: Try querying a different function (e.g., "Read totalSupply 0x... on Sepolia").

## Troubleshooting
- Call fail? Check contract address and RPC in `.env`.
- Key error? Verify `GEMINI_API_KEY`.

## Best Practices
- Use valid contract addresses.
- Log errors for debugging.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 03_transact for blockchain writes.
- Explore tutorials in docs/ for more.