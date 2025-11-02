# Agents Standalone: PlanExecuteAgent Run (LOLA OS V1 Example)

## Overview
Zero-mastery demo of PlanExecuteAgent: LLM plan + graph execute with tool. Why? Phase 6 templates—structured reasoning for V1. Run: <1min. Output: Plan + results + log.

## Prerequisites
- Poetry/Python 3.12+.
- Gemini key.

## Setup
1. `cd examples/version_1/agents_standalone`
2. `cp .env.sample .env` & fill.
3. `poetry install`.

## Run
`python agent.py`

Expected: "Plan: 1. Research flights to New York. 2. Check hotels..." + "Results: {'web_crawl': {'content': 'Trip info...'}}"

## Walkthrough
agent.py self-doc: Docblock explains. Key lines:
1. `agent = PlanExecuteAgent()`: Init with memory.
2. `agent.bind_tools([WebCrawlTool()])`: Bind phase 5 tool.
3. `state = agent.run("Plan trip")`: LLM plan → graph nodes/edges → execute.
4. Print/log: Plan + tool_results.

**Exercise 1:** Add tool. Bind TransactTool, run "Plan and transfer 1 ETH"—check EVM sim.
**Exercise 2:** Custom plan prompt. Edit plan_prompt in run, rerun.

## Troubleshooting
- LLM error? Check key. Log: "LLM call".
- No plan? Prompt tweak; Gemini rate.

Best: Plan for complex tasks, graph for steps.

## Next Steps
Integrate: See agents_combined for conversational with EVM. Phase 7: CLI run uses templates.

Files: agent.py (self-doc), config.yaml, .env.sample, README.