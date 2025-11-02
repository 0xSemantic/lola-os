# API Reference (Auto-Gen Stub - Phase 8 Full)

## lola.core.state
- `State`: Model with messages/tool_results/timestamp (to_json/from_json, validate_messages).

## lola.core.graph
- `LOLAStateGraph`: Extend with add_node/edge/execute(async).

## lola.core.memory
- `StateManager`: save/load JSON.
- `ConversationMemory`: extract_entities/summarize_history (LLMProxy).

## lola.core.agent
- `BaseAgent`: init/bind_tools/run/call_llm (abstract run).

Docstrings: Inline Args/Returns.


## lola.chains.connection
- `Web3Connection`: Init/switch_chain (config RPCs).

## lola.chains.contract
- `LOLAContract`: Init/call (ABI load).

## lola.chains.wallet
- `LOLAWallet`: balance/sign_tx (config key).

## lola.chains.key_manager
- `KeyManager`: load_key (validate SecretStr).

## lola.chains.utils
- `gas_estimate`: Estimate TX gas.
- `simulate_call`: Dry-run TX.

Docstrings: Inline Args/Returns.


## lola.tools.base
- `BaseTool`: init/execute/validate/bind_to_agent (abstract execute).

## lola.tools.web_crawl
- `WebCrawlTool`: execute (async crawl via config timeout/retries).

## lola.tools.onchain.contract_call
- `ContractCallTool`: execute (call via phase 4 contract).

## lola.tools.onchain.transact
- `TransactTool`: execute (TX sim/sign/broadcast via phase 4 wallet).

## lola.tools.onchain.utils
- `gas_helper`: Estimate via phase 4.
- `simulate_tx`: Dry-run via phase 4.

Docstrings: Inline Args/Returns.