# Standard imports
import sys
from pathlib import Path

# Third-party imports
# None (Poetry deps)

# Local imports
from lola.libs.litellm.proxy import LLMProxy
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Standalone script for LiteLLM proxy Gemini call demo.

Purpose: Demonstrates LLMProxy routing/fallback/cost in isolation for onboarding.
How: Loads config, inits proxy, completes prompt, logs/prints response.
Why: Teaches V1 LLM integration without full agent—zero-mastery entry.
Full Path: lola-os/examples/version_1/libs_standalone/agent.py
"""

if __name__ == "__main__":
    # Inline: Load config for model/key
    config = load_config()
    logger = setup_logger()
    proxy = LLMProxy(config.llm_model)
    response = proxy.complete("What is LOLA OS?")
    logger.info("Standalone LLM demo", extra={"response_len": len(response)})
    print(f"Gemini response: {response[:100]}...")
    print("Cost est:", proxy.cost_estimate(config.llm_model, 100))