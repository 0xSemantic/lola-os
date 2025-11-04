# Tutorial: Building Your First Agent

From zero to custom agent: A step-by-step guide for beginners, with advanced tips.

## Beginner: Scaffold and Run
1. Scaffold:
   ```bash
   poetry run lola create my_agent --template react
   cd my_agent
   ```
2. Configure `.env` with GEMINI_API_KEY.
3. Run:
   ```bash
   poetry run lola run --query "Crawl example.com and summarize"
   ```
- What happened? Agent reasoned, crawled the site, summarized using Gemini.

## Intermediate: Customize
1. Add tool in `agent.py`:
   ```python
   from lola.tools.onchain.contract_call import ContractCallTool
   self.bind_tools([ContractCallTool()])
   ```
2. Run with EVM query:
   ```bash
   poetry run lola run --query "Read balance on Sepolia"
   ```
3. Exercise: Edit `_build_prompt` to customize LLM instructions.

## Advanced: Extend Logic
1. Add multi-turn in `run`:
   ```python
   history = self.memory.summarize_history(state.messages)
   prompt = f"History: {history}\n{self._build_prompt(state)}"
   ```
2. Handle errors:
   ```python
   try:
       tool_result = self._execute_tool(action)
   except Exception as e:
       tool_result = f"Error: {str(e)}"
       logger.error("Tool error", extra={"tool": action["tool"], "error": str(e)})
   ```
3. Deploy as script: Add `if __name__ == "__main__": main()` for standalone run.

## Troubleshooting
- Tool fail? Check inputs in `execute`.
- Loop error? Reduce `max_turns` in `__init__`.

## Best Practices
- Use structured JSON for parsing.
- Test with different LLMs (change `config.yaml`).
- Log extra fields for debugging.

## Next Steps
- Try onchain_tools tutorial for blockchain tasks.
- Build a conversational agent.