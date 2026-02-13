# LOLA OS Quickstart

**Get your first agent onchain in 10 minutes.**  
No blockchain experience required. No framework rewrite. Just Go.

---

## 1. Prerequisites

- **Go 1.24+** ([install](https://go.dev/dl/))
- An EVM RPC endpoint (Infura, Alchemy, or a local node)

---

## 2. Install the SDK

```bash
go get github.com/0xSemantic/lola-os/sdk
```

---

## 3. Minimal Configuration

Create a `.env` file in your project root (copy from [`.env.example`](.env.example)):

```bash
# Ethereum Mainnet (replace with your own RPC URL)
ETH_MAINNET_RPC=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
```

That’s it. LOLA OS will automatically detect the available chains and operate in **read‑only mode** (no private key needed).

---

## 4. Write Your First Agent

Create a file `main.go`:

```go
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/0xSemantic/lola-os/sdk"
)

func main() {
	// Initialize the LOLA OS runtime (reads .env automatically)
	rt := sdk.Init()

	// Run your agent logic inside a session
	err := rt.Run(context.Background(), func(ctx context.Context, rt *sdk.Runtime) error {
		// Get an EVM client for the default chain
		evm, err := rt.EVM(ctx)
		if err != nil {
			return err
		}

		// Check the balance of a famous Ethereum address
		balance, err := evm.GetBalance(ctx, "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7", nil)
		if err != nil {
			return err
		}

		fmt.Printf("Balance: %s wei\n", balance.String())
		return nil
	})

	if err != nil {
		log.Fatal(err)
	}
}
```

---

## 5. Run It

```bash
go run main.go
```

**Expected output** (your balance may differ):
```
Balance: 1234567890000000000 wei
```

---

## 6. What Just Happened?

- LOLA OS read your `.env` file and connected to Ethereum mainnet.
- It created a **session** (automatically logged with a unique ID).
- The `GetBalance` call was executed with automatic retries, structured logging, and a security policy check (none were configured, so it passed).
- The result was printed, and the session closed gracefully.

All RPC calls are logged in JSON format to stdout. You can see them by running with `LOLA_LOG_LEVEL=debug`.

---

## 7. Next Steps

- **Send a transaction** – Add a private key to your `.env` and use `evm.SendTransaction()`.
- **Register custom tools** – See the [custom tool example](sdk/examples/03_custom_tool).
- **Configure security policies** – Create a `lola.yaml` file to set daily limits, whitelist addresses, or enable human‑in‑the‑loop.
- **Explore the case studies** – Real‑world agents you can copy and adapt:
  - [LiquidityBot](https://github.com/0xSemantic/lola-liquiditybot) – Uniswap V3 position manager
  - [TreasuryWatch](https://github.com/0xSemantic/lola-treasurywatch) – DAO treasury monitor
  - [Veritas](https://github.com/0xSemantic/lola-veritas) – On‑chain research assistant
  - [MintSync](https://github.com/0xSemantic/lola-mintsync) – NFT mint coordinator
  - [ChainAudit](https://github.com/0xSemantic/lola-chainaudit) – Supply chain ESG auditor

---

## 8. Need Help?

- 📖 [Full Documentation](https://lolaos.online/docs)
- 💬 [Discord Community](https://discord.gg/lola-os)
- 🐦 [Twitter @0xSemantic](https://twitter.com/0xSemantic)
- 🐛 [GitHub Issues](https://github.com/0xSemantic/lola-os/issues)

---

**LOLA OS** – *Make every agent blockchain-native.*  
`github.com/0xSemantic/lola-os` · Apache 2.0