# Tutorial: Build Your First "Agent" Stub (Phase 1 Utils)

1. Use utils_combined/agent.py as base.
2. Add: `config = load_config()` for model/key.
3. Log: `logger.debug("Agent init", extra={"model": config.llm_model})`.
4. Run/test: See extras in log.

Extend (Phase 6): Bind real agent.

Exercise: Add RPC log—`extra["rpcs"] = config.evm_rpcs.keys()`.