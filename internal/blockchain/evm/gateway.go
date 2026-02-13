// Package evm implements the blockchain.Chain interface for EVM‑compatible chains.
//
// File: internal/blockchain/evm/gateway.go

package evm

import (
	"context"
	"errors"
	"fmt"
	"math/big"

	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/common"

	"github.com/0xSemantic/lola-os/internal/blockchain"
	"github.com/0xSemantic/lola-os/internal/observe"
)

// EVMGateway is a production‑grade implementation of blockchain.Chain
// for EVM networks. It uses an internal Client for RPC communication.
type EVMGateway struct {
	client *Client
	logger observe.Logger
	wallet blockchain.Wallet // added for write operations
}

// NewEVMGateway creates a new gateway for a specific RPC endpoint.
// It establishes the connection immediately.
func NewEVMGateway(ctx context.Context, rpcURL string, logger observe.Logger, retry *RetryConfig, wallet blockchain.Wallet) (*EVMGateway, error) {
	client, err := NewClient(ctx, rpcURL, logger, retry)
	if err != nil {
		return nil, err
	}
	return &EVMGateway{
		client: client,
		logger: logger,
		wallet: wallet,
	}, nil
}

// Close terminates the underlying RPC connection.
func (g *EVMGateway) Close() {
	g.client.Close()
}

// SetClient replaces the underlying client (for testing only).
func (g *EVMGateway) SetClient(client *Client) {
	g.client = client
}

// GetBalance returns the balance of the given address at the specified block.
// If block is nil, the latest block is used.
func (g *EVMGateway) GetBalance(ctx context.Context, address string, block blockchain.BlockNumber) (*big.Int, error) {
	g.logger.Debug("GetBalance called", map[string]interface{}{
		"address": address,
		"block":   block,
	})

	if !common.IsHexAddress(address) {
		return nil, fmt.Errorf("invalid address format: %s", address)
	}
	addr := common.HexToAddress(address)

	var blockNum *big.Int
	if block != "" {
		switch block {
		case blockchain.BlockNumberLatest, blockchain.BlockNumberPending, blockchain.BlockNumberEarliest:
			blockNum = nil // ethclient interprets nil as latest/pending
		default:
			// Try to parse as decimal or hex.
			blockNum = new(big.Int)
			_, ok := blockNum.SetString(string(block), 0)
			if !ok {
				return nil, fmt.Errorf("invalid block number format: %s", block)
			}
		}
	}

	bal, err := g.client.BalanceAt(ctx, addr, blockNum)
	if err != nil {
		return nil, fmt.Errorf("GetBalance: %w", err)
	}
	return bal, nil
}

// SendTransaction is not implemented in read‑only mode.
func (g *EVMGateway) SendTransaction(ctx context.Context, tx *blockchain.Transaction) (string, error) {
	return "", errors.New("SendTransaction not implemented in read‑only EVM gateway")
}

// CallContract executes a message call without creating a transaction.
func (g *EVMGateway) CallContract(ctx context.Context, call *blockchain.ContractCall) ([]byte, error) {
	g.logger.Debug("CallContract called", map[string]interface{}{
		"to":    call.To,
		"value": call.Value,
		"gas":   call.Gas,
		"data":  common.Bytes2Hex(call.Data),
	})

	if !common.IsHexAddress(call.To) {
		return nil, fmt.Errorf("invalid contract address: %s", call.To)
	}
	to := common.HexToAddress(call.To)

	msg := ethereum.CallMsg{
		To:    &to,
		Data:  call.Data,
		Value: call.Value,
		Gas:   call.Gas,
	}

	data, err := g.client.CallContract(ctx, msg, nil) // always latest block for calls
	if err != nil {
		return nil, fmt.Errorf("CallContract: %w", err)
	}
	return data, nil
}

// ChainID returns the chain ID of the connected network.
func (g *EVMGateway) ChainID(ctx context.Context) (*big.Int, error) {
	id, err := g.client.ChainID(ctx)
	if err != nil {
		return nil, fmt.Errorf("ChainID: %w", err)
	}
	return id, nil
}

