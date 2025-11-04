# Tutorial: On-Chain Tools

From basic EVM read to advanced transactions: Guide for all levels.

## Beginner: Read Balance
1. Scaffold:
   ```bash
   poetry run lola create chain_agent --template plan_execute
   cd chain_agent
   ```
2. Configure `.env` with PRIVATE_KEY and EVM_RPC_SEPOLIA.
3. Run:
   ```bash
   poetry run lola run --query "Read my balance on Sepolia"
   ```
- What happened? Agent planned, called ContractCallTool, returned balance.

## Intermediate: Contract Call
1. Add tool in `agent.py`:
   ```python
   from lola.tools.onchain.contract_call import ContractCallTool
   self.bind_tools([ContractCallTool()])
   ```
2. Run with contract query:
   ```bash
   poetry run lola run --query "Call ERC20 balanceOf on Sepolia"
   ```
3. Exercise: Add ABI in `config.yaml` for custom contracts.

## Advanced: Transaction
1. Add TransactTool:
   ```python
   from lola.tools.onchain.transact import TransactTool
   self.bind_tools([TransactTool()])
   ```
2. Run with write query:
   ```bash
   poetry run lola run --query "Transfer 0.1 ETH on Sepolia"
   ```
3. Customize simulation:
   ```python
   from lola.tools.onchain.utils import simulate_call
   result = simulate_call(tx_data)
   ```
4. Handle multi-chain: Add RPCs in `config.yaml`, switch in prompt.

## Troubleshooting
- TX fail? Check gas in utils.py.
- Key invalid? Use SecretStr in `.env`.

## Best Practices
- Always simulate TX before broadcast.
- Use testnet for development.
- Log TX hashes for tracing.

## Next Steps
- Combine with web tools for hybrid agents.
- Explore advanced examples in `examples/version_1/advanced/`.