# Tutorial: On-Chain Tools with Libs (Phase 2)

1. Import: `from lola.libs.web3 import Web3Connection, LOLAWallet`
2. Conn: `conn = Web3Connection("sepolia")`
3. Wallet: `wallet = LOLAWallet()`; `balance = wallet.balance()`
4. Log: Uses utils logger.

Exercise: Sim TX gas with utils/gas_estimate.

# Tutorial: On-Chain Tools with Chains (Phase 4)

1. Import: `from lola.chains import Web3Connection, LOLAContract, LOLAWallet`
2. Connection: `conn = Web3Connection("sepolia")`
3. Contract: `abi = [...]; contract = LOLAContract(addr, abi, conn); balance = contract.call("balanceOf", addr)`
4. Wallet: `wallet = LOLAWallet(); balance = wallet.balance(); signed = wallet.sign_tx(tx)`
5. Utils: `gas = gas_estimate(conn, tx); sim = simulate_call(conn, tx)`

Exercise: Sim transfer TX, check revert if low balance.