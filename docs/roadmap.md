# LOLA OS Development Roadmap

**Version:** 1.0-alpha  
**Date:** February 12, 2026  
**Author:** Levi Chinecherem Chidi (0xSemantic)  
**Document:** Roadmap & Engineering Plan

---

## 1. Introduction

This roadmap defines the **incremental, principle‑driven development** of LOLA OS Version 1 alpha. Every line of code will adhere to two non‑negotiable engineering standards:

1. **SOLID Design Principles** – The system is composed of single‑responsibility components, open for extension, substitutable via interfaces, segregated by contract, and dependent only on abstractions.
2. **Self‑Documenting Code** – Every source file must begin with a comprehensive header describing its purpose, key structures, and interactions, followed by a file‑path comment, grouped imports, and strategic inline comments. Every exported symbol is documented. Every file ends with an `// EOF` comment.

This roadmap is **phased for feasibility**: each phase delivers a **vertically integrated, testable slice** of functionality. Phases are sequenced to minimise risk and maximise early validation. The entire V1 alpha is planned for **22 weeks** of focused engineering.

---

## 2. Development Principles – Illustrated

### 2.1 SOLID in Practice

| Principle | Application in LOLA OS |
|-----------|------------------------|
| **Single Responsibility** | Each package and type has exactly one reason to change. `engine` executes tools; `evm` talks to Ethereum; `keystore` manages keys. |
| **Open‑Closed** | Components define interfaces; new chain implementations or security policies are added without modifying existing code. |
| **Liskov Substitution** | Any implementation of `Chain`, `Wallet`, `SecurityPolicy` can replace another without altering the core. |
| **Interface Segregation** | `Chain` does not contain wallet methods; `Wallet` is separate. Large interfaces are split into focused roles. |
| **Dependency Inversion** | High‑level modules (`engine`) depend on abstractions (`Chain`), not on concrete EVM or Solana code. |

### 2.2 Self‑Documentation – Canonical Example

Every Go file in the LOLA OS project MUST follow this exact structure. Below is the **template** that will be used for `internal/core/engine.go`:

```go
// Package core provides the central orchestration engine for LOLA OS.
// It manages agent sessions, tool dispatch, security policy enforcement,
// and coordinates all blockchain interactions through abstract interfaces.
//
// Key types:
//   - Engine      : main orchestrator; created via NewEngine()
//   - Session     : holds per‑invocation context (chain preferences, logger)
//   - Tool        : function signature for executable tools
//
// Engine depends only on interfaces (Chain, Wallet, SecurityPolicy, ToolRegistry),
// making it completely agnostic to specific blockchain implementations.
//
// File: internal/core/engine.go

package core

import (
    "context"
    "fmt"
    "sync"

    "github.com/lola-os/internal/config"
    "github.com/lola-os/internal/security"
    "github.com/lola-os/internal/tools"
    "github.com/lola-os/sdk/types"   // shared types
)

// Engine orchestrates agent operations.
type Engine struct {
    config      *config.Config
    registry    tools.Registry
    security    security.Enforcer
    mu          sync.RWMutex
    sessions    map[string]*Session
}

// NewEngine creates a fully wired Engine instance.
// All dependencies are injected – no hidden global state.
func NewEngine(cfg *config.Config, reg tools.Registry, sec security.Enforcer) *Engine {
    return &Engine{
        config:   cfg,
        registry: reg,
        security: sec,
        sessions: make(map[string]*Session),
    }
}

// Execute runs a tool by name with the given arguments.
// It first resolves the tool, then applies security policies,
// and finally executes the tool function.
// Returns the tool's result or an error.
func (e *Engine) Execute(ctx context.Context, toolName string, args map[string]interface{}) (interface{}, error) {
    // 1. Resolve tool from registry
    tool, err := e.registry.Get(toolName)
    if err != nil {
        return nil, fmt.Errorf("tool %q not found: %w", toolName, err)
    }

    // 2. Create evaluation context for security policies
    evalCtx := &security.EvaluationContext{
        Tool:    toolName,
        Args:    args,
        Session: sessionFromContext(ctx), // extract session if any
    }

    // 3. Run all security policies; if any denies, abort
    if err := e.security.Evaluate(ctx, evalCtx); err != nil {
        return nil, fmt.Errorf("security policy blocked execution: %w", err)
    }

    // 4. Execute the tool
    return tool.Fn(ctx, args)
}

// EOF: internal/core/engine.go
```

