# Standard imports
from typing import Optional
from pathlib import Path

# Third-party imports
from eth_account import Account

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger

"""
File: Key manager for LOLA EVM private keys with secure load and validation.

Purpose: Loads and validates private keys from .env/config, logs access without revealing, for wallet use in V1.
How: Uses config SecretStr for load, eth-account for validation (hex format), logs masked.
Why: Ensures secure, sovereign key handling in V1, no lock-in (config load), prevents invalid keys early.
Full Path: lola-os/python/lola/chains/key_manager.py
"""

logger = setup_logger("lola.chains.key_manager")

class KeyManager:
    """KeyManager: Secure EVM private key loader/validator. Does NOT store keys—load once for wallet."""

    @staticmethod
    def load_key() -> str:
        """
        Loads and validates private key from config.

        Returns:
            Valid hex private key string.

        Does Not: Cache—load per use for security.
        """
        config = load_config()
        if not config.evm_private_key:
            raise ValueError("No EVM private key in config; set EVM_PRIVATE_KEY in .env.")
        pk_str = config.evm_private_key.get_secret_value()
        if not (pk_str.startswith("0x") and len(pk_str) == 66 and all(c in '0123456789abcdefABCDEF' for c in pk_str[2:])):
            raise ValueError("Invalid private key format: must be 0x-prefixed 64-hex chars.")
        # Inline: Optional: Validate by deriving address (no sign needed)
        try:
            Account.from_key(pk_str)
        except ValueError as e:
            raise ValueError(f"Invalid private key: {e}") from e
        logger.info("Private key loaded and validated", extra={"length": len(pk_str), "masked": pk_str[:10] + "..."})  # No full log
        return pk_str

__all__ = ["KeyManager"]