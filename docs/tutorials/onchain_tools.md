# Tutorial: On-Chain Tools with Libs (Phase 2)

1. Import: `from lola.libs.web3 import Web3Connection, LOLAWallet`
2. Conn: `conn = Web3Connection("sepolia")`
3. Wallet: `wallet = LOLAWallet()`; `balance = wallet.balance()`
4. Log: Uses utils logger.

Exercise: Sim TX gas with utils/gas_estimate.