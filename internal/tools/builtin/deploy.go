// Package builtin provides contract deployment tool.
//
// File: internal/tools/builtin/deploy.go

package builtin

import (
	"context"
	"errors"
	"fmt"

	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
	"github.com/0xSemantic/lola-os/internal/core"
	"encoding/hex"
)

// Deploy deploys a smart contract.
// Arguments:
//   - bytecode: contract creation bytecode (hex string or []byte)
//   - gas:      optional gas limit (uint64)
// Returns: map[string]interface{} with "tx_hash" and "contract_address".
func Deploy(ctx context.Context, args map[string]interface{}) (interface{}, error) {
	// Extract bytecode.
	var bytecode []byte
	switch v := args["bytecode"].(type) {
	case string:
		var err error
		bytecode, err = hex.DecodeString(v)
		if err != nil {
			return nil, fmt.Errorf("deploy: decode hex bytecode: %w", err)
		}
	case []byte:
		bytecode = v
	default:
		return nil, errors.New("deploy: 'bytecode' must be string or []byte")
	}

	// Optional gas.
	var gas uint64
	if gasRaw, ok := args["gas"]; ok {
		if g, ok := gasRaw.(uint64); ok {
			gas = g
		}
	}

	// Get session and chain.
	sess := core.SessionFromContext(ctx)
	if sess == nil {
		return nil, errors.New("deploy: no session in context")
	}
	evmChain, ok := sess.Chain.(*evm.EVMGateway)
	if !ok {
		return nil, errors.New("deploy: chain is not an EVM gateway")
	}

	// Deploy.
	txHash, contractAddr, err := evmChain.DeployContract(ctx, bytecode, &evm.TxOpts{GasLimit: gas})
	if err != nil {
		return nil, fmt.Errorf("deploy: %w", err)
	}

	return map[string]interface{}{
		"tx_hash":          txHash,
		"contract_address": contractAddr.Hex(),
	}, nil
}

// EOF: internal/tools/builtin/deploy.go