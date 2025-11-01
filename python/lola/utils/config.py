# Standard imports
import os
from typing import Dict, Optional
from pathlib import Path

# Third-party imports
from dotenv import load_dotenv
import yaml
from pydantic import BaseModel, SecretStr, field_validator, ValidationError

"""
File: Defines the configuration management for LOLA OS, handling .env, YAML, and environment variable overrides.

Purpose: Centralizes loading and validation of settings like LLM models, API keys, and EVM RPCs, ensuring secure handling of secrets.
How: Loads .env first for overrides, then YAML for defaults, validates with Pydantic (SecretStr for keys), and raises clear errors.
Why: Promotes developer sovereignty by allowing flexible configs without lock-in, foundational for all phases per LOLA's phased rollout.
Full Path: lola-os/python/lola/utils/config.py
"""

class Config(BaseModel):
    """Config: Pydantic model for LOLA OS settings. Does NOT load sources automatically—use load_config()."""

    llm_model: str = "gemini/gemini-1.5-flash"
    """Default LLM model for LiteLLM routing."""

    gemini_api_key: Optional[SecretStr] = None
    """Gemini API key (SecretStr for masking)."""

    evm_rpcs: Dict[str, str] = {}
    """EVM RPC URLs by chain (e.g., {'ethereum': 'https://...'})."""

    evm_private_key: Optional[SecretStr] = None
    """Private key for EVM signing (SecretStr)."""

    config_file: str = "config.yaml"
    """Path to YAML config file."""

    @field_validator("evm_rpcs")
    @classmethod
    def validate_rpcs(cls, v):
        """Validate RPC dict has valid URLs if provided."""
        if not v:
            return v
        for chain, url in v.items():
            if not url.startswith(("http://", "https://")):
                raise ValueError(f"Invalid RPC URL for {chain}: {url}")
        return v

    @field_validator("evm_private_key")
    @classmethod
    def validate_private_key(cls, v):
        """Basic hex validation for private key."""
        if v is None:
            return v
        pk_str = v.get_secret_value()
        if not (pk_str.startswith("0x") and len(pk_str) == 66 and all(c in '0123456789abcdefABCDEF' for c in pk_str[2:])):
            raise ValueError("Invalid private key format: must be 0x-prefixed 64-hex chars.")
        return v

def load_config(config_path: Optional[str] = None) -> Config:
    """
    Loads configuration from .env (override), YAML (defaults), and os.environ (final override).

    Args:
        config_path: Optional path to YAML file; defaults to 'config.yaml'.

    Returns:
        Validated Config instance.

    Does Not: Handle non-standard formats—use YAML/ENV only.
    """
    # Inline: Load .env for secrets/overrides
    load_dotenv()

    config_path = config_path or Path.cwd() / "config.yaml"
    yaml_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            yaml_data = yaml.safe_load(f) or {}

    # Inline: Merge os.environ last for runtime overrides (uppercased keys)
    env_data = {}
    for field in Config.model_fields:
        env_val = os.getenv(field.upper())
        if env_val:
            env_data[field] = env_val
    all_data = {**yaml_data, **env_data}

    try:
        return Config.model_validate(all_data)
    except ValidationError as e:
        raise ValueError(f"Config validation failed: {e}") from e

__all__ = ["Config", "load_config"]