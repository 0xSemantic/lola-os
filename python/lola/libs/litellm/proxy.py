# Standard imports
import typing as tp
from typing import Optional, Dict

# Third-party imports
from litellm import completion, model_cost

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Proxy for LiteLLM with LOLA routing, fallback, and cost estimation.

Purpose: Provides provider-agnostic LLM calls with Gemini default, fallback on error, and cost tracking.
How: Wraps litellm.completion with config model, tries fallbacks, estimates cost via model_cost.
Why: Ensures reliability/sovereignty in V1 (switch providers via config, no lock-in).
Full Path: lola-os/python/lola/libs/litellm/proxy.py
"""

logger = setup_logger("lola.litellm")

class LLMProxy:
    """LLMProxy: LiteLLM wrapper for LOLA. Does NOT handle streaming—use completion(stream=True) if needed."""

    def __init__(self, model: Optional[str] = None, fallbacks: Optional[tp.List[str]] = None):
        """
        Initialize LLMProxy with model and fallbacks.

        Args:
            model: Primary model (e.g., "gemini/gemini-1.5-flash"; loads from config if None).
            fallbacks: List of fallback models (default: ["openai/gpt-4o-mini"]).

        Does Not: Validate API keys—assume config has them.
        """
        config = load_config()
        self.model = model or config.llm_model
        self.fallbacks = fallbacks or ["openai/gpt-4o-mini", "anthropic/claude-3-haiku"]
        self.api_key = config.gemini_api_key.get_secret_value() if config.gemini_api_key else None
        logger.info("LLMProxy init", extra={"model": self.model, "fallbacks": len(self.fallbacks)})

    def complete(self, prompt: str, max_tokens: int = 1000, **kwargs) -> str:
        """
        Completes prompt via LiteLLM with fallback.

        Args:
            prompt: Input prompt.
            max_tokens: Max output tokens (default: 1000).
            **kwargs: Passed to completion (e.g., temperature).

        Returns:
            Response content string.

        Does Not: Handle non-text outputs—assumes chat completion.
        """
        models_to_try = [self.model] + self.fallbacks
        for model in models_to_try:
            try:
                # Inline: Set API key if Gemini (LiteLLM auto for others)
                if "gemini" in model and self.api_key:
                    kwargs["api_key"] = self.api_key  # Temp override for Gemini
                response = completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    **kwargs
                )
                content = response.choices[0].message.content
                cost = model_cost(model=model, num_tokens=max_tokens) or 0
                logger.info("LLM complete success", extra={"model": model, "tokens": max_tokens, "cost_usd": cost})
                return content
            except Exception as e:
                logger.warning("LLM fail, trying fallback", extra={"model": model, "error": str(e)})
                continue
        raise RuntimeError(f"All models failed: {models_to_try}")

    def cost_estimate(self, model: str, tokens: int) -> float:
        """
        Estimates cost for model/tokens.

        Args:
            model: Model name.
            tokens: Token count.

        Returns:
            Estimated USD cost.

        Does Not: Account for input tokens—output only.
        """
        cost = model_cost(model=model, num_tokens=tokens) or 0
        logger.debug("Cost estimate", extra={"model": model, "tokens": tokens, "cost_usd": cost})
        return cost

__all__ = ["LLMProxy"]