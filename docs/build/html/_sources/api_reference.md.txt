# API Reference

Full documentation of LOLA OS modules, classes, and functions.

## Utils
- `Config`: Pydantic model for configuration.
- `load_config()`: Loads config from .env/yaml.
- `setup_logger()`: Configures structured logger.

## Libs
- `LLMProxy`: Provider-agnostic LLM caller.
- `SupervisedStateGraph`: Extended LangGraph with supervision.

## Core
- `BaseAgent`: Abstract agent base.
- `LOLAStateGraph`: Workflow graph.
- `State`: Agent state model.
- `ConversationMemory`: History summarization.

## Agents
- `ReActAgent`: Reasoning-action loop.
- `PlanExecuteAgent`: Planning and execution.
- `ConversationalAgent`: Multi-turn conversation.

## Tools
- `BaseTool`: Abstract tool base.
- `WebCrawlTool`: Web extraction.
- `ContractCallTool`: EVM read.
- `TransactTool`: EVM write.

## Chains
- `Web3Connection`: RPC connection.
- `LOLAContract`: Contract interaction.
- `LOLAWallet`: Wallet management.
- `KeyManager`: Key loading.

Generated with Sphinx autodoc—run `make html` in docs/ to view.