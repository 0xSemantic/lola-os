# Core Concepts (V1)

## Utils: Config & Logging
- **Config**: Pydantic + .env/YAML. Defaults: Gemini 1.5 Flash. Secrets: SecretStr (masked).
- **Logging**: JSON extras, rotation. Use: `logger.info(..., extra={"trace": id})`.

Why? Sovereign: Switch providers via config, no hardcodes.


## Libs: Adapters
- **LiteLLM Proxy**: Routes/fallback (Gemini default), cost est.
- **LangGraph Adapter**: Supervised graphs (turns/reflect).
- **Crawl4AI**: Async JS crawl, JSON extract.
- **Web3**: Multi-RPC connect, contract call, wallet sign, gas sim.

Use: `from lola.libs import LLMProxy`—config-driven.


## Core: Orchestration Engine
- **State**: Pydantic model for messages/tool_results (validate/serialize with config max_messages).
- **Graph**: LOLAStateGraph for async workflows (supervision/reflection via phase 2 adapter).
- **Memory**: JSON persistence (StateManager), LLM entity/summary (ConversationMemory).
- **Agent**: BaseAgent with call_llm/graph run/bind_tools (abstract run for templates).

Use: `from lola.core import BaseAgent, LOLAStateGraph`—config-driven limits/LLM.


## Chains: EVM Abstractions
- **Connection**: Multi-RPC pooling/switch (config.evm_rpcs), retries.
- **Contract**: ABI load/call (read-only, from file/str).
- **Wallet**: Balance/sign (eth-account, SecretStr key).
- **KeyManager**: Load/validate key from config (no log reveal).
- **Utils**: Gas est/sim call (dry-run reverts).

Use: `from lola.chains import Web3Connection, LOLAWallet`—config-driven chains.

## Tools: Base and Web/Onchain Plugins
- **BaseTool**: ABC for execute/validate/bind (agent tools list).
- **WebCrawlTool**: Async crawl with selectors/JSON/Markdown (Crawl4AI, config timeout).
- **ContractCallTool**: EVM read call (via phase 4 contract, config ABI/address).
- **TransactTool**: EVM TX send with sim/gas (via phase 4 wallet/utils, config chain).
- **OnchainUtils**: gas_helper/simulate_tx (via phase 4).

Use: `from lola.tools import BaseTool, WebCrawlTool`—bind to agent.tools for graph.

Next: Phase 6 agents use tools in templates (e.g., ReAct loop).