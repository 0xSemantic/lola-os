#!/usr/bin/env python
"""
Combined example: Stub "agent" using config + logging (e.g., "load settings, log run").
Extends standalone: Simulates agent init/log with config-driven extras.
Run: python agent.py
Expected: JSON log with full config extras (masked secrets).
"""

# Local imports (add parent to path for demo)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "python"))

from lola.utils.config import load_config
from lola.utils.logging import setup_logger

if __name__ == "__main__":
    config = load_config()
    logger = setup_logger(name="lola.agent")

    # Stub agent "run": Log with config extras (masks keys)
    logger.info(
        "Stub agent run: Config loaded and ready",
        extra={
            "model": config.llm_model,
            "api_key_set": bool(config.gemini_api_key),
            "private_key_set": bool(config.evm_private_key),
            "rpc_chains": list(config.evm_rpcs.keys()),
            "session_id": "demo-001",
        },
    )
    print(f"Stub agent: Model={config.llm_model}, Chains={config.evm_rpcs.keys()}")
    print("Full trace in lola.log (JSON with extras).")