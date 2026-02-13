// Package evm provides a high‑level contract binding.
//
// File: internal/blockchain/evm/contract.go

package evm

import (
	"context"
	"errors"
	"fmt"
	"strings"

	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/common"

	"github.com/0xSemantic/lola-os/internal/blockchain"
)

// BoundContract implements blockchain.Contract for EVM smart contracts.
type BoundContract struct {
	address common.Address
	abi     abi.ABI
	gateway *EVMGateway
}

// NewBoundContract creates a new contract binding.
// The ABI is parsed at construction; invalid ABI returns an error.
func NewBoundContract(address string, abiJSON string, gateway *EVMGateway) (blockchain.Contract, error) {
	if !common.IsHexAddress(address) {
		return nil, fmt.Errorf("invalid contract address: %s", address)
	}
	addr := common.HexToAddress(address)

	parsedABI, err := abi.JSON(strings.NewReader(abiJSON))
	if err != nil {
		return nil, fmt.Errorf("parse ABI: %w", err)
	}

	return &BoundContract{
		address: addr,
		abi:     parsedABI,
		gateway: gateway,
	}, nil
}

// Call executes a read‑only contract method.
// args are the method parameters, which are ABI‑encoded.
// Returns the decoded return values as a slice of interface{}.
func (c *BoundContract) Call(ctx context.Context, method string, args ...interface{}) ([]interface{}, error) {
	// 1. Look up method in ABI.
	m, ok := c.abi.Methods[method]
	if !ok {
		return nil, fmt.Errorf("method %q not found in ABI", method)
	}

	// 2. Pack the arguments.
	data, err := c.abi.Pack(method, args...)
	if err != nil {
		return nil, fmt.Errorf("pack arguments: %w", err)
	}

	// 3. Construct the call.
	call := &blockchain.ContractCall{
		To:   c.address.Hex(),
		Data: data,
	}

	// 4. Execute call via gateway.
	resultData, err := c.gateway.CallContract(ctx, call)
	if err != nil {
		return nil, fmt.Errorf("contract call: %w", err)
	}

	// 5. Unpack the result.
	// The ABI binding returns a single `*interface{}` or multiple values.
	unpacked, err := m.Outputs.Unpack(resultData)
	if err != nil {
		return nil, fmt.Errorf("unpack result: %w", err)
	}

	// If the method returns a single value, it's often wrapped; we return as slice.
	return unpacked, nil
}

// Transact is not implemented in read‑only mode.
func (c *BoundContract) Transact(ctx context.Context, method string, args ...interface{}) (string, error) {
	return "", errors.New("Transact not implemented in read‑only EVM contract binding")
}

// EOF: internal/blockchain/evm/contract.go