**Every** file will follow this pattern: **header comment** (package doc + explanation), **file‑path comment**, **imports**, **code** with strategic inline comments, and an **EOF** marker.

---

## 3. Project Folder Structure (V1 Alpha)

Below is the **complete** directory tree for the LOLA OS repository at the conclusion of Version 1 alpha. Files are organised by responsibility, with internal packages hidden from external consumers, and the `sdk` package providing the public API.

```
lola-os/
├── .github/                   # CI, issue templates
├── cmd/
│   └── lola/                  # (Optional) CLI wrapper, not part of alpha
├── internal/                  # Private implementation – no external imports
│   ├── core/
│   │   ├── engine.go
│   │   ├── session.go
│   │   └── engine_test.go
│   ├── blockchain/
│   │   ├── interface.go       # Chain, Wallet, Contract interfaces
│   │   └── evm/               # EVM implementation (V1 only)
│   │       ├── gateway.go
│   │       ├── keystore.go
│   │       ├── contract.go
│   │       └── evm_test.go
│   ├── tools/
│   │   ├── registry.go
│   │   ├── builtin/          # Built‑in tools (balance, send, etc.)
│   │   │   ├── balance.go
│   │   │   └── transfer.go
│   │   └── registry_test.go
│   ├── security/
│   │   ├── enforcer.go
│   │   ├── policies/
│   │   │   ├── limit.go
│   │   │   ├── whitelist.go
│   │   │   ├── hitl.go
│   │   │   └── readonly.go
│   │   └── enforcer_test.go
│   ├── config/
│   │   ├── loader.go
│   │   ├── env.go
│   │   ├── yaml.go
│   │   └── profiles.go
│   └── observe/
│       ├── logger.go
│       ├── metrics.go
│       ├── tracer.go
│       └── audit.go
├── sdk/
│   ├── lola.go               # Main entry: Init(), Runtime, Tool registration
│   ├── types/                # Shared public types
│   │   ├── transaction.go
│   │   ├── contract.go
│   │   └── chain.go
│   ├── evm/                  # Public EVM convenience wrappers
│   │   └── client.go
│   └── examples/             # Working examples (placed here for documentation)
│       ├── 01_balance_checker/
│       │   └── main.go
│       ├── 02_token_transfer/
│       │   └── main.go
│       └── 03_custom_tool/
│           └── main.go
├── .env.example
├── lola.yaml.example
├── go.mod
├── go.sum
├── Makefile
├── README.md
└── CONTRIBUTING.md
```

**Important:** All code under `internal/` is **private** and not intended for direct consumption. The public SDK lives in `sdk/` and exposes a clean, ergonomic API.

---

## 4. Development Phases

Each phase is **time‑boxed** and delivers a **demonstrable, testable** increment. Phases build upon previous ones; no phase depends on future work. All code produced in any phase **must** already follow the self‑documentation and SOLID standards.

### Phase 0: Project Setup & Foundation (Weeks 1–2)

**Goal:** Establish repository structure, build system, CI, and the **core interfaces** that will drive the entire system.

**Components Developed:**
- `go.mod`, `Makefile`, basic CI (lint, test).
- `internal/blockchain/interface.go` – defines `Chain`, `Wallet`, `Contract` interfaces.
- `internal/tools/interface.go` – defines `Registry` and `Tool` types.
- `internal/security/interface.go` – defines `Enforcer` and `Policy` interfaces.
- `internal/config/interface.go` – defines `Loader` interface.
- `internal/observe/interface.go` – defines `Logger`, `Metrics`, `Tracer` interfaces.

**Key Deliverables:**
- All core abstractions agreed upon and documented.
- No concrete implementations yet – only contracts.
- A test harness that can verify mock implementations.

**Self‑Documentation Sample:**  
The `internal/blockchain/interface.go` file will follow the template, explaining each interface and its role in the dependency inversion chain.

