# LOLA OS Configuration Reference

**Version:** 1.0-alpha  
**Document:** `configurations.md`  
**Last Updated:** February 12, 2026  

---

## Table of Contents

1. [Overview](#overview)  
2. [Configuration Layers & Precedence](#configuration-layers--precedence)  
3. [Environment Variables (`.env`)](#environment-variables-env)  
   - 3.1 [Required Variables](#31-required-variables)  
   - 3.2 [Optional Variables](#32-optional-variables)  
   - 3.3 [Private Key & Security](#33-private-key--security)  
4. [YAML Configuration (`lola.yaml`)](#yaml-configuration-lolayaml)  
   - 4.1 [Top‑Level Structure](#41-top‑level-structure)  
   - 4.2 [`chains` Section](#42-chains-section)  
   - 4.3 [`wallet` Section](#43-wallet-section)  
   - 4.4 [`security` Section](#44-security-section)  
   - 4.5 [`observability` Section](#45-observability-section)  
   - 4.6 [`advanced` Section](#46-advanced-section)  
5. [Chain Profiles](#chain-profiles)  
   - 5.1 [Built‑in Profiles](#51-built‑in-profiles)  
   - 5.2 [Overriding a Profile](#52-overriding-a-profile)  
   - 5.3 [Custom Chains](#53-custom-chains)  
6. [Security Policy Configuration](#security-policy-configuration)  
   - 6.1 [Transaction Limits](#61-transaction-limits)  
   - 6.2 [Address Whitelist / Blacklist](#62-address-whitelist--blacklist)  
   - 6.3 [Human‑in‑the‑Loop (HITL)](#63-human‑in‑the‑loop-hitl)  
   - 6.4 [Read‑Only Mode](#64-read‑only-mode)  
7. [Observability Configuration](#observability-configuration)  
   - 7.1 [Logging](#71-logging)  
   - 7.2 [Metrics](#72-metrics)  
   - 7.3 [Tracing](#73-tracing)  
   - 7.4 [Audit Trail](#74-audit-trail)  
8. [Complete Configuration Examples](#complete-configuration-examples)  
   - 8.1 [Minimal (`.env` only)](#81-minimal-env-only)  
   - 8.2 [Development with Custom Chain](#82-development-with-custom-chain)  
   - 8.3 [Production with Full Security](#83-production-with-full-security)  
9. [Appendix: Environment Variable Reference](#appendix-environment-variable-reference)  

---

## 1. Overview

LOLA OS is designed around **zero‑configuration by default** and **progressive disclosure of complexity**.  

- **You can start with nothing but a `.env` file containing a single RPC URL.**  
- When you need fine‑grained control—custom chain settings, security policies, or observability—you add a `lola.yaml` file.  
- Every configuration value has a **sensible default**; you only need to specify what you want to change.

**Philosophy:**  
> Configuration should be boring. Secrets stay out of code. Defaults work for 80% of users. The remaining 20% can override anything.

---

## 2. Configuration Layers & Precedence

LOLA OS reads configuration from multiple sources, with **later sources overriding earlier ones**:

| Layer               | Source                      | Precedence |
|---------------------|-----------------------------|------------|
| 1. Defaults         | Hard‑coded in code          | Lowest     |
| 2. Chain profiles   | Built‑in YAML (embedded)    |            |
| 3. Config file      | `lola.yaml` or `lola.json`  |            |
| 4. Environment      | `.env` file / OS env vars   |            |
| 5. Programmatic     | `lola.Init(WithOption)`     | Highest    |

**Order of evaluation:**  
1. Start with built‑in defaults and chain profiles.  
2. Load optional `lola.yaml` (if present) and merge.  
3. Read environment variables (`.env` or actual env) – these **override** any YAML settings.  
4. Apply any options passed to `lola.Init()` (e.g., `lola.WithChainRPC(...)`).

---

## 3. Environment Variables (`.env`)

Environment variables are the **primary mechanism for supplying secrets** (RPC endpoints, private keys) and are also used for quick overrides.

### 3.1 Required Variables

You **must** provide at least one RPC URL for a chain. Without one, LOLA OS cannot connect to any blockchain.

```bash
# Ethereum Mainnet
ETH_MAINNET_RPC=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# OR Polygon
POLYGON_RPC=https://polygon-rpc.com

# OR any other supported chain – see built‑in profiles
```

If you do **not** provide a private key, the agent operates in **read‑only mode** (balance checks, contract calls – no transactions).

### 3.2 Optional Variables

| Variable                     | Description                                                                 | Example                                 |
|------------------------------|-----------------------------------------------------------------------------|-----------------------------------------|
| `ETH_PRIVATE_KEY`            | Hex‑encoded private key (without `0x`). **Never commit to git.**            | `ETH_PRIVATE_KEY=4c0883a...`            |
| `LOLA_LOG_LEVEL`            | Log level: `debug`, `info`, `warn`, `error` (default `info`).              | `LOLA_LOG_LEVEL=debug`                 |
| `LOLA_METRICS_ENABLED`      | Enable Prometheus metrics endpoint (default `false`).                       | `LOLA_METRICS_ENABLED=true`            |
| `LOLA_METRICS_ADDR`        | Listen address for metrics (default `:9090`).                              | `LOLA_METRICS_ADDR=:8081`              |
| `LOLA_AUDIT_PATH`          | File path for audit log (default `./lola.audit.log`).                      | `LOLA_AUDIT_PATH=/var/log/lola/audit`  |
| `LOLA_DEFAULT_CHAIN`       | Chain ID or name to use as default (overrides config).                     | `LOLA_DEFAULT_CHAIN=polygon`           |

### 3.3 Private Key & Security

- The private key variable is **read once at startup** and never logged.  
- We **strongly recommend** using an encrypted keystore instead of plaintext env vars for production.  
- To use the encrypted keystore, omit `ETH_PRIVATE_KEY` and configure the keystore path in `lola.yaml` (see [§4.3](#43-wallet-section)).

---

## 4. YAML Configuration (`lola.yaml`)

Place `lola.yaml` (or `lola.json`) in the working directory of your agent, or specify a custom path via the `LOLA_CONFIG` environment variable.

### 4.1 Top‑Level Structure

```yaml
# lola.yaml – complete reference
version: "1.0"                # optional, reserved for future schema evolution
name: "my-trading-agent"      # optional, used in logs and metrics

chains:
  # ... see section 4.2

wallet:
  # ... see section 4.3

security:
  # ... see section 4.4

observability:
  # ... see section 4.5

advanced:
  # ... see section 4.6
```

### 4.2 `chains` Section

Configure chain‑specific settings. You can reference a built‑in profile by its **id** (e.g., `ethereum`, `polygon`) and override only the fields you need.

```yaml
chains:
  # Override Ethereum mainnet settings
  ethereum:
    rpc: https://mainnet.infura.io/v3/abc123         # overrides env or default
    rpc_fallback:                                    # optional backup RPC
      - https://eth-mainnet.alchemyapi.io/v2/xyz
      - https://cloudflare-eth.com
    gas_price_limit: 100 gwei                        # reject txs above this
    confirmations: 2                                 # blocks to wait
    timeout: 30s                                     # RPC timeout
    default: true                                    # use as default chain

  # Add a custom network not in built‑in profiles
  my-local-geth:
    chain_id: 1337
    rpc: http://localhost:8545
    native_currency: ETH
    block_time: 2s
    default: false
```

**Fields:**
- `rpc` – primary RPC endpoint (overrides `*_RPC` env var).  
- `rpc_fallback` – list of backup RPCs (tried in order).  
- `gas_price_limit` – max gas price the agent will accept (string with unit, e.g., `100 gwei`, `0.1 eth`).  
- `confirmations` – number of blocks to wait for transaction finality (default: `1`).  
- `timeout` – per‑request timeout (Go duration string).  
- `default` – set to `true` to make this chain the default when none is specified.  

### 4.3 `wallet` Section

Configure how the agent handles keys and signing.

```yaml
wallet:
  # Use encrypted keystore (recommended for production)
  keystore_path: ./keystore
  # If not set, you will be prompted for the passphrase on startup.
  # You can also set the passphrase via env var: LOLA_KEYSTORE_PASSPHRASE
  # passphrase_env: LOLA_KEYSTORE_PASSPHRASE

  # Alternative: use plaintext private key from env (development only)
  # private_key_env: ETH_PRIVATE_KEY   # this is the default

  # Timeout for wallet operations (signing, decryption)
  timeout: 5s
```

- If `keystore_path` is provided, LOLA OS uses an **encrypted keystore** (AES‑256‑GCM).  
- If `keystore_path` does not exist, a new keystore will be created on first use.  
- Passphrase can be supplied via:
  - Interactive prompt (if terminal)  
  - Environment variable (set `keystore.passphrase_env`)  
  - Programmatic option `lola.WithKeystorePassphrase()`

### 4.4 `security` Section

Define security policies. All policies are **optional**; if omitted, the corresponding checks are skipped.

```yaml
security:
  # Global read‑only mode – overrides any private key presence
  read_only: false

  # Per‑transaction amount limit (applies to native currency)
  max_transaction_value: 1 eth   # strings with units: wei, gwei, eth

  # Daily spend limit (native currency)
  daily_limit: 5 eth

  # Address restrictions
  allowed_addresses:
    - "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7"
    - "0x..."   # contracts your agent is allowed to interact with
  blocked_addresses: []          # if both are present, allowed takes precedence

  # Human‑in‑the‑loop: require manual approval for transactions above threshold
  human_in_the_loop:
    enabled: true
    threshold: 0.5 eth
    timeout: 5m                 # how long to wait for approval
    mode: console              # other modes: http (future)
```

**Amount units:**  
- `wei`, `gwei`, `eth` (case‑insensitive).  
- Examples: `"1000 wei"`, `"2.5 gwei"`, `"0.1 eth"`.  
- If no unit is given, defaults to `wei`.

### 4.5 `observability` Section

```yaml
observability:
  logging:
    level: info                # debug, info, warn, error
    format: json              # json or console
    output: stdout           # file path or stdout/stderr

  metrics:
    enabled: false
    addr: :9090
    path: /metrics

  tracing:
    enabled: false
    exporter: otlp           # otlp, jaeger, stdout
    endpoint: localhost:4317
    service_name: lola-agent

  audit:
    enabled: true
    path: ./lola.audit.log   # append‑only file
    # or use a custom writer via plugin (future)
```

### 4.6 `advanced` Section

Reserved for experimental or advanced tuning. Use with caution.

```yaml
advanced:
  # Tool registry backend (default: in‑memory)
  # tool_registry: redis://localhost:6379   (future)

  # Maximum RPC retries
  rpc_retries: 3

  # RPC backoff initial delay
  rpc_backoff: 100ms
```

---

## 5. Chain Profiles

### 5.1 Built‑in Profiles

LOLA OS ships with pre‑defined profiles for the most popular EVM chains. Each profile knows:

- `chain_id`  
- `native_currency` (symbol, decimals)  
- `block_time` (for confirmation estimates)  
- Optional **public fallback RPC** (rate‑limited, use only for testing)

| Profile ID   | Chain Name      | Chain ID | Native Currency | Public Fallback RPC (if any) |
|--------------|-----------------|----------|-----------------|------------------------------|
| `ethereum`   | Ethereum Mainnet| 1        | ETH             | https://cloudflare-eth.com  |
| `polygon`    | Polygon         | 137      | MATIC           | https://polygon-rpc.com     |
| `arbitrum`   | Arbitrum One    | 42161    | ETH             | https://arb1.arbitrum.io/rpc|
| `optimism`   | Optimism        | 10       | ETH             | https://mainnet.optimism.io |
| `base`       | Base            | 8453     | ETH             | https://mainnet.base.org    |
| `bsc`        | Binance Smart   | 56       | BNB             | https://bsc-dataseed.binance.org|
| `avalanche`  | Avalanche C‑chain| 43114   | AVAX            | https://api.avax.network/ext/bc/C/rpc|
| `goerli`     | Goerli (testnet)| 5        | ETH             | (none, must provide own RPC)|
| `sepolia`    | Sepolia         | 11155111 | ETH             | (none)                     |

### 5.2 Overriding a Profile

To change any property of a built‑in profile, simply include it in your `lola.yaml`:

```yaml
chains:
  polygon:
    rpc: https://polygon-mainnet.g.alchemy.com/v2/your-key
    confirmations: 3
```

All other profile properties remain at their built‑in defaults.

### 5.3 Custom Chains

Add a completely new chain by specifying a unique **key** (your identifier) and at minimum `chain_id` and `rpc`:

```yaml
chains:
  my-rollup:
    chain_id: 4242
    rpc: https://my-rollup.com/rpc
    native_currency: ETH
    block_time: 2s
```

You can then refer to this chain in your agent by its key `"my-rollup"`.

---

## 6. Security Policy Configuration

Security policies are evaluated **in order** when a transaction is attempted. If any policy denies the operation, the transaction is rejected.

### 6.1 Transaction Limits

- **`max_transaction_value`** – rejects any transaction with `value > limit`.  
- **`daily_limit`** – tracks total value sent in the last 24h (rolling window).  

Both limits apply **only to the native currency** (ETH, MATIC, etc.). Token transfers are **not** counted toward these limits (but can be restricted via whitelist).

### 6.2 Address Whitelist / Blacklist

- **`allowed_addresses`** – if non‑empty, only these addresses are permitted as `to` in transactions.  
- **`blocked_addresses`** – if an address is in both lists, `allowed` takes precedence.

These lists apply to **all write operations** (ETH transfers, contract calls). Read operations are unrestricted.

### 6.3 Human‑in‑the‑Loop (HITL)

When enabled, transactions above `threshold` will **pause** and wait for manual approval.  

**Console mode:**  
The agent prints a prompt to stdout, waits for `y`/`n` input, and resumes execution. This is ideal for local development or agents running in interactive terminals.

**HTTP mode (future):**  
Will call an external webhook for approval.

### 6.4 Read‑Only Mode

Setting `read_only: true` **globally disables all write operations**, regardless of private key presence. Useful for untrusted environments or audit agents.

---

## 7. Observability Configuration

### 7.1 Logging

- **`level`** – `debug` (verbose), `info` (default), `warn`, `error`.  
- **`format`** – `json` (structured, recommended) or `console` (human‑readable).  
- **`output`** – file path or `stdout`/`stderr`.

All log entries include:
- `timestamp` (RFC3339 with millis)  
- `level`  
- `session_id` (correlation ID for the agent run)  
- `component` (e.g., `engine`, `evm`, `security`)  
- `message`  
- Additional fields depending on context (`chain`, `tx_hash`, `tool`)

### 7.2 Metrics

Prometheus metrics are exposed on `/metrics` (default port `9090`).  

**Metrics provided:**
- `lola_rpc_requests_total` – counters per chain and method  
- `lola_rpc_duration_seconds` – histogram  
- `lola_transactions_submitted_total` – counter  
- `lola_transactions_confirmed_total` – counter  
- `lola_security_policy_denials_total` – counter per policy  

### 7.3 Tracing

OpenTelemetry tracing can be enabled to trace requests from agent call to blockchain receipt.  

Supported exporters: `otlp` (gRPC), `jaeger`, `stdout` (debug).

### 7.4 Audit Trail

When enabled, every **onchain write** is recorded in an append‑only file. Each entry is a JSON object containing:

```json
{
  "timestamp": "2026-02-12T15:04:05Z",
  "session_id": "abc123",
  "agent_name": "my-trading-bot",
  "chain": "ethereum",
  "tx_hash": "0x...",
  "from": "0x...",
  "to": "0x...",
  "value": "1000000000000000000",
  "data": "0x...",
  "policy_results": ["limit:allow", "whitelist:allow"]
}
```

This file is **immutable** (append‑only) and can be used for compliance or post‑mortem analysis.

---

## 8. Complete Configuration Examples

### 8.1 Minimal (`.env` only)

```bash
# .env – all you need to start
ETH_MAINNET_RPC=https://mainnet.infura.io/v3/abc123
```

That’s it. LOLA OS uses built‑in defaults, read‑only mode, console logging, no metrics.

### 8.2 Development with Custom Chain

```yaml
# lola.yaml
version: "1.0"
name: "dev-agent"

chains:
  ethereum:
    rpc: http://localhost:8545   # local ganache
    confirmations: 1
    default: true

security:
  max_transaction_value: 10 eth   # high limit for dev
  human_in_the_loop:
    enabled: true
    threshold: 1 eth
    mode: console

observability:
  logging:
    level: debug
    format: console
```

```bash
# .env – still need an RPC for the custom chain (already in YAML)
# No private key – we'll use keystore
```

### 8.3 Production with Full Security

```yaml
# lola.yaml
version: "1.0"
name: "prod-trading-bot"

chains:
  ethereum:
    rpc: ${ETH_MAINNET_RPC}          # reference env var
    gas_price_limit: 50 gwei
    confirmations: 3
  polygon:
    rpc: ${POLYGON_RPC}
    default: true                   # default chain is polygon

wallet:
  keystore_path: /secrets/keystore
  passphrase_env: KEYSTORE_PASSPHRASE

security:
  read_only: false
  max_transaction_value: 0.5 eth
  daily_limit: 2 eth
  allowed_addresses:
    - "0x..."   # only our own contracts
  human_in_the_loop:
    enabled: true
    threshold: 0.1 eth
    timeout: 10m

observability:
  logging:
    level: info
    format: json
    output: /var/log/lola/agent.log
  metrics:
    enabled: true
    addr: :9090
  audit:
    enabled: true
    path: /var/log/lola/audit.log
```

```bash
# .env – secrets only
ETH_MAINNET_RPC=https://mainnet.infura.io/v3/abc123
POLYGON_RPC=https://polygon-mainnet.g.alchemy.com/v2/xyz
KEYSTORE_PASSPHRASE=supersecret
```

---

## 9. Appendix: Environment Variable Reference

| Variable                          | Description                                                                 | Default         |
|-----------------------------------|-----------------------------------------------------------------------------|-----------------|
| `ETH_MAINNET_RPC`                | Ethereum Mainnet RPC URL                                                   | – (required if used) |
| `POLYGON_RPC`                   | Polygon RPC URL                                                            | –              |
| `ARBITRUM_RPC`                  | Arbitrum RPC URL                                                           | –              |
| `OPTIMISM_RPC`                  | Optimism RPC URL                                                           | –              |
| `BASE_RPC`                      | Base RPC URL                                                               | –              |
| `BSC_RPC`                       | Binance Smart Chain RPC URL                                                | –              |
| `AVALANCHE_RPC`                | Avalanche C‑chain RPC URL                                                  | –              |
| `GOERLI_RPC`                   | Goerli testnet RPC URL                                                     | –              |
| `SEPOLIA_RPC`                  | Sepolia testnet RPC URL                                                    | –              |
| `ETH_PRIVATE_KEY`              | Hex private key (no 0x) for signing                                        | –              |
| `LOLA_KEYSTORE_PASSPHRASE`    | Passphrase for encrypted keystore                                          | –              |
| `LOLA_CONFIG`                  | Path to YAML/JSON config file (default `./lola.yaml`)                     | `./lola.yaml`  |
| `LOLA_LOG_LEVEL`              | Log level: `debug`, `info`, `warn`, `error`                               | `info`         |
| `LOLA_LOG_FORMAT`            | Log format: `json` or `console`                                           | `json`         |
| `LOLA_LOG_OUTPUT`            | Log output destination (file path or `stdout`/`stderr`)                   | `stdout`       |
| `LOLA_METRICS_ENABLED`       | Enable Prometheus metrics endpoint                                        | `false`        |
| `LOLA_METRICS_ADDR`          | Metrics listen address                                                    | `:9090`        |
| `LOLA_AUDIT_PATH`            | Audit log file path                                                       | `./lola.audit.log` |
| `LOLA_DEFAULT_CHAIN`         | Default chain ID or name                                                  | `ethereum`     |
| `LOLA_RPC_RETRIES`           | Number of RPC retries on failure                                          | `3`            |
| `LOLA_RPC_BACKOFF`           | Initial backoff duration for RPC retries                                  | `100ms`        |

---

**LOLA OS** – *Configure once, run everywhere.*  
[GitHub](https://github.com/0xSemantic/lola-os) · [Docs](https://github.com/0xSemantic/lola-os/tree/main/docs) · [Discord](https://discord.gg/lola-os)