// Example 04: Multi‑Chain USDC Balance Scanner
// Demonstrates iterating over multiple chains and fetching token balances.
//
// File: sdk/examples/04_multi_chain/main.go

package main

import (
	"context"
	"fmt"
	"log"
	"math/big"
	"strings"

	"github.com/0xSemantic/lola-os/sdk"
	"github.com/0xSemantic/lola-os/sdk/evm"
)

// ERC‑20 ABI (balanceOf)
const erc20ABI = `[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]`

// USDC addresses on different chains.
var usdcAddresses = map[string]string{
	"ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
	"polygon":  "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
	"arbitrum": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
	"optimism": "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",
	"base":     "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
}

func main() {
	rt := sdk.Init()

	err := rt.Run(context.Background(), func(ctx context.Context, rt *sdk.Runtime) error {
		// Get list of configured chains from runtime config.
		chains := rt.Config().Chains // we need to expose Config() on Runtime
		// We'll add this method.
		
		for chainID := range usdcAddresses {
			// Check if this chain is configured.
			if _, ok := chains[chainID]; !ok {
				continue
			}

			evmClient, err := rt.EVM(ctx)
			if err != nil {
				log.Printf("Skipping %s: %v", chainID, err)
				continue
			}

			// Create contract binding.
			contract, err := evm.BindContract(ctx, evmClient, usdcAddresses[chainID], erc20ABI)
			if err != nil {
				log.Printf("Failed to bind USDC on %s: %v", chainID, err)
				continue
			}

			// Call balanceOf.
			result, err := contract.Call(ctx, "balanceOf", "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7")
			if err != nil {
				log.Printf("Failed to get balance on %s: %v", chainID, err)
				continue
			}

			balance := result[0].(*big.Int)
			fmt.Printf("%s USDC balance: %s\n", strings.Title(chainID), balance.String())
		}
		return nil
	})

	if err != nil {
		log.Fatal(err)
	}
}

// EOF: sdk/examples/04_multi_chain/main.go