**SOLID Focus:**  
- **Dependency Inversion** established from day one.
- **Interface Segregation** – separate concerns (balance vs. send vs. events).

**Folder Additions:**
```
internal/
├── blockchain/interface.go
├── tools/interface.go
├── security/interface.go
├── config/interface.go
└── observe/interface.go
```

---

### Phase 1: Core Engine & Tool Registry (Weeks 3–5)

**Goal:** Implement the `Engine` and a concrete in‑memory `ToolRegistry`. The engine must be able to execute mock tools and evaluate mock security policies.

**Components Developed:**
- `internal/core/engine.go` – full implementation, depending only on interfaces.
- `internal/tools/registry.go` – thread‑safe in‑memory registry.
- `internal/tools/builtin/` – placeholder built‑in tools (no real blockchain yet).
- Unit tests with mock dependencies.

**Key Deliverables:**
- `Engine.Execute()` correctly resolves tools, calls security, and returns results.
- `ToolRegistry.Register()` and `Get()`.
- 100% test coverage on engine logic.

**Self‑Documentation Sample:**  
`internal/core/engine.go` as shown in section 2.2.

**SOLID Focus:**  
- **Single Responsibility** – engine does not know about blockchain; registry does not execute.
- **Open‑Closed** – new tools can be registered without modifying engine.

**Folder Additions:**
### Phase 1: Core Engine & Tool Registry (Weeks 3–5)

**Goal:** Implement the `Engine` and a concrete in‑memory `ToolRegistry`. The engine must be able to execute mock tools and evaluate mock security policies.

**Components Developed:**
- `internal/core/engine.go` – full implementation, depending only on interfaces.
- `internal/tools/registry.go` – thread‑safe in‑memory registry.
- `internal/tools/builtin/` – placeholder built‑in tools (no real blockchain yet).
- Unit tests with mock dependencies.

**Key Deliverables:**
- `Engine.Execute()` correctly resolves tools, calls security, and returns results.
- `ToolRegistry.Register()` and `Get()`.
- 100% test coverage on engine logic.

**Self‑Documentation Sample:**  
`internal/core/engine.go` as shown in section 2.2.

**SOLID Focus:**  
- **Single Responsibility** – engine does not know about blockchain; registry does not execute.
- **Open‑Closed** – new tools can be registered without modifying engine.

**Folder Additions:**
```
internal/
├── core/
│   ├── engine.go
│   ├── session.go
│   └── engine_test.go
├── tools/
│   ├── registry.go
│   ├── builtin/          (empty stubs)
│   └── registry_test.go
```

```
internal/
├── core/
│   ├── engine.go
│   ├── session.go
│   └── engine_test.go
├── tools/
│   ├── registry.go
│   ├── builtin/          (empty stubs)
│   └── registry_test.go
```

---

### Phase 2: Blockchain Gateway – EVM Read Operations (Weeks 6–8)

**Goal:** Implement **read‑only** EVM capabilities: `GetBalance`, `CallContract`, `ChainID`, `BlockNumber`. No transaction signing or sending yet.

**Components Developed:**
- `internal/blockchain/evm/gateway.go` – implements `Chain` interface for EVM.
- RPC client management (pooling, retries, context support).
- Contract call abstraction – both raw `eth_call` and ABI‑decoded methods.
- Unit tests using a mock RPC server or a forked mainnet node.

**Key Deliverables:**
- Agent can query balances and call view functions on any EVM chain.
- Configuration can specify RPC URLs.
- Logging of all RPC requests (via `observe` interface – we'll use a no‑op logger for now).

**Self‑Documentation Sample:**  
`internal/blockchain/evm/gateway.go` – header explains connection pooling, retry policy, and the fact it implements `Chain`.

**SOLID Focus:**  
- **Liskov Substitution** – `EVMGateway` is a valid `Chain`.
- **Open‑Closed** – new chains (Solana, etc.) will add new packages without touching `evm`.

**Folder Additions:**
```
internal/
├── blockchain/
│   ├── evm/
│   │   ├── gateway.go
│   │   ├── client.go        # RPC client wrapper
│   │   ├── contract.go      # Contract call helpers
│   │   └── evm_test.go
```

**Integration:**  
Engine now can be configured with an `EVMGateway` and execute tools that call it (e.g., a `balance` tool). We will implement the built‑in `balance` tool in this phase.

---

### Phase 3: Blockchain Gateway – Write Operations & Wallet (Weeks 9–11)

**Goal:** Add **transaction creation, signing, and submission** for EVM. Implement `Wallet` interface with an encrypted keystore.

**Components Developed:**
- `internal/blockchain/evm/keystore.go` – implements `Wallet` using AES‑256‑GCM encryption.
- Transaction builder – `evm.SendTransaction`, `evm.DeployContract`.
- Gas estimation and fee market logic (EIP‑1559 support).
- Receipt waiting and confirmation handling.

**Key Deliverables:**
- Agent can send ETH and ERC‑20 tokens.
- Private keys are stored encrypted on disk; decrypted only in memory for signing.
- Read‑only mode if no private key provided.

**Self‑Documentation Sample:**  
`internal/blockchain/evm/keystore.go` – explains encryption scheme, passphrase handling, and security considerations.

**SOLID Focus:**  
- **Dependency Inversion** – `EVMGateway` depends on `Wallet` interface, not on `Keystore` concretely.
- **Single Responsibility** – keystore only manages keys and signing.

**Folder Additions:**
```
internal/
├── blockchain/
│   ├── evm/
│   │   ├── keystore.go
│   │   ├── tx.go           # transaction construction helpers
│   │   └── receipt.go
```

**Built‑in Tools Added:** `transfer`, `deploy`, `approve`, etc.

---

### Phase 4: Security Guardrails & Configuration (Weeks 12–14)

**Goal:** Implement a **pluggable security policy enforcer** and the full configuration system (`.env`, `lola.yaml`). The engine will now consult policies before allowing any write operation.

**Components Developed:**
- `internal/security/enforcer.go` – aggregates multiple policies, all must allow.
- `internal/security/policies/` – concrete policies:
  - `limit.go` – per‑tx and daily limits.
  - `whitelist.go` – restrict destination addresses.
  - `hitl.go` – human‑in‑the‑loop (console prompt).
  - `readonly.go` – global read‑only flag.
- `internal/config/loader.go` – layered config: env overrides file, defaults.
- `internal/config/env.go`, `internal/config/yaml.go` – providers.

**Key Deliverables:**
- Agent can be configured with daily spend limits.
- Human approval for large transactions (pauses, prompts in console, resumes).
- Configuration files are optional; `.env` alone is sufficient for basic use.

**Self‑Documentation Sample:**  
`internal/security/enforcer.go` – explains policy chaining, early exit, error aggregation.

**SOLID Focus:**  
- **Open‑Closed** – new policies added without modifying enforcer.
- **Interface Segregation** – `Policy` interface is minimal: `Check(ctx, evalCtx) error`.

**Folder Additions:**
```
internal/
├── security/
│   ├── enforcer.go
│   ├── enforcer_test.go
│   └── policies/
│       ├── limit.go
│       ├── whitelist.go
│       ├── hitl.go
│       └── readonly.go
├── config/
│   ├── loader.go
│   ├── env.go
│   ├── yaml.go
│   ├── profiles.go        # chain profiles
│   └── config_test.go
```

---

### Phase 5: Observability & Auditing (Weeks 15–16)

**Goal:** Implement structured logging, Prometheus metrics, and an audit trail. This is **non‑negotiable** – every operation must be observable.

**Components Developed:**
- `internal/observe/logger.go` – wrapper around `zap` for structured JSON logs.
- `internal/observe/metrics.go` – Prometheus counters, histograms for RPC calls, tx submissions, errors.
- `internal/observe/tracer.go` – OpenTelemetry tracing (context propagation).
- `internal/observe/audit.go` – append‑only log of all onchain writes (local file, pluggable).

**Key Deliverables:**
- All components (engine, evm, security) emit logs with `session_id`, `tool`, `chain`, `tx_hash`.
- Metrics endpoint exposed (if enabled).
- Audit trail records every transaction sent.

**Self‑Documentation Sample:**  
`internal/observe/logger.go` – explains log levels, fields, and how to inject a logger into context.

**SOLID Focus:**  
- **Dependency Inversion** – components depend on `Logger` interface, not concrete zap logger.
- **Single Responsibility** – observability separated from business logic.

**Folder Additions:**
```
internal/
└── observe/
    ├── logger.go
    ├── metrics.go
    ├── tracer.go
    ├── audit.go
    └── noop.go           # no‑op implementations for testing
```

**Integration:**  
All previous components are refactored to accept `Logger`, `Metrics`, etc. via dependency injection.

---

### Phase 6: Adapter Layer & Go SDK Ergonomics (Weeks 17–19)

**Goal:** Expose a **polished, idiomatic Go SDK** that developers will actually enjoy using. Implement the adapter layer, decorators, and the `lola.Init()` experience.

**Components Developed:**
- `sdk/lola.go` – `Init()`, `Runtime`, `WithChain`, `RegisterTool`, `ToolFunc`.
- `sdk/evm/client.go` – public convenience wrappers (e.g., `evm.GetBalance`).
- `internal/adapter/` – internal bridge between SDK and internal components (thin).
- `sdk/examples/` – first three working examples.

**Key Deliverables:**
- Developer can `go get github.com/lola-os/sdk` and write a 10‑line agent.
- Complete parity between SDK convenience functions and low‑level internal APIs.
- All examples are tested and runnable.

**Self‑Documentation Sample:**  
`sdk/lola.go` – explains the fluent initialisation, how the runtime holds the engine, and how tools are registered.

**SOLID Focus:**  
- **Dependency Inversion** – SDK talks to internal interfaces, not concrete global state.
- **Open‑Closed** – new SDK methods can be added without breaking existing users.

**Folder Additions:**
```
sdk/
├── lola.go
├── runtime.go
├── options.go
├── types/
│   ├── transaction.go
│   ├── contract.go
│   └── chain.go
├── evm/
│   └── client.go
└── examples/
    ├── 01_balance_checker/
    │   └── main.go
    ├── 02_token_transfer/
    │   └── main.go
    └── 03_custom_tool/
        └── main.go
```

---

### Phase 7: Examples, Documentation, and Alpha Polish (Weeks 20–22)

**Goal:** Ensure the system is **ready for public alpha**. This is not a “throw over the wall” release; it must be polished, documented, and easy to adopt.

**Tasks:**
- Expand examples to cover all major use cases (multi‑chain, custom tools, security policies).
- Write comprehensive `README.md`, `CONTRIBUTING.md`, and user‑facing documentation.
- Perform **failure injection tests** (simulate RPC errors, timeouts, policy denials) using a test harness.
- Profile and optimise critical paths (RPC pooling, JSON unmarshaling).
- Finalise `lola.yaml.example` and `.env.example`.
- Create a **quickstart** guide that can be followed in one evening.

**Key Deliverables:**
- Public `v1.0.0-alpha` tag on GitHub.
- All documentation in place.
- Test coverage >80% (with focus on critical paths).

**Self‑Documentation:**  
Every example file follows the same self‑documentation standard, so new developers can learn by reading.

---

## 5. Post‑Alpha Roadmap (Brief)

After the alpha release, development will continue in parallel tracks:

| Track | Focus | Estimated Timeline |
|-------|-------|---------------------|
| **Non‑EVM Chains** | Solana, Cosmos adapters | Q3 2026 |
| **Advanced Networking** | QUIC transport, gossip discovery | Q4 2026 |
| **lola.garden** | LLM specialization module | Q1 2027 |
| **Python SDK** | Feature‑complete Python binding | Q2 2027 |
| **Web Dashboard** | Visual agent monitoring | H2 2027 |

These extensions will be developed as **optional plugins** that depend on the core but never modify it – a testament to the SOLID foundation built in V1 alpha.

---

## 6. Conclusion

This roadmap is **realistic, detailed, and principle‑driven**. Each phase produces a working, testable increment that brings us closer to the vision: **every agent blockchain‑native**. By adhering to SOLID and self‑documentation from the first commit, we ensure that LOLA OS will be **maintainable, extensible, and trusted** by developers worldwide.

The path is clear. Let’s build it.

---

*End of Roadmap Document*