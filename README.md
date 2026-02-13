# LOLA OS

**Live Onchain Logical Agents** · *Make every agent blockchain-native.*

[![Go Reference](https://pkg.go.dev/badge/github.com/0xSemantic/lola-os.svg)](https://pkg.go.dev/github.com/0xSemantic/lola-os)
[![Go Report Card](https://goreportcard.com/badge/github.com/0xSemantic/lola-os)](https://goreportcard.com/report/github.com/0xSemantic/lola-os)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/0xSemantic/lola-os/actions/workflows/ci.yml/badge.svg)](https://github.com/0xSemantic/lola-os/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/0xSemantic/lola-os/branch/main/graph/badge.svg)](https://codecov.io/gh/0xSemantic/lola-os)
[![Discord](https://img.shields.io/discord/1234567890?color=5865F2&label=Discord&logo=discord&logoColor=white)](https://discord.gg/lola-os)
[![Twitter Follow](https://img.shields.io/twitter/follow/0xSemantic?style=social)](https://twitter.com/0xSemantic)

---

**LOLA OS** is a modular, extensible systems infrastructure that turns **any** AI agent—regardless of its original framework—into a **blockchain‑native agent** with full read/write capabilities across EVM chains.  

> ✨ **One evening. No framework rewrite. Full onchain power.**

---

## Why LOLA OS?

Every day, thousands of developers build agents that could benefit from onchain interactions—trading, verifying, escrowing, automating DeFi, or simply reading contract state.  
Today, they cobble together fragile scripts: raw RPC calls, manual transaction signing, ad‑hoc retry logic, and zero security guardrails.  

**LOLA OS replaces that chaos with a single, idiomatic Go SDK.**  

- **Framework‑agnostic** – works with LangChain, CrewAI, AutoGPT, or raw Go functions.  
- **Minimal friction** – import, init, and you’re calling contracts in 10 lines.  
- **Ownership‑grade** – built with SOLID principles, full observability, and failure injection testing.  
- **Future‑proof** – designed for tomorrow’s chains and protocols, without breaking today’s agents.  

---

## Quick Start – 10 Minutes to Onchain

```bash
go get github.com/0xSemantic/lola-os/sdk
```

Create a `.env` file (copy from `.env.example`):

```bash
ETH_MAINNET_RPC=https://mainnet.infura.io/v3/YOUR_KEY
# ETH_PRIVATE_KEY=...   # optional – without it, agent is read‑only
```

Write your first agent – `main.go`:

```go
package main

import (
    "context"
    "fmt"
    "github.com/0xSemantic/lola-os/sdk"
)

func main() {
    rt := sdk.Init() // reads .env, sets up default chains

    err := rt.Run(context.Background(), func(ctx context.Context, rt *sdk.Runtime) error {
        balance, err := rt.EVM.GetBalance(ctx, "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7", nil)
        if err != nil {
            return err
        }
        fmt.Printf("Balance: %s wei\n", balance.String())
        return nil
    })

    if err != nil {
        panic(err)
    }
}
```

```bash
go run main.go
```

✅ **You just made an agent blockchain‑native in <10 minutes.**  

[👉 See more examples →](https://github.com/0xSemantic/lola-os/tree/main/sdk/examples)

---

## Features (Version 1 alpha)

| Category | Capabilities |
|----------|--------------|
| **EVM Chains** | Ethereum, Polygon, Arbitrum, Optimism, Base, BSC, Avalanche + any custom RPC |
| **Read Operations** | Balance, nonce, contract calls (ABI or raw), chain ID, block number |
| **Write Operations** | Send ETH, deploy contracts, write to contracts (ERC‑20, ERC‑721, custom) |
| **Wallet Management** | Encrypted keystore (AES‑256‑GCM), read‑only fallback, hardware wallet (planned) |
| **Security Guardrails** | Per‑tx & daily limits, address whitelist, human‑in‑the‑loop, global read‑only mode |
| **Configuration** | `.env` for secrets, optional `lola.yaml` for advanced settings, chain profiles |
| **Tool System** | Register any Go function as an onchain tool, call via `rt.Execute()` |
| **Observability** | Structured JSON logs, Prometheus metrics, OpenTelemetry traces, immutable audit trail |
| **Integration** | Works with any agent framework – just wrap your logic in `rt.Run()` |

> 🔒 **Security by default** – no private key? agent is read‑only. Exceed a limit? transaction is blocked.  
> 🔍 **Observable by design** – every RPC call, every signature, every policy decision is logged with a correlation ID.

---

## Architecture in a Nutshell

LOLA OS is **three concentric layers**:

1. **Agent Environment** – your existing code, unchanged.  
2. **LOLA OS SDK** – a thin adapter, the orchestration engine, and pluggable blockchain modules.  
3. **External Systems** – EVM RPC endpoints, block explorers.

```
┌─────────────────┐
│   Your Agent    │  (LangChain, CrewAI, custom)
└────────┬────────┘
         │ wraps calls
         ▼
┌─────────────────────────────────────┐
│         LOLA OS SDK                │
│  ┌─────────────┐  ┌─────────────┐  │
│  │  Adapter    │  │   Engine    │  │
│  └─────────────┘  └─────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  │
│  │    EVM      │  │  Security   │  │
│  │   Gateway   │  │  Guardrails │  │
│  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────┘
         │ RPC/WebSocket
         ▼
┌─────────────────┐
│   EVM Chains    │
└─────────────────┘
```

**Every component is defined by an interface.**  
New chains (Solana, Cosmos) are new packages that implement the same `Chain` interface – **zero changes to the core**.

[📘 Read the full architecture →](https://github.com/0xSemantic/lola-os/blob/main/docs/architecture.md)

---

## Why Go?

- **Performance** – low latency, high concurrency, ideal for agent workloads.  
- **Simplicity** – one binary, no runtime, easy deployment.  
- **Ecosystem** – `go-ethereum` is the gold standard for EVM.  
- **Future‑proof** – Go’s interface system makes SOLID design natural.

> 🐍 **Python SDK is coming** – a thin wrapper around the Go core, with complete feature parity.

---

## Getting Started

### 1. Installation

```bash
go get github.com/0xSemantic/lola-os/sdk
```

### 2. Configuration

Copy `.env.example` to `.env` and add at least one RPC URL.  
That’s it. LOLA OS auto‑detects available chains.

### 3. Write your first tool

```go
// Register a custom swap tool
sdk.RegisterTool("swap", func(ctx context.Context, args map[string]interface{}) (interface{}, error) {
    from := args["from"].(string)
    to := args["to"].(string)
    amount := args["amount"].(*big.Int)
    // ... build transaction ...
    return rt.EVM.SendTransaction(ctx, tx)
})

// Then call it from anywhere
result, _ := rt.Execute(ctx, "swap", map[string]interface{}{
    "from":   "0x...",
    "to":     "0x...",
    "amount": big.NewInt(1e18),
})
```

[📚 Full SDK reference →](https://pkg.go.dev/github.com/0xSemantic/lola-os/sdk)

---

## Examples

| Example | Description | Link |
|--------|-------------|------|
| **Balance Checker** | 10‑line agent that reads ETH balance | [view](https://github.com/0xSemantic/lola-os/tree/main/sdk/examples/01_balance_checker) |
| **Token Transfer** | Send ERC‑20 tokens with human approval | [view](https://github.com/0xSemantic/lola-os/tree/main/sdk/examples/02_token_transfer) |
| **Custom Tool** | Register a Uniswap swap tool and execute it | [view](https://github.com/0xSemantic/lola-os/tree/main/sdk/examples/03_custom_tool) |
| **Multi‑Chain Scanner** | Iterate over 3 chains and fetch USDC balances | [view](https://github.com/0xSemantic/lola-os/tree/main/sdk/examples/04_multi_chain) |
| **Security Policies** | Configure daily limits and whitelist | [view](https://github.com/0xSemantic/lola-os/tree/main/sdk/examples/05_security_policies) |

All examples are **tested and runnable** – copy, paste, `go run`.

---

## Documentation

- 📖 [**Architecture**](https://github.com/0xSemantic/lola-os/blob/main/docs/architecture.md) – complete system design, interface contracts, data flows.
- 🛣️ [**Roadmap**](https://github.com/0xSemantic/lola-os/blob/main/docs/roadmap.md) – phased development plan from V1 alpha to ecosystem.
- 🧑‍💻 [**Contributing Guide**](https://github.com/0xSemantic/lola-os/blob/main/CONTRIBUTING.md) – how to build, test, and submit changes.
- 🔧 [**Configuration Reference**](https://github.com/0xSemantic/lola-os/blob/main/docs/configuration.md) – all `.env` and `lola.yaml` options.
- 🐛 [**Issue Tracker**](https://github.com/0xSemantic/lola-os/issues) – bugs, feature requests, RFCs.

---

## Community & Contributing

LOLA OS is **open source** (Apache 2.0) and we welcome contributors of all skill levels.

### Ways to contribute

- 🐛 **Report bugs** – open an issue with a clear reproduction.
- 💡 **Suggest features** – start a discussion or open a feature request.
- 🔧 **Submit code** – read the [contributing guide](https://github.com/0xSemantic/lola-os/blob/main/CONTRIBUTING.md), pick an issue, and open a PR.
- 📚 **Improve docs** – fix typos, write examples, translate.
- 🌍 **Spread the word** – star the repo, tweet, blog, or present at meetups.

### Join the conversation

- 💬 [**Discord**](https://discord.gg/lola-os) – chat with maintainers and users.
- 🐦 [**Twitter**](https://twitter.com/0xSemantic) – follow for updates.
- 📧 **Email** – [lola@0xsemantic.com](mailto:lola@0xsemantic.com) (maintainer)

### Core contributors

- **Levi Chinecherem Chidi** ([@0xSemantic](https://github.com/0xSemantic)) – creator & lead architect.

---

## License

Copyright © 2026 Levi Chinecherem Chidi  

Licensed under the **Apache License, Version 2.0** (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at  

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)  

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

---

**LOLA OS** – *Live Onchain Logical Agents*  
Built with ❤️ by [0xSemantic](https://github.com/0xSemantic) and contributors.  

[![Star History Chart](https://api.star-history.com/svg?repos=0xSemantic/lola-os&type=Date)](https://star-history.com/#0xSemantic/lola-os&Date)