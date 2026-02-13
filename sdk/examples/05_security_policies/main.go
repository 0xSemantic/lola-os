// Example 05: Security Policies
// Demonstrates configuring daily limits and whitelist via lola.yaml.
// This agent will attempt to send ETH and be blocked by policies.
//
// File: sdk/examples/05_security_policies/main.go

package main

import (
	"context"
	"fmt"
	"log"
	"math/big"

	"github.com/0xSemantic/lola-os/sdk"
)

func main() {
	// Load configuration from lola.yaml (expected to have security policies)
	rt := sdk.Init(sdk.WithConfigFile("./lola.yaml"))

	err := rt.Run(context.Background(), func(ctx context.Context, rt *sdk.Runtime) error {
		evm, err := rt.EVM(ctx)
		if err != nil {
			return err
		}

		// Attempt to send 0.6 ETH (above threshold)
		to := "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7"
		amount := big.NewInt(600000000000000000) // 0.6 ETH
		txHash, err := evm.SendTransaction(ctx, &sdktypes.Transaction{
			To:    &to,
			Value: amount,
		})
		if err != nil {
			// Expected to be blocked by HITL or limit policy.
			fmt.Printf("Transaction blocked: %v\n", err)
			return nil
		}
		fmt.Printf("Transaction sent: %s\n", txHash)
		return nil
	})

	if err != nil {
		log.Fatal(err)
	}
}

// EOF: sdk/examples/05_security_policies/main.go