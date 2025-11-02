# Core Standalone: BaseAgent LLM Call (LOLA OS V1 Example)

## Overview
Zero-mastery demo of BaseAgent: Init with config, run query via call_llm (Gemini default). Why? V3 core foundation—self-doc code teaches sovereignty. Run: <30s. Output: Query/response + log.

## Prerequisites
- Poetry/Python 3.12+.
- Free Gemini key [](https://aistudio.google.com).

## Setup
1. `cd examples/version_1/core_standalone`
2. `cp .env.sample .env` & fill GEMINI_API_KEY.
3. `poetry install` (root).

## Run
`python agent.py`

Expected: "Query: What is LOLA OS?" + "Response: LOLA OS is a layered orchestration for logic and automation on-chain..."

## Walkthrough
agent.py self-doc: Docblock explains. Key lines:
1. `class SimpleAgent(BaseAgent)`: Extend with run → call_llm.
2. `response = self.call_llm(...)`: Proxy to Gemini.
3. `State(...)`: Messages with response, validates.
4. Print/log: Human-readable.

**Exercise 1:** Custom prompt. Edit run prompt to "Summarize {query}", rerun.
**Exercise 2:** Bind tool. Add self.bind_tools([MockTool()]), rerun (extend run to use tools).

## Troubleshooting
- API error? Check key/rate. Log: "LLM call".
- Validation fail? Messages empty? See state.py docstring.

Best: Config for model switch, state for verifiable flow.

## Next Steps
Integrate: See core_combined for graph+memory. Phase 4: Chains add EVM tools to bind.

Files: agent.py (self-doc), config.yaml, .env.sample, README.