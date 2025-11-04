# Web-Blockchain Integrator (Advanced Example 4)

A LOLA OS agent for integrating web data with blockchain transactions.

## Overview
Uses ReActAgent with SupervisedStateGraph to combine web crawling and transactions on Sepolia. Ideal for advanced users building integrated workflows.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC and private key (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/advanced/04_web_blockchain_integrator
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
- Or: `poetry run lola run --query "Crawl https://coingecko.com for ETH price and send 0.1 ETH to 0x... if price > $2000"`.
- Expected: Agent response with price and transaction result.

## Walkthrough
- `agent.py`: Uses ReActAgent with state graph for web-blockchain integration.
- `config.yaml`: Sets Gemini Pro model and Sepolia RPC.
- Exercise: Add conditional logic for price thresholds in `_build_prompt`.

## Troubleshooting
- Web fail? Check URL or selectors in query.
- TX fail? Verify balance or RPC in `.env`.

## Best Practices
- Validate web data before transactions.
- Log all tool actions and results.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 05_stateful_multi_agent for multi-agent tasks.
- Explore tutorials in docs/ for more.