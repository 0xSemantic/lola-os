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

# Tutorial: On-Chain Tools with Tools (Phase 5)

1. Import: `from lola.tools import WebCrawlTool, ContractCallTool, TransactTool`
2. Init: `crawl = WebCrawlTool(); call = ContractCallTool(); tx = TransactTool()`
3. Validate/Bind: `crawl.validate(url=...)["valid"]`; `crawl.bind_to_agent(agent)`
4. Execute: `result = crawl.execute(url="example.com")`; `balance = call.execute(address=..., abi=..., function_name="balanceOf", addr)`; `tx_hash = tx.execute(to=..., value=0)`
5. Utils: `gas = gas_helper("sepolia", tx)`; `sim = simulate_tx("sepolia", tx)`

Exercise: Bind to mock agent, execute chain: Crawl → call EVM via response → transact if balance >0.