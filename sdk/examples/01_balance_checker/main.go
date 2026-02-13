// Example 01: Simple balance checker.
//
// File: sdk/examples/01_balance_checker/main.go

package main

import (
	"context"
	"fmt"
	"log"

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

// EOF: sdk/examples/01_balance_checker/main.go