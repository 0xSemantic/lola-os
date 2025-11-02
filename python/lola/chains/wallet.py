# Standard imports
from typing import Optional, Dict
from eth_account import Account

# Third-party imports
from web3 import Web3

# Local imports
from lola.utils.config import load_config
from lola.utils.logging import setup_logger
from .connection import Web3Connection

"""
File: EVM wallet abstraction for LOLA with balance and signing.

Purpose: Manages wallet operations with private key from config, for balance and TX signing in V1.
How: Uses eth-account for signing, Web3Connection for balance, SecretStr for secure key load.
Why: Enables secure EVM writes in V1 tools/agents, no lock-in (config key/RPC).
Full Path: lola-os/python/lola/chains/wallet.py
"""

logger = setup_logger("lola.chains.wallet")

class LOLAWallet:
    """LOLAWallet: EVM wallet for balance and signing. Does NOT broadcast TX—use transact.py."""

    def __init__(self, private_key: Optional[str] = None, connection: Optional[Web3Connection] = None):
        """
        Initialize LOLAWallet with key and connection.

        Args:
            private_key: Hex private key (loads from config if None).
            connection: Web3Connection (default first chain).

        Does Not: Validate chain—assume connected.
        """
        config = load_config()
        pk = private_key or config.evm_private_key.get_secret_value() if config.evm_private_key else None
        if not pk:
            raise ValueError("No private key provided; set EVM_PRIVATE_KEY in .env or pass private_key.")
        self.account = Account.from_key(pk)
        self.connection = connection or Web3Connection()
        logger.info("LOLAWallet init", extra={"address": self.account.address})

    def balance(self) -> int:
        """
        Gets wallet balance in wei.

        Returns:
            Balance in wei.

        Does Not: Convert units—use w3.from_wei for ETH.
        """
        balance = self.connection.w3.eth.get_balance(self.account.address)
        logger.debug("Wallet balance fetched", extra={"wei": balance})
        return balance

    def sign_tx(self, tx_dict: Dict) -> bytes:
        """
        Signs transaction dict for broadcast.

        Args:
            tx_dict: Unsigned TX (e.g., {"to": addr, "value": wei, "gas": 21000, "nonce": int, "data": bytes}).

        Returns:
            Signed TX bytes.

        Does Not: Estimate gas/nonce—pre-populate or use utils.
        """
        signed = self.connection.w3.eth.account.sign_transaction(tx_dict, self.account.key)
        logger.info("TX signed", extra={"tx_hash": signed.hash.hex()[:10]})
        return signed.rawTransaction

__all__ = ["LOLAWallet"]