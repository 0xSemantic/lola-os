# Changelog (V1 Phases)

## v1.0.0-alpha.1 (Phase 1 - 2025-11-01)
- Add utils: Config (Pydantic/SecretStr), Logging (JSON/rotation).
- Tests: 100% pass, real overrides.
- Examples: 2 (standalone/combined).

## v1.0.0-alpha.2 (Phase 2 - 2025-11-02)
- Add libs: LangGraph supervise, LiteLLM proxy, Crawl4AI wrap, web3 adapters.
- Tests: 8 pass, real/mocked.
- Examples: 2 (standalone/combined).

## v1.0.0-alpha.3 (Phase 3 - 2025-11-02)
- Add core: State (Pydantic/validate), Graph (async/supervision), Memory (JSON/LLM extract), BaseAgent (call_llm/graph).
- Tests: 6 pass, real/mocked LLM.
- Examples: 2 (standalone/combined).

## v1.0.0-alpha.4 (Phase 4 - 2025-11-02)
- Add chains: Connection (multi-RPC), Contract (ABI/call), Wallet (balance/sign), KeyManager (secure load), Utils (gas/sim).
- Tests: 8 pass, mocked web3 for unit, real structure.
- Examples: 2 (standalone/combined).

## v1.0.0-alpha.5 (Phase 5 - 2025-11-02)
- Add tools: BaseTool (validate/bind), WebCrawlTool (async extract), ContractCallTool/TransactTool (read/write), onchain utils (gas/sim).
- Tests: 8 pass, mocked crawl/broadcast, real structure.
- Examples: 2 (standalone/combined).

## v1.0.0-alpha.6 (Phase 6 - 2025-11-02)
- Add agents: BaseAgent extend, ReAct (loop), PlanExecute (plan/graph), Conversational (memory).
- Tests: 8 pass, mocked LLM/tool, real structure.
- Examples: 2 (standalone/combined).

## v1.0.0-alpha.6 (Phase 6 - 2025-11-02)
Version 1.0 - TMVP1. Phase 7 complete: CLI ready. Run `lola --help` for commands.
Quickstart: lola create my_agent && cd my_agent && lola run --query "Test"