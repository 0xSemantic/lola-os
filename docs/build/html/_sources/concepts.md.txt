# Core Concepts

Build a strong foundation with LOLA OS components. This guide progresses from beginner explanations to advanced usage.

## Beginner: Overview
LOLA OS is like an operating system for AI agents on blockchain. Key parts:
- **Agents**: The "brains" that reason and act (e.g., ReAct for loop-based reasoning).
- **Tools**: Plugins for actions (e.g., web crawl, EVM call).
- **Chains**: Blockchain connections (e.g., multi-RPC for Ethereum chains).
- **Libs**: Adapters for external libraries (e.g., LiteLLM for LLMs).
- **Core**: Orchestration (state, graph, memory for workflows).
- **CLI**: Command-line for scaffolding/running.
- **Utils**: Config/logging for setup.

## Intermediate: Deep Dive
- **BaseAgent**: Abstract class for all agents. Extend it:
  ```python
  class MyAgent(BaseAgent):
      def run(self, query: str) -> State:
          # Custom logic
          return State(messages=[{"role": "assistant", "content": "Response"}])
  ```
  - Bind tools: `agent.bind_tools([WebCrawlTool()])`.
- **StateGraph**: Build workflows:
  ```python
  graph = LOLAStateGraph()
  graph.add_node("step1", lambda state: state)
  graph.add_edge("__start__", "step1")
  graph.add_edge("step1", END)
  state = asyncio.run(graph.execute({"messages": []}))
  ```
- **Memory**: Manage context:
  ```python
  memory = ConversationMemory(LLMProxy())
  summary = memory.summarize_history([{"role": "user", "content": "Hello"}])
  ```
- **Tools/Chains**: EVM example:
  ```python
  tool = ContractCallTool()
  result = tool.execute(contract_address="0x...", function_name="balanceOf", args=["0x..."])
  ```
- **CLI**: Scaffold and run:
  ```bash
  lola create my_agent --template react
  lola run --query "Test"
  ```

## Advanced: Customization
- Extend agents for custom workflows (e.g., add RAG in future).
- Configure multi-chain: Edit `config.yaml` for RPCs.
- Integrate libs: Switch LLM providers in LiteLLM proxy.
- Error handling: Use logger for traceability.
- Performance: Use async for concurrent tools.

## Best Practices
- Start simple: Use ReAct for most tasks.
- Secure keys: Always use SecretStr for private_key.
- Test locally: Use Sepolia testnet, free Gemini.

## Troubleshooting
- Import error? Check `__init__.py` exports.
- LLM fail? Verify API key in `.env`.
- EVM error? Check RPC URLs in config.

## Next Steps
- Tutorials for hands-on practice.
- API Reference for module details.