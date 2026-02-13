// Package evm provides transaction receipt polling with confirmation handling.
//
// File: internal/blockchain/evm/receipt.go

package evm

import (
	"context"
	"fmt"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
)

// WaitForReceipt polls for a transaction receipt until it is mined or the context is cancelled.
// It waits for the specified number of confirmations (blocks after the receipt block).
// Returns the receipt and the number of blocks it has been confirmed.
func (c *Client) WaitForReceipt(ctx context.Context, txHash common.Hash, confirmations uint64) (*types.Receipt, uint64, error) {
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	var receipt *types.Receipt
	var err error

	for {
		select {
		case <-ctx.Done():
			return nil, 0, ctx.Err()
		case <-ticker.C:
			receipt, err = c.ec.TransactionReceipt(ctx, txHash)
			if err != nil {
				// If not found, continue polling.
				continue
			}
			if receipt != nil {
				// Receipt found; check confirmations.
				currentBlock, err := c.ec.BlockNumber(ctx)
				if err != nil {
					continue
				}
				blocks := currentBlock - receipt.BlockNumber.Uint64()
				if blocks >= confirmations {
					return receipt, blocks, nil
				}
			}
		}
	}
}

// WaitForReceiptWithBackoff polls with exponential backoff.
func (c *Client) WaitForReceiptWithBackoff(ctx context.Context, txHash common.Hash, confirmations uint64) (*types.Receipt, uint64, error) {
	backoff := 500 * time.Millisecond
	maxBackoff := 30 * time.Second
	const factor = 1.5

	for {
		select {
		case <-ctx.Done():
			return nil, 0, ctx.Err()
		default:
		}

		receipt, err := c.ec.TransactionReceipt(ctx, txHash)
		if err == nil && receipt != nil {
			currentBlock, err := c.ec.BlockNumber(ctx)
			if err == nil {
				blocks := currentBlock - receipt.BlockNumber.Uint64()
				if blocks >= confirmations {
					return receipt, blocks, nil
				}
			}
		}

		// Wait before next attempt.
		time.Sleep(backoff)
		backoff = time.Duration(float64(backoff) * factor)
		if backoff > maxBackoff {
			backoff = maxBackoff
		}
	}
}

// EOF: internal/blockchain/evm/receipt.go