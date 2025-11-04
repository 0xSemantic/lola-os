# Integration Guide

Integrate LOLA OS with external systems, from beginner setup to advanced customizations.

## Beginner: LLM Providers
1. Edit `config.yaml`:
   ```yaml
   llm_model: openai/gpt-4o
   ```
2. Add key to `.env`:
   ```text
   OPENAI_API_KEY=your_openai_key
   ```
3. Run agent to test switch.

## Intermediate: Blockchain Chains
1. Add RPCs in `config.yaml`:
   ```yaml
   evm_rpcs:
     polygon: https://polygon-rpc.com
     arbitrum: https://arbitrum-mainnet.infura.io/v3/your_key
   ```
2. Use in tool:
   ```python
   tool = ContractCallTool(chain="polygon")
   ```
3. Exercise: Switch chains in agent prompt.

## Advanced: Custom Tools/Libs
1. Extend Tool:
   ```python
   class CustomTool(BaseTool):
       def execute(self, **kwargs):
           # Custom logic
           return "Result"
   ```
2. Integrate lib:
   ```python
   from lola.libs.litellm.proxy import LLMProxy
   llm = LLMProxy(model="custom-model")
   ```
3. Deploy: Use LOLA in FastAPI:
   ```python
   from fastapi import FastAPI
   from lola import ReActAgent

   app = FastAPI()
   agent = ReActAgent()

   @app.post("/run")
   def run_agent(query: str):
       state = agent.run(query)
       return {"response": state.messages[-1]["content"]}
   ```

## Troubleshooting
- Provider error? Check keys in `.env`.
- Chain fail? Verify RPC URLs.

## Best Practices
- Use fallbacks in LLMProxy for reliability.
- Secure RPCs with API keys.

## Next Steps
- API Reference for module details.
- Examples for real-world integrations.
