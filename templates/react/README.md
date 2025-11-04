# Market-Ready ReAct Agent Template

## Overview
This is a production-grade ReAct agent template for LOLA OS, featuring reasoning-action loops with LLM, tools, memory, error handling, and logging. Ideal for dynamic tasks like research or on-chain interactions.

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
lola run --query "Research Ethereum price and analyze"
```
- Output: Agent state with messages, tool results, and summary.

## Walkthrough
- `agent.py`: `Agent` class with `_build_prompt` for structured output, `_parse_response` for JSON parsing, `_execute_tool` with error handling.
- Key Features: Turn limits, memory summarization, logging for traceability.
- Exercise: Add an EVM tool—import `from lola.tools.onchain.contract_call import ContractCallTool`, bind in `__init__`, test with query involving blockchain.

## Troubleshooting
- LLM fail? Check `.env` key and config model.
- Tool error? Ensure inputs match tool schema; log file (`lola.log`) has details.
- Infinite loop? Adjust `max_turns` in config.yaml.

## Best Practices
- Use structured prompts for reliable parsing.
- Handle exceptions in custom tools.
- Monitor costs with LiteLLM's logging.
- Test with real data (e.g., testnet RPCs).

## Next Steps
- Integrate EVM: Add `from lola.tools.onchain import *` and bind.
- Scale: Subclass for custom parsing/prompts.
- Deploy: Wrap in FastAPI for API (future versions).