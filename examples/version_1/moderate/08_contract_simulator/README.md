# Contract Simulator (Moderate Example 8)

A LOLA OS agent for simulating EVM contract calls.

## Overview
Uses ReActAgent with simulate_call utility to test contract calls on Sepolia. Ideal for intermediate users learning contract simulation.

## Prerequisites
- Python 3.12+ and Poetry.
- Gemini API key (https://ai.google.dev).
- Sepolia testnet RPC (https://alchemy.com).

## Setup
1. Navigate:
   ```bash
   cd examples/version_1/moderate/08_contract_simulator
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
- Or: `poetry run lola run --query "Simulate balanceOf 0x... on Sepolia"`.
- Expected: Agent response with simulated call result.

## Walkthrough
- `agent.py`: Uses ReActAgent with simulate_call for contract testing.
- `config.yaml`: Sets Gemini model and Sepolia RPC.
- Exercise: Add support for simulating multiple functions in `_build_prompt`.

## Troubleshooting
- Simulation fail? Check contract address or RPC in `.env`.
- JSON error? Verify LLM response format.

## Best Practices
- Simulate calls before live execution.
- Log simulation results.
- Never commit `.env` (add to .gitignore).

## Next Steps
- Move to advanced examples for complex workflows.
- Explore tutorials in docs/ for more.