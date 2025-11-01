# Utils Combined: Config + Logging in "Agent" Stub (LOLA OS V1 Example)

## Overview
Builds on standalone: A minimal "agent" stub that loads config, sets up logger, and "runs" with extras (e.g., chains list, session ID). Demonstrates integration—secrets masked, overrides work. Why? Previews V3+ agents using utils. Run time: <1min. Output: JSON log extras + print.

## Prerequisites
Same as standalone: Python 3.12+, Poetry, free Gemini key. No extras.

## Setup (2min)
1. `cd examples/version_1/utils_combined`
2. `cp .env.sample .env` & fill (Gemini key, testnet private key—faucet at sepoliafaucet.com).
3. `poetry install` (root pyproject.toml).
4. Tweak `config.yaml` (e.g., add RPC—YAML for multi-chain defaults).

Pro tip: .env for local (secrets), YAML for repo defaults (no commits!).

## Run (10s)
`python agent.py`

**Expected Output:**
Stub agent: Model=gemini/gemini-1.5-flash, Chains=dict_keys(['polygon', 'arbitrum'])
Full trace in lola.log (JSON with extras).

Log sample: `{"...": "...", "extra": {"model": "gemini/gemini-1.5-flash", "api_key_set": true, "private_key_set": true, "rpc_chains": ["polygon", "arbitrum"], "session_id": "demo-001", "process_id": 12345}}`

## Walkthrough (Line-by-Line)
1. Path hack: Enables imports (prod: `pip install -e .` from root).
2. `load_config()`: Merges YAML/.env/env—e.g., bad key? ValueError early.
3. `setup_logger("lola.agent")`: Namespaced, JSON extras (e.g., rpc_chains list).
4. `logger.info(..., extra=...)`: Structured trace—masks bool(private_key_set), no raw secrets.
5. Print: Human-readable summary.

**Exercise 1:** Override chain. Add to .env: `EVM_RPCS_POLYGON=https://new-rpc.com`. Rerun—see "polygon" in extras. Why? Dynamic multi-RPC for V1 interop.
**Exercise 2:** Simulate error. Remove key from .env, rerun—extras: {"api_key_set": false}. Extend: Add if not config.gemini_api_key: logger.warning("Key missing—fallback mode").

## Troubleshooting
- **Validation fail?** Private key not 0x64hex? Use tool like [eth-keyfile](https://pypi.org/project/eth-keyfile) gen. Error msg guides.
- **No extras in log?** Check JSON parse—use jq: `jq . lola.log`.
- **Dup handlers?** setup_logger cleans—rerun ok.
- **YAML multi-line?** Use | for blocks, but simple dict here.

Pitfall: Env keys UPPERCASE (LLM_MODEL)—Pydantic maps.

## Best Practices
- Extras: Dict for traces (V2 telemetry: export to OTEL). Avoid secrets—use bools/has_key.
- Levels: DEBUG for dev (change level="DEBUG"), INFO prod.
- Rotation: 10MB/5bk—scales to heavy agents (V6 Rust perf).
- Security: SecretStr everywhere—str() masks in logs/prints.

## Next Steps
- Customize: Add "debug" field to Config, log if true.
- Chain: utils_combined → Phase 3 core (graph uses logger).
- Explore: Standalone for utils-only tests; this for integration preview.

Files: Same as standalone, but agent.py stubs full flow.

LOLA: Sovereign from utils up. Feedback? PR away! 🌐