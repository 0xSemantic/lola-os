# Libs Combined: Crawl4AI + Web3 Read (LOLA OS V1 Example)

## Overview
Integrates libs: Crawl site + read wallet balance. Why? V1 agents bridge web/EVM. Run: <1min. Output: Content snippet + balance.

## Prerequisites
- Poetry.
- Infura/Alchemy RPC free, testnet key (Sepolia faucet).

## Setup
1. `cd examples/version_1/libs_combined`
2. `cp .env.sample .env` & fill RPC/key.
3. `poetry install`.

## Run
`python agent.py`

Expected: "Crawl: Example Domain..." + "Balance: 1000000000000000000 wei"

## Walkthrough
1. `LOLAWebCrawler()`: Async crawl with selector.
2. `Web3Connection()`: Multi-RPC from config.
3. `LOLAWallet()`: Balance from key.
4. Logs: "Crawl success", "Balance fetched".

**Exercise 1:** Switch chain. Edit config evm_rpcs polygon, rerun—balance on Polygon.
**Exercise 2:** Selector. Change css="h1", rerun—title only.

## Troubleshooting
- RPC fail? Check .env URL/key. Log: "Failed to connect".
- No balance? Faucet ETH. Key invalid? Validation error.

Best: Config RPCs for interop.

## Next Steps
Extend: Phase 5 tools use these. Add LLM summarize crawl.

Files: agent.py, config.yaml, .env.sample, README.