// BlockNumber returns the number of the most recent block.
func (g *EVMGateway) BlockNumber(ctx context.Context) (uint64, error) {
	num, err := g.client.BlockNumber(ctx)
	if err != nil {
		return 0, fmt.Errorf("BlockNumber: %w", err)
	}
	return num, nil
}

// EstimateGas tries to estimate the gas needed for a transaction or call.
func (g *EVMGateway) EstimateGas(ctx context.Context, call *blockchain.ContractCall) (uint64, error) {
	g.logger.Debug("EstimateGas called", map[string]interface{}{
		"to":    call.To,
		"value": call.Value,
		"data":  common.Bytes2Hex(call.Data),
	})

	if !common.IsHexAddress(call.To) {
		return 0, fmt.Errorf("invalid contract address: %s", call.To)
	}
	to := common.HexToAddress(call.To)

	msg := ethereum.CallMsg{
		To:    &to,
		Data:  call.Data,
		Value: call.Value,
	}

	gas, err := g.client.EstimateGas(ctx, msg)
	if err != nil {
		return 0, fmt.Errorf("EstimateGas: %w", err)
	}
	return gas, nil
}

// SendTransaction implements blockchain.Chain.
// It builds, signs, and broadcasts a transaction using the provided wallet.
// If the gateway does not have a wallet, an error is returned.
func (g *EVMGateway) SendTransaction(ctx context.Context, tx *blockchain.Transaction) (string, error) {
	if g.wallet == nil {
		return "", errors.New("SendTransaction: no wallet configured, read‑only mode")
	}

	builder, err := NewTxBuilder(ctx, g.client, g.wallet)
	if err != nil {
		return "", fmt.Errorf("SendTransaction: create tx builder: %w", err)
	}

	// Convert blockchain.Transaction to builder options.
	opts := &TxOpts{
		GasLimit:    tx.Gas,
		GasPrice:    tx.GasPrice,
		GasFeeCap:   tx.GasFeeCap,
		GasTipCap:   tx.GasTipCap,
		Nonce:       tx.Nonce,
		DynamicFee:  tx.GasFeeCap != nil || tx.GasTipCap != nil,
	}

	var signedTx *types.Transaction
	if tx.To == nil {
		// Contract deployment.
		signedTx, err = builder.BuildDeploy(ctx, tx.Data, opts)
	} else {
		// Transfer or contract call.
		signedTx, err = builder.BuildContractCall(ctx, *tx.To, tx.Data, tx.Value, opts)
	}
	if err != nil {
		return "", fmt.Errorf("SendTransaction: build tx: %w", err)
	}

	// Broadcast.
	err = g.client.ec.SendTransaction(ctx, signedTx)
	if err != nil {
		return "", fmt.Errorf("SendTransaction: send: %w", err)
	}

	return signedTx.Hash().Hex(), nil
}

// DeployContract is a convenience method for contract deployment.
// It is equivalent to SendTransaction with To = nil.
func (g *EVMGateway) DeployContract(ctx context.Context, data []byte, opts *TxOpts) (string, common.Address, error) {
	if g.wallet == nil {
		return "", common.Address{}, errors.New("DeployContract: no wallet configured, read‑only mode")
	}

	builder, err := NewTxBuilder(ctx, g.client, g.wallet)
	if err != nil {
		return "", common.Address{}, fmt.Errorf("DeployContract: create tx builder: %w", err)
	}

	signedTx, err := builder.BuildDeploy(ctx, data, opts)
	if err != nil {
		return "", common.Address{}, fmt.Errorf("DeployContract: build tx: %w", err)
	}

	err = g.client.ec.SendTransaction(ctx, signedTx)
	if err != nil {
		return "", common.Address{}, fmt.Errorf("DeployContract: send: %w", err)
	}

	// Compute contract address from sender and nonce.
	contractAddress := crypto.CreateAddress(builder.address, signedTx.Nonce())
	return signedTx.Hash().Hex(), contractAddress, nil
}

// SetWallet assigns a wallet to the gateway, enabling write operations.
func (g *EVMGateway) SetWallet(wallet blockchain.Wallet) {
	g.wallet = wallet
}

// Wallet returns the currently configured wallet, or nil if none.
func (g *EVMGateway) Wallet() blockchain.Wallet {
	return g.wallet
}

// EOF: internal/blockchain/evm/gateway.go