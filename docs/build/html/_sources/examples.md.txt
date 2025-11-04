# Examples
LOLA OS includes 24 examples in `examples/version_1/` (8 easy, 8 moderate, 8 advanced). Each has a `README.md` guiding from setup to advanced customization.
## Easy Examples
1. **01_web_crawler**: Simple web crawling.
2. **02_contract_reader**: Reading EVM contract data.
3. **03_transact**: Sending simple EVM transactions.
4. **04_conversational**: Basic conversational tasks with memory.
5. **05_react_basic**: Basic ReAct loop for web crawling.
6. **06_plan_execute**: Basic plan-execute loop for web crawling.
7. **07_gas_estimator**: Estimating gas costs for EVM transactions.
8. **08_wallet_checker**: Checking wallet balances on Sepolia.
## Moderate Examples
1. **01_web_contract_combo**: Combining web crawling and EVM contract reads.
2. **02_transact_with_check**: Checking balance before sending transactions.
3. **03_conversational_with_tools**: Conversational tasks with web crawling tools.
4. **04_plan_transact**: Planning and executing EVM transactions.
5. **05_wallet_monitor**: Monitoring wallet balance changes.
6. **06_gas_aware_transact**: Sending transactions with gas estimation.
7. **07_stateful_conversation**: Stateful conversations with web tool support.
8. **08_contract_simulator**: Simulating EVM contract calls.
## Advanced Examples
1. **01_multi_tool_orchestrator**: Orchestrating web crawling, contract reads, and transactions.
2. **02_dynamic_contract_interactor**: Dynamic planning, simulation, and execution of contract interactions.
3. **03_wallet_analytics**: Analyzing wallet balance and contract interactions.
4. **04_web_blockchain_integrator**: Integrating web data with blockchain transactions.
5. **05_stateful_multi_agent**: Coordinating multiple agents for web and contract tasks.
6. **06_gas_optimized_workflow**: Gas-optimized transaction planning and execution.
7. **07_conversational_blockchain**: Conversational tasks for blockchain contract calls and transactions.
8. **08_monitor_and_act**: Monitoring wallet balance and triggering transactions.


Run any example:
```bash
cd examples/version_1/easy/01_web_crawler
poetry install
poetry run python agent.py
```