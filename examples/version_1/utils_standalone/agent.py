#!/usr/bin/env python
"""
Standalone example: Load config and log a message using LOLA utils.
Run: python agent.py
Expected: JSON log with config values (secrets masked).
"""

# Local imports (add parent to path for demo)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "python"))

from lola.utils.config import load_config
from lola.utils.logging import setup_logger

if __name__ == "__main__":
    # Load config (uses .env.sample if present)
    config = load_config()
    logger = setup_logger()

    logger.info(
        "Utils standalone demo",
        extra={
            "llm_model": config.llm_model,
            "has_key": bool(config.gemini_api_key),
            "chains_count": len(config.evm_rpcs),
        },
    )
    print(f"Config loaded: Model={config.llm_model}, Chains={len(config.evm_rpcs)}")
    print("Check lola.log for JSON output.")