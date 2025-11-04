# Stateful Multi-Agent (Advanced Example 5)

A LOLA OS multi-agent system for web and contract tasks.

## Overview
Uses SupervisedStateGraph to coordinate ConversationalAgent and ReActAgent for complex tasks. Ideal for advanced users mastering multi-agent systems.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/advanced/05_stateful_multi_agent
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
- Or: `poetry run lola run --query "Discuss market trends and check contract 0x... on Sepolia"`.
- Expected: Agent response with discussion and contract data.

## Walkthrough
- `agent.py`: Uses state graph to coordinate ConversationalAgent and ReActAgent.
- `config.yaml`: Sets Gemini Pro model and Sepolia RPC.
- Exercise: Add transaction tool to ReActAgent in `_react`.

## Troubleshooting
- Routing fail? Check `_route_to_react` logic.
- Tool fail? Verify RPC or query format.

## Best Practices
- Use state graphs for agent coordination.
- Log all agent actions and routing decisions.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Try 06_gas_optimized_workflow for gas optimization.
- Explore tutorials in docs/ for more.