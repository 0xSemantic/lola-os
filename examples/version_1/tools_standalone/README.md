# Tools Combined: WebCrawl + Onchain Call/Transact (LOLA OS V1 Example)

## Overview
Integrates tools: Base validate/bind, web crawl extract, onchain read/write. Why? Phase 5 full layer—off/onchain for V1. Run: <1min. Output: Crawl content/contract/tx_hash + log.

## Prerequisites
- Poetry.
- Infura RPC, testnet key (Sepolia).

## Setup
1. `cd examples/version_1/tools_combined`
2. `cp .env.sample .env` & fill RPC/key.
3. `poetry install`.

## Run
`python agent.py`

Expected: "Crawl: <p>This domain..." + "Contract call: 0" + "Transact: 0xhash..." (if key set; else skip onchain).

## Walkthrough
agent.py self-doc: Docblock explains. Key lines:
1. `crawl_tool = WebCrawlTool()`: Init, bind to mock agent.
2. `crawl_result = crawl_tool.execute(...)`: Async crawl/extract.
3. `call_result = call_tool.execute(...)`: Contract read via chains.
4. `tx_result = transact_tool.execute(...)`: TX sim/sign/broadcast via chains.

**Exercise 1:** Add data. Set data="0x..." for contract call, rerun.
**Exercise 2:** Retry crawl. Add --retry flag (extend execute), rerun on bad URL.

## Troubleshooting
- Crawl timeout? Increase crawl_timeout in config.
- TX revert? Check sim in log; low balance? Faucet.
- No key? Skip onchain (graceful).

Best: Base for custom tools, chains for EVM, crawl for web.

## Next Steps
Extend: Phase 6 agents bind these for ReAct/plan (e.g., agent.tools.append(crawl_tool)). Phase 7: CLI run uses tools.

Files: agent.py (self-doc), config.yaml, .env.sample, README.