# Core Combined: Agent + Graph + Memory (LOLA OS V1 Example)

## Overview
Integrates core: Agent with graph (reason node), memory (extract/summarize). Why? V3 full workflow—async orchestration with context. Run: <1min. Output: Reason/entities/summary.

## Prerequisites
- Poetry.
- Gemini key.

## Setup
1. `cd examples/version_1/core_combined`
2. `cp .env.sample .env` & fill.
3. `poetry install`.

## Run
`python agent.py`

Expected: "Reason: To plan the trip, first check flights to New York..." + "Entities: ['Alice', 'New York', '2025-01-01']" + "Summary: Alice plans trip to New York on Jan 1, 2025."

## Walkthrough
agent.py self-doc: Docblock explains. Key lines:
1. `class GraphAgent(BaseAgent)`: Adds graph/memory, reason_node with LLM.
2. `self.graph.add_node/edge` : Builds async workflow.
3. `asyncio.run(self.graph.execute(...))` : Runs with initial State.
4. `self.memory.extract_entities(...)` : LLM extract from messages.

**Exercise 1:** Add node. Add self.graph.add_node("reflect", self.reflect_node), add_edge("reason", "reflect"), rerun.
**Exercise 2:** Save/load. Add StateManager.save(state, "state.json"), load in next run.

## Troubleshooting
- Async error? Ensure Python 3.12+.
- No entities? LLM variation; prompt tweak in extract_entities.

Best: Graph for parallel steps, memory for long chains.

## Next Steps
Extend: Phase 5 tools in graph nodes (e.g., web_crawl in reason). Phase 4: Chains for EVM state.

Files: agent.py (self-doc), config.yaml, .env.sample, README.