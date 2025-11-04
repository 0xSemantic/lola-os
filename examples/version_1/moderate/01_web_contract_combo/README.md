# Web-Contract Combo (Moderate Example 1)

A LOLA OS agent combining web crawling and EVM contract reads.

## Overview
Uses ReActAgent with WebCrawlTool and ContractCallTool to fetch web data and contract data in a single workflow. Ideal for intermediate users learning multi-tool coordination.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/moderate/01_web_contract_combo
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
- Or: `poetry run lola run --query "Crawl https://coingecko.com for ETH price and read balanceOf 0x... on Sepolia"`.
- Expected: Agent response with price and balance.

## Walkthrough
- `agent.py`: Uses ReActAgent for multi-tool coordination.
- `config.yaml`: Sets Gemini model and Sepolia RPC.
- Exercise: Add validation for web data before contract call.

## Troubleshooting
- Web fail? Check URL or selectors in query.
- Contract fail? Verify address and RPC in `.env`.

## Best Practices
- Use ReAct for structured workflows.
- Log tool actions and errors.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 02_transact_with_check for transaction workflows.
- Explore tutorials in docs/ for more.