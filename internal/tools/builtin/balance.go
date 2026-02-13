// Package builtin provides placeholder implementations of common onchain tools.
// These tools do NOT connect to real blockchains; they return deterministic
// mock responses suitable for testing and demonstration.
//
// File: internal/tools/builtin/balance.go

package builtin

import (
	"context"
	"math/big"
)

// Balance is a placeholder tool that simulates checking an account balance.
// It always returns 100 ETH (1e18 wei) for any address.
func Balance(ctx context.Context, args map[string]interface{}) (interface{}, error) {
	// In a real implementation we would extract the address from args.
	// Here we ignore it and return a fixed balance.
	return big.NewInt(1e18), nil
}

// EOF: internal/tools/builtin/balance.go