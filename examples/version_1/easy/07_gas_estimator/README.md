# Gas Estimator (Easy Example 7)

A LOLA OS agent for estimating gas costs of EVM transactions.

## Overview
Uses BaseAgent with gas_estimate utility to calculate gas for Sepolia transactions. Ideal for beginners learning gas concepts.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/easy/07_gas_estimator
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
- Or: `poetry run lola run --query "Estimate gas for sending 0.1 ETH to 0x..."`.
- Expected: Agent response with gas estimate.

## Walkthrough
- `agent.py`: Uses BaseAgent with gas_estimate for transaction cost.
- `config.yaml`: Sets Gemini model and Sepolia RPC.
- Exercise: Try estimating gas for a different amount (e.g., "Estimate gas for sending 0.01 ETH").

## Troubleshooting
- Gas fail? Check RPC or address in `.env`.
- Key error? Verify `GEMINI_API_KEY`.

## Best Practices
- Test gas estimates on testnets.
- Log estimation details.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 08_wallet_checker for wallet tasks.
- Explore tutorials in docs/ for more.