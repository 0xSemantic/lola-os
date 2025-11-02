# Agents Combined: ConversationalAgent with Tools/EVM (LOLA OS V1 Example)

## Overview
Integrates agents: Conversational with memory/tools for multi-turn EVM query. Why? Phase 6 full templates—chat-like onchain for V1. Run: <1min. Output: Response/tools/summary + log.

## Prerequisites
- Poetry.
- Gemini key, Infura RPC, testnet key.

## Setup
1. `cd examples/version_1/agents_combined`
2. `cp .env.sample .env` & fill.
3. `poetry install`.

## Run
`python agent.py`

Expected: "Response: Your balance is 1 ETH. Gas prices: ..." + "Tools: {'contract_call': 1000000000000000000}" + "Summary: User asked balance..."

## Walkthrough
agent.py self-doc: Docblock explains. Key lines:
1. `agent = ConversationalAgent()`: Init with memory.
2. `agent.bind_tools([WebCrawlTool(), ContractCallTool()])`: Bind phase 5 tools.
3. `state = agent.run("Check balance", history)`: Memory summary → LLM respond/act → tool execute.
4. Print/log: Response + tool_results + summary.

**Exercise 1:** Multi-turn. Add history loop, rerun with "Transfer 0.5 ETH"—check tool chain.
**Exercise 2:** Add ReAct. Switch to ReActAgent, rerun—see reasoning loop.

## Troubleshooting
- LLM error? Check key. Log: "LLM call".
- EVM error? Falsify RPC/key. Log: "Connection failed".
- No summary? Empty history; test with prior.

Best: Memory for context, tools for action in chat.

## Next Steps
Extend: Phase 7 CLI run templates (e.g., lola run react). Phase 8: 24 examples with agents.

Files: agent.py (self-doc), config.yaml, .env.sample, README.