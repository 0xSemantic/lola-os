# Monitor and Act (Advanced Example 8)

A LOLA OS agent for monitoring wallet and triggering transactions.

## Overview
Uses ReActAgent with SupervisedStateGraph to monitor wallet balance and trigger transactions on Sepolia. Ideal for advanced users building automated workflows.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC and private key (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/advanced/08_monitor_and_act
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
- Or: `poetry run lola run --query "Monitor 0x... balance and send 0.1 ETH if balance > 1 ETH"`.
- Expected: Agent response with balance and transaction result.

## Walkthrough
- `agent.py`: Uses ReActAgent with state graph for monitoring and actions.
- `config.yaml`: Sets Gemini Pro model and Sepolia RPC.
- Exercise: Add periodic monitoring with a loop in `_monitor`.

## Troubleshooting
- Monitor fail? Check address or RPC in `.env`.
- TX fail? Verify balance or gas settings.

## Best Practices
- Use state graphs for automated workflows.
- Log all monitoring and transaction actions.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Explore tutorials in docs/ for more advanced workflows.
- Build custom agents based on these examples.