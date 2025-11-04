# Market-Ready Conversational Agent Template

## Overview
This is a production-grade Conversational agent template for LOLA OS, featuring multi-turn context via memory, tool actions, structured responses, error handling, and logging. Ideal for interactive bots like assistants or query handlers.

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
lola run --query "What's the weather?" --history '[{"role": "user", "content": "Hello"}]'
```
- Output: Updated state with response, tool results (if used), and summary.

## Walkthrough
- `agent.py`: `Agent` class with `_build_prompt` for structured JSON, `_parse_action` for tool detection, `_execute_tool` with error handling, and memory for history summarization.
- Key Features: JSON output for parsing, logging for turns, flexible history input.
- Exercise: Add an EVM tool—import `from lola.tools.onchain.contract_call import ContractCallTool`, bind in `__init__`, test with query needing blockchain data.

## Troubleshooting
- No context? Pass `--history` as JSON list.
- Parse error? Check LLM response format in logs (`lola.log`).
- Tool fail? Verify tool name/inputs.

## Best Practices
- Use JSON for reliable action parsing.
- Persist history externally for sessions.
- Limit history length to avoid token overflow.

## Next Steps
- Integrate EVM: Add `from lola.tools.onchain import *` and bind.
- Scale: Subclass for session management.
- Deploy: Use in chat apps with persistent memory.