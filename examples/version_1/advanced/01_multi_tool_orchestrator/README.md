# Multi-Tool Orchestrator (Advanced Example 1)

A LOLA OS agent for orchestrating web crawling, contract reads, and transactions.

## Overview
Uses ReActAgent with SupervisedStateGraph to coordinate multiple tools in a stateful workflow. Ideal for advanced users mastering complex orchestration.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC and private key (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/advanced/01_multi_tool_orchestrator
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
- Or: `poetry run lola run --query "Crawl https://coingecko.com for ETH price, read balanceOf 0x..., and send 0.1 ETH if balance sufficient"`.
- Expected: Agent response with price, balance, and transaction result.

## Walkthrough
- `agent.py`: Uses ReActAgent with SupervisedStateGraph for multi-tool workflow.
- `config.yaml`: Sets Gemini Pro model and Sepolia RPC.
- Exercise: Add gas estimation before transaction in `_build_prompt`.

## Troubleshooting
- Tool fail? Check tool inputs or RPC in `.env`.
- JSON error? Verify LLM response format.

## Best Practices
- Use state graphs for complex workflows.
- Log all tool actions and errors.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 02_dynamic_contract_interactor for dynamic contract tasks.
- Explore tutorials in docs/ for more.