# Standard imports
from typing import Optional, Dict 

# Third-party imports
from eth_account import Account
from web3 import Web3

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger
from .connection import Web3Connection

"""
File: Web3 wallet adapter for LOLA balance/signing.

Purpose: Manages EVM wallets with private key from config.
How: Uses eth-account for signing, Web3Connection for balance/TX build.
Why: Secure signing for V1 transact tools (SecretStr key).
Full Path: lola-os/python/lola/libs/web3/wallet.py
"""

logger = setup_logger("lola.web3.wallet")

class LOLAWallet:
    """LOLAWallet: EVM wallet adapter. Does NOT broadcast TX—use transact.py."""

    def __init__(self, private_key: Optional[str] = None, connection: Optional[Web3Connection] = None):
        """
        Initialize LOLAWallet.

        Args:
            private_key: Hex key (loads from config if None).
            connection: Web3Connection (default).

        Does Not: Validate chain—assume connected.
        """
        config = load_config()
        pk = private_key or config.evm_private_key.get_secret_value() if config.evm_private_key else None
        if not pk:
            raise ValueError("No private key provided")
        self.account = Account.from_key(pk)
        self.connection = connection or Web3Connection()
        logger.info("LOLAWallet init", extra={"address": self.account.address})

    def balance(self) -> int:
        """
        Gets wallet balance in wei.

        Returns:
            Balance wei.

        Does Not: Convert units—use w3.from_wei.
        """
        balance = self.connection.w3.eth.get_balance(self.account.address)
        logger.debug("Balance fetched", extra={"wei": balance})
        return balance

    def sign_tx(self, tx_dict: Dict) -> str:
        """
        Signs transaction dict.

        Args:
            tx_dict: Unsigned TX (e.g., {"to": addr, "value": wei, "gas": 21000}).

        Returns:
            Signed TX hex.

        Does Not: Estimate gas—pre-populate.
        """
        signed = self.connection.w3.eth.account.sign_transaction(tx_dict, self.account.key)
        logger.info("TX signed", extra={"tx_hash": signed.hash.hex()[:10]})
        return signed.rawTransaction.hex()

__all__ = ["LOLAWallet"]