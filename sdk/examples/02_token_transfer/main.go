// Example 02: Send ETH.
//
// File: sdk/examples/02_token_transfer/main.go

package main

import (
	"context"
	"fmt"
	"log"
	"math/big"

	"github.com/0xSemantic/lola-os/sdk"
	"github.com/0xSemantic/lola-os/sdk/types"
)

func main() {
	rt := sdk.Init()

	err := rt.Run(context.Background(), func(ctx context.Context, rt *sdk.Runtime) error {
		evm, err := rt.EVM(ctx)
		if err != nil {
			return err
		}
		to := "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7"
		amount := big.NewInt(1000000000000000) // 0.001 ETH
		txHash, err := evm.SendTransaction(ctx, &sdktypes.Transaction{
			To:    &to,
			Value: amount,
		})
		if err != nil {
			return err
		}
		fmt.Printf("Transaction sent: %s\n", txHash)
		return nil
	})

	if err != nil {
		log.Fatal(err)
	}
}

// EOF: sdk/examples/02_token_transfer/main.go