// Package evm provides public convenience wrappers for EVM operations.
//
// File: sdk/evm/client.go

package evm

import (
	"fmt"
	"context"
	"math/big"

	"github.com/0xSemantic/lola-os/internal/blockchain"
	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
	"github.com/0xSemantic/lola-os/internal/core"
	"github.com/0xSemantic/lola-os/sdk/types"
)

// Client is a high‑level EVM client attached to a runtime session.
type Client struct {
	chain blockchain.Chain
	sess  *core.Session
}

// NewClient creates a new EVM client from a session.
// It is not intended for direct use; use Runtime.EVM() instead.
func NewClient(sess *core.Session) *Client {
	return &Client{
		chain: sess.Chain,
		sess:  sess,
	}
}

// GetBalance returns the wei balance of the given address.
func (c *Client) GetBalance(ctx context.Context, address string, block *types.BlockNumber) (*big.Int, error) {
	if c.chain == nil {
		return nil, fmt.Errorf("evm client: no chain available in session")
	}
	var b blockchain.BlockNumber
	if block != nil {
		b = blockchain.BlockNumber(*block)
	}
	return c.chain.GetBalance(ctx, address, b)
}

// CallContract executes a read‑only contract call.
func (c *Client) CallContract(ctx context.Context, call *types.ContractCall) ([]byte, error) {
	if c.chain == nil {
		return nil, fmt.Errorf("evm client: no chain available in session")
	}
	internalCall := &blockchain.ContractCall{
		To:    call.To,
		Data:  call.Data,
		Value: call.Value,
		Gas:   call.Gas,
	}
	return c.chain.CallContract(ctx, internalCall)
}

// SendTransaction signs and broadcasts a transaction.
// Requires a wallet configured in the runtime.
func (c *Client) SendTransaction(ctx context.Context, tx *types.Transaction) (string, error) {
	if c.chain == nil {
		return "", fmt.Errorf("evm client: no chain available in session")
	}
	internalTx := &blockchain.Transaction{
		To:        tx.To,
		Value:     tx.Value,
		Gas:       tx.Gas,
		GasPrice:  tx.GasPrice,
		GasFeeCap: tx.GasFeeCap,
		GasTipCap: tx.GasTipCap,
		Data:      tx.Data,
		Nonce:     tx.Nonce,
	}
	return c.chain.SendTransaction(ctx, internalTx)
}

// DeployContract deploys a smart contract.
func (c *Client) DeployContract(ctx context.Context, bytecode []byte) (string, string, error) {
	if c.chain == nil {
		return "", "", fmt.Errorf("evm client: no chain available in session")
	}
	// We need to type‑assert to evm.EVMGateway to access DeployContract.
	gw, ok := c.chain.(*evm.EVMGateway)
	if !ok {
		return "", "", fmt.Errorf("evm client: chain is not EVM gateway")
	}
	txHash, addr, err := gw.DeployContract(ctx, bytecode, nil)
	return txHash, addr.Hex(), err
}

// BindContract creates a high‑level contract binding.
func BindContract(ctx context.Context, client *Client, address, abiJSON string) (types.Contract, error) {
	if client.chain == nil {
		return nil, fmt.Errorf("evm client: no chain available")
	}
	gw, ok := client.chain.(*evm.EVMGateway)
	if !ok {
		return nil, fmt.Errorf("evm client: chain is not EVM gateway")
	}
	return evm.NewBoundContract(address, abiJSON, gw)
}

// EOF: sdk/evm/client.go