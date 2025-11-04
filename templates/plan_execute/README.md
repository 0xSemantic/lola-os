# Market-Ready Plan-Execute Agent Template

## Overview
This is a production-grade Plan-Execute agent template for LOLA OS, featuring LLM planning, dynamic graph execution, tool integration, memory summarization, and error handling. Ideal for multi-step tasks like planning workflows or on-chain sequences.

## Prerequisites
- Python 3.12+, Poetry installed.
- LOLA OS full installation (`poetry install` in root).
- Gemini API key for LLM (free tier available at https://ai.google.dev/).

## Setup
1. Copy `.env.sample` to `.env` and set `GEMINI_API_KEY`.
2. Run `poetry install` in this directory.
3. Optional: Bind custom tools in `agent.py` (e.g., onchain tools).

## Run
```bash
lola run --query "Plan a trip to NY and book flight"
```
- Output: Agent state with plan, step executions, tool results, and summary.

## Walkthrough
- `agent.py`: `Agent` class with `_build_plan_prompt` for structured planning, `_parse_plan` for step extraction, `_build_graph` for dynamic nodes, and `_execute_tool` with error handling.
- Key Features: Async execution, memory for context, logging for traceability.
- Exercise: Add an EVM tool—import `from lola.tools.onchain.transact import TransactTool`, bind in `__init__`, test with query involving transactions.

## Troubleshooting
- Plan empty? Check LLM key and prompt in `_build_plan_prompt`.
- Tool error? Ensure inputs match; log file (`lola.log`) has details.
- Graph fail? Verify steps parse correctly.

## Best Practices
- Use descriptive prompts for accurate planning.
- Limit steps in complex tasks to avoid overhead.
- Monitor async performance with logging.

## Next Steps
- Integrate EVM: Add `from lola.tools.onchain import *` and bind.
- Scale: Subclass for custom graph logic.
- Deploy: Use in services with persistent memory.