// Package builtin provides production‑ready tools for onchain operations.
//
// File: internal/tools/builtin/transfer.go

package builtin

import (
	"context"
	"errors"
	"fmt"
	"math/big"

	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
	"github.com/0xSemantic/lola-os/internal/core"
)

// Transfer sends native currency to an address.
// Arguments:
//   - to:      recipient address (string)
//   - amount:  amount in wei (*big.Int)
//   - gas:     optional gas limit (uint64)
//   - gasPrice: optional gas price (*big.Int) – legacy
// Returns transaction hash (string).
func Transfer(ctx context.Context, args map[string]interface{}) (interface{}, error) {
	// Extract arguments.
	toRaw, ok := args["to"]
	if !ok {
		return nil, errors.New("transfer: missing 'to' argument")
	}
	to, ok := toRaw.(string)
	if !ok {
		return nil, errors.New("transfer: 'to' must be string")
	}

	amountRaw, ok := args["amount"]
	if !ok {
		return nil, errors.New("transfer: missing 'amount' argument")
	}
	amount, ok := amountRaw.(*big.Int)
	if !ok {
		return nil, errors.New("transfer: 'amount' must be *big.Int")
	}

	// Optional gas.
	var gas uint64
	if gasRaw, ok := args["gas"]; ok {
		if g, ok := gasRaw.(uint64); ok {
			gas = g
		}
	}

	// Optional gas price.
	var gasPrice *big.Int
	if gpRaw, ok := args["gasPrice"]; ok {
		if gp, ok := gpRaw.(*big.Int); ok {
			gasPrice = gp
		}
	}

	// Get session and chain.
	sess := core.SessionFromContext(ctx)
	if sess == nil {
		return nil, errors.New("transfer: no session in context")
	}
	evmChain, ok := sess.Chain.(*evm.EVMGateway)
	if !ok {
		return nil, errors.New("transfer: chain is not an EVM gateway")
	}

	// Send transaction.
	txHash, err := evmChain.SendTransaction(ctx, &blockchain.Transaction{
		To:       &to,
		Value:    amount,
		Gas:      gas,
		GasPrice: gasPrice,
	})
	if err != nil {
		return nil, fmt.Errorf("transfer: %w", err)
	}
	return txHash, nil
}

// EOF: internal/tools/builtin/transfer.go