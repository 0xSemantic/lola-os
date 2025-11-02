# Core Concepts (V1)

## Core: Orchestration Engine
- **State**: Pydantic model for messages/tool_results (validate/serialize with config max_messages).
- **Graph**: LOLAStateGraph for async workflows (supervision/reflection via phase 2 adapter).
- **Memory**: JSON persistence (StateManager), LLM entity/summary (ConversationMemory).
- **Agent**: BaseAgent with call_llm/graph run/bind_tools (abstract run for templates).

Use: `from lola.core import BaseAgent, LOLAStateGraph`—config-driven limits/LLM.

Next: Phase 4 chains use State for EVM results in graph nodes.