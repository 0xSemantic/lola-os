# Integration Guide: Keys & Config (V1)

## API Keys
- **Gemini**: Free tier [here](https://aistudio.google.com). .env: `GEMINI_API_KEY=sk-...`
- **EVM RPCs**: Free Infura/Alchemy. YAML: `evm_rpcs: {sepolia: "https://..."}`
- **Private Key**: Testnet only! Validate: 0x64hex.

## Config Flow
load_config() → YAML defaults → .env secrets → env overrides → Validate.

Example: Switch model: `os.environ["LLM_MODEL"] = "openai/gpt-4o-mini"`.

Best: .gitignore .env; use direnv for auto-load.