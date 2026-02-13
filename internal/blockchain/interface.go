// Package blockchain defines the core interfaces for interacting with
// distributed ledger technologies. It provides the abstractions that
// allow LOLA OS to be chain‑agnostic.
//
// Key types:
//   - Chain       : read/write operations common to all blockchains.
//   - Wallet      : signing and address derivation.
//   - Contract    : high‑level interaction with smart contracts.
//
// All implementations of these interfaces must be safe for concurrent use.
//
// File: internal/blockchain/interface.go

package blockchain

import (
	"context"
	"math/big"
)

// BlockNumber represents a block identifier.
// It can be a decimal/hex string, a *big.Int, or one of the predefined
// constants: "latest", "pending", "earliest".
type BlockNumber string

const (
	BlockNumberLatest    BlockNumber = "latest"
	BlockNumberPending   BlockNumber = "pending"
	BlockNumberEarliest  BlockNumber = "earliest"
)

// Transaction represents a blockchain transaction to be signed and broadcast.
// All fields are optional; nil values indicate the field should be omitted
// or automatically estimated by the node.
type Transaction struct {
	To        *string  `json:"to"`         // nil for contract creation
	Value     *big.Int `json:"value"`      // amount of native currency
	Gas       uint64   `json:"gas"`        // gas limit
	GasPrice  *big.Int `json:"gasPrice"`   // legacy gas price
	GasFeeCap *big.Int `json:"maxFeePerGas"`   // EIP‑1559 fee cap
	GasTipCap *big.Int `json:"maxPriorityFeePerGas"` // EIP‑1559 tip
	Data      []byte   `json:"data"`       // input data
	Nonce     *uint64  `json:"nonce"`      // account nonce
}

// ContractCall represents a message call that does not create a transaction.
// It is used for eth_call and similar read‑only operations.
type ContractCall struct {
	To    string   `json:"to"`    // target contract address
	Data  []byte   `json:"data"`  // encoded call data
	Value *big.Int `json:"value"` // native currency sent with the call
	Gas   uint64   `json:"gas"`   // gas limit (optional)
}

// Chain defines the set of operations a blockchain must support.
type Chain interface {
	// GetBalance returns the balance of the given address at the specified block.
	GetBalance(ctx context.Context, address string, block BlockNumber) (*big.Int, error)

	// SendTransaction signs and broadcasts a transaction.
	// Returns the transaction hash.
	SendTransaction(ctx context.Context, tx *Transaction) (string, error)

	// CallContract executes a message call without creating a transaction.
	// The returned byte slice is the raw response data.
	CallContract(ctx context.Context, call *ContractCall) ([]byte, error)

	// ChainID returns the unique identifier of the chain.
	ChainID(ctx context.Context) (*big.Int, error)

	// BlockNumber returns the number of the most recent block.
	BlockNumber(ctx context.Context) (uint64, error)

	// EstimateGas tries to estimate the gas needed for a transaction or call.
	EstimateGas(ctx context.Context, call *ContractCall) (uint64, error)
}

// Wallet is responsible for cryptographic signing and address management.
type Wallet interface {
	// Sign signs the provided digest (usually a transaction hash).
	// Returns the raw signature bytes.
	Sign(digest []byte) ([]byte, error)

	// Address returns the wallet's public address as a hex‑encoded string.
	Address() string
}

// Contract provides a convenient, type‑safe interface for interacting with
// a deployed smart contract. It requires an ABI definition to encode/decode calls.
type Contract interface {
	// Call executes a read‑only contract method.
	// args are the method parameters, which will be ABI‑encoded.
	// Returns the decoded return values as a slice of interface{}.
	Call(ctx context.Context, method string, args ...interface{}) ([]interface{}, error)

	// Transact creates and sends a transaction that invokes a contract method.
	// Returns the transaction hash.
	Transact(ctx context.Context, method string, args ...interface{}) (string, error)
}

// EOF: internal/blockchain/interface.go