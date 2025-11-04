# Conversational Blockchain (Advanced Example 7)

A LOLA OS agent for conversational blockchain tasks.

## Overview
Uses ConversationalAgent with SupervisedStateGraph for contract calls and transactions on Sepolia. Ideal for advanced users building conversational blockchain workflows.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC and private key (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/advanced/07_conversational_blockchain
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
- Or: `poetry run lola run --query "Check balanceOf 0x... and send 0.1 ETH if sufficient"`.
- Expected: Agent response with balance and transaction result.

## Walkthrough
- `agent.py`: Uses ConversationalAgent with state graph for blockchain tasks.
- `config.yaml`: Sets Gemini Pro model and Sepolia RPC.
- Exercise: Add multi-turn conversation support in `_build_prompt`.

## Troubleshooting
- Tool fail? Check address or RPC in `.env`.
- JSON error? Verify LLM response format.

## Best Practices
- Use state graphs for conversational workflows.
- Log all tool actions and conversations.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 08_monitor_and_act for monitoring and action workflows.
- Explore tutorials in docs/ for more.