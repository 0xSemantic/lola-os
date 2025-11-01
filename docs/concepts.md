# Core Concepts (V1)

## Utils: Config & Logging
- **Config**: Pydantic + .env/YAML. Defaults: Gemini 1.5 Flash. Secrets: SecretStr (masked).
- **Logging**: JSON extras, rotation. Use: `logger.info(..., extra={"trace": id})`.

Why? Sovereign: Switch providers via config, no hardcodes.

Next: Libs adapters (LiteLLM routes).