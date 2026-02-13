// Package types provides contract ABI types.
//
// File: sdk/types/contract.go

package types

// Contract is a high‑level binding to a deployed smart contract.
type Contract interface {
	// Call executes a read‑only contract method.
	Call(ctx context.Context, method string, args ...interface{}) ([]interface{}, error)

	// Transact creates and sends a transaction that invokes a contract method.
	Transact(ctx context.Context, method string, args ...interface{}) (string, error)
}

// EOF: sdk/types/contract.go