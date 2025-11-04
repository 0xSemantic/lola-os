# Quickstart Guide

This guide takes you from zero to running your first LOLA OS agent in 10 minutes. No prior AI/blockchain experience required.

## Step 1: Prerequisites
- Python 3.12+ (download from python.org).
- Poetry (install with `pip install poetry`).
- Git (for cloning repo).
- Free Gemini API key (sign up at https://ai.google.dev and generate key).
- Optional: Sepolia testnet RPC (free from Alchemy at https://alchemy.com—create account, get Sepolia URL).

## Step 2: Install LOLA OS
1. Clone the repository:
   ```bash
   git clone https://github.com/0xSemantic/lola-os.git
   cd lola-os
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```

## Step 3: Configure
1. Copy sample env:
   ```bash
   cp examples/version_1/easy/01_web_qa_bot/.env.sample .env
   ```
2. Edit `.env` with your Gemini key:
   ```text
   GEMINI_API_KEY=your_gemini_key_here
   ```
3. For EVM examples, add to `.env`:
   ```text
   PRIVATE_KEY=your_testnet_private_key
   EVM_RPC_SEPOLIA=your_alchemy_sepolia_url
   ```

## Step 4: Run Your First Agent
1. Scaffold a project:
   ```bash
   poetry run lola create my_agent --template react
   cd my_agent
   ```
2. Run the agent:
   ```bash
   poetry run lola run --query "Crawl example.com and summarize"
   ```
   - Output: Agent response with summary from the site.

## Step 5: Understand What Happened
- `lola create`: Created a ReAct agent template with `agent.py`, `config.yaml`, `.env.sample`, and `README.md`.
- `lola run`: Loaded the agent, called `run("query")`, and outputted the state.
- The agent used Gemini LLM to reason and Crawl4AI to fetch data.

## Step 6: Customize
1. Edit `agent.py` to add a tool:
   ```python
   from lola.tools.onchain.contract_call import ContractCallTool
   agent.bind_tools([ContractCallTool()])
   ```
2. Rerun with a new query:
   ```bash
   poetry run lola run --query "Check balance on Sepolia"
   ```
3. Exercise: Add your own tool or change the LLM model in `config.yaml` to "openai/gpt-4o" (add OPENAI_API_KEY to `.env`).

## Troubleshooting
- Poetry install fail? Check Python version (`python --version`).
- LLM error? Verify `GEMINI_API_KEY` in `.env`.
- EVM error? Ensure PRIVATE_KEY and RPC URL are set.
- CLI not found? Run `poetry install` again.

## Best Practices
- Use testnet for EVM to avoid real funds.
- Secure keys—never commit `.env`.
- Log everything for debugging (`lola.log`).

## Next Steps
- Explore Concepts to understand components.
- Try Tutorials for advanced building.
- Run more examples in `examples/version_1/`.
- Contribute on GitHub!