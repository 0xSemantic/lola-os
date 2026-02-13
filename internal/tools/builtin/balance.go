// Package builtin provides production‑ready tools that use the blockchain.Chain
// interface from the session. These tools are registered by default.
//
// File: internal/tools/builtin/balance.go

package builtin

import (
	"context"
	"errors"
	"fmt"
	"math/big"

	"github.com/0xSemantic/lola-os/internal/blockchain"
	"github.com/0xSemantic/lola-os/internal/core"
)

// Balance is a tool that returns the native currency balance of an address.
// It expects an "address" argument (string) and an optional "block" argument (string).
// Returns *big.Int.
func Balance(ctx context.Context, args map[string]interface{}) (interface{}, error) {
	// 1. Extract address.
	addrRaw, ok := args["address"]
	if !ok {
		return nil, errors.New("balance: missing 'address' argument")
	}
	address, ok := addrRaw.(string)
	if !ok {
		return nil, errors.New("balance: 'address' must be a string")
	}

	// 2. Extract optional block.
	block := blockchain.BlockNumberLatest
	if blockRaw, ok := args["block"]; ok {
		if blockStr, ok := blockRaw.(string); ok {
			block = blockchain.BlockNumber(blockStr)
		} else {
			return nil, errors.New("balance: 'block' must be a string")
		}
	}

	// 3. Get session and chain.
	sess := core.SessionFromContext(ctx)
	if sess == nil {
		return nil, errors.New("balance: no session in context")
	}
	if sess.Chain == nil {
		return nil, errors.New("balance: no blockchain chain available in session")
	}

	// 4. Call GetBalance.
	bal, err := sess.Chain.GetBalance(ctx, address, block)
	if err != nil {
		return nil, fmt.Errorf("balance: %w", err)
	}

	return bal, nil
}

// EOF: internal/tools/builtin/balance.go