// Package types provides public types for LOLA OS SDK users.
//
// File: sdk/types/chain.go

package types

import (
	"math/big"
)

// BlockNumber represents a block identifier.
type BlockNumber string

const (
	BlockNumberLatest   BlockNumber = "latest"
	BlockNumberPending  BlockNumber = "pending"
	BlockNumberEarliest BlockNumber = "earliest"
)

// Transaction represents a blockchain transaction.
type Transaction struct {
	To        *string  `json:"to"`
	Value     *big.Int `json:"value"`
	Gas       uint64   `json:"gas"`
	GasPrice  *big.Int `json:"gasPrice"`
	GasFeeCap *big.Int `json:"maxFeePerGas"`
	GasTipCap *big.Int `json:"maxPriorityFeePerGas"`
	Data      []byte   `json:"data"`
	Nonce     *uint64  `json:"nonce"`
}

// ContractCall represents a message call.
type ContractCall struct {
	To    string   `json:"to"`
	Data  []byte   `json:"data"`
	Value *big.Int `json:"value"`
	Gas   uint64   `json:"gas"`
}

// EOF: sdk/types/chain.go