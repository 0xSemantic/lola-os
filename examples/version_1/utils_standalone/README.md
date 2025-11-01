# Utils Standalone: Config + Logging Basics (LOLA OS V1 Example)

## Overview
This zero-mastery demo shows LOLA's utils in isolation: Load config (YAML defaults, .env/env overrides, SecretStr secrets) and log structured JSON (console/file, rotation). Why? Foundational for agents—see Gemini default, masked keys. No EVM/LLM yet (Phase 2+). Run time: <1min. Output: JSON log + print.

## Prerequisites
- Python 3.12+ (install via pyenv/brew).
- Poetry (pip install poetry) for deps—leverages free Gemini tier, no paid keys needed for this.
- Git (optional: clone repo).
- No blockchain setup—pure utils.

## Setup (2min)
1. `cd examples/version_1/utils_standalone`
2. `cp .env.sample .env` (gitignores .env—never commit secrets!).
3. Edit `.env`: Get free GEMINI_API_KEY at [Google AI Studio](https://aistudio.google.com/app/apikey). Add testnet EVM_PRIVATE_KEY (e.g., from MetaMask export, Sepolia faucet). Skip if testing defaults.
4. `poetry install` (pulls pydantic/dotenv/yaml from pyproject.toml).
5. Edit `config.yaml` if desired (e.g., change model—YAML for dev defaults).

Best practice: Use .env for secrets/RPCs (overrides YAML), os.environ for CI (e.g., GitHub Actions secrets).

## Run (10s)
`python agent.py`

**Expected Output:**
Config loaded: Model=gemini/gemini-1.5-flash, Chains=1
Check lola.log for JSON output.

Console/log (`lola.log`): `{"timestamp": "2025-11-01T...", "level": "INFO", "message": "Utils standalone demo", "extra": {"llm_model": "gemini/gemini-1.5-flash", "has_key": true, "chains_count": 1, "process_id": 12345}}`

If no key: `has_key: false` (graceful—V1 fallbacks in Phase 2).

## Walkthrough (Line-by-Line)
1. `sys.path.insert(0, ...)`: Adds repo root for imports (demo hack; use `pip install -e .` in prod).
2. `load_config()`: Loads YAML → .env/env, validates (e.g., hex key? Error: "Invalid private key...").
3. `setup_logger()`: Wires JSON (extras like model), rotates at 10MB (check handler props).
4. `logger.info(..., extra=...)`: Structured—secrets masked (str(key) = '***sk-123').
5. Print: Quick feedback.

**Exercise 1:** Override model. Edit `.env`: `LLM_MODEL=anthropic/claude-3-haiku`. Rerun—see "anthropic/..." in log/print. Why? Env beats YAML for prod flexibility.
**Exercise 2:** Break validation. Set `EVM_PRIVATE_KEY=invalid` in .env. Rerun—ValueError. Fix: Use real 0x64hex. Teaches secure key handling.

## Troubleshooting
- **ImportError?** Run from repo root: `PYTHONPATH=python python examples/.../agent.py`.
- **Key error ("Config validation failed")?** Check .env format (no quotes for keys). For Gemini: Signup free, rate limit? Wait 60s.
- **No log file?** Perms: Run in writable dir. Rotation not triggering? Logs <10MB—normal.
- **YAML parse fail?** Indent error—use 2 spaces, no tabs.

Common pit: Committing .env—add to .gitignore! Test: `git status` (should ignore).

## Best Practices
- Secrets: Always SecretStr—logs mask, but get_secret_value() for use (e.g., Phase 4 wallet).
- Overrides: YAML=dev defaults, .env=local secrets, env=CI/prod (no files).
- Logging: Extras for traces (e.g., {"agent_id": 42})—enables V2 monitoring hooks.
- Validation: Custom @field_validator prevents bad RPCs/keys early.

## Next Steps
- Customize: Add field to Config (e.g., `debug: bool = True`), update model_validate.
- Integrate: See utils_combined/ for "agent" stub. Then Phase 2: Add LiteLLM to config.
- Extend: Fork, PR to repo. Questions? [GitHub Issues](https://github.com/lola-os/open-core/issues).

Files:
- `agent.py`: Main runnable.
- `config.yaml`: Defaults.
- `requirements.txt`: Empty (Poetry).
- `.env.sample`: Template (fill!).
- README.md: This guide.

Build on-chain agents with LOLA—V1 hooks you in! 🚀