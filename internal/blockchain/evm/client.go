// Package evm provides a production‑grade EVM blockchain adapter.
// It implements the Chain interface using go-ethereum and adds
// connection pooling, retry logic, and full observability.
//
// Key types:
//   - Client   : thread‑safe RPC client with retries and logging.
//   - EVMGateway : implements blockchain.Chain (see gateway.go).
//
// File: internal/blockchain/evm/client.go

package evm

import (
	"context"
	"errors"
	"fmt"
	"math/big"
	"time"

	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"

	"github.com/0xSemantic/lola-os/internal/observe"
)

// RetryConfig defines the policy for retrying RPC calls.
type RetryConfig struct {
	MaxAttempts     int
	InitialBackoff  time.Duration
	MaxBackoff      time.Duration
	BackoffFactor   float64
}

// DefaultRetryConfig is the recommended retry policy.
var DefaultRetryConfig = RetryConfig{
	MaxAttempts:    3,
	InitialBackoff: 100 * time.Millisecond,
	MaxBackoff:     2 * time.Second,
	BackoffFactor:  2.0,
}

// Client is a thread‑safe wrapper around ethclient.Client with retry and logging.
type Client struct {
	rpcURL string
	ec     *ethclient.Client
	logger observe.Logger
	retry  RetryConfig
}

// NewClient creates a new EVM RPC client.
// It establishes the connection immediately; if the connection fails,
// the error is returned and the client is unusable.
func NewClient(ctx context.Context, rpcURL string, logger observe.Logger, retry *RetryConfig) (*Client, error) {
	ec, err := ethclient.DialContext(ctx, rpcURL)
	if err != nil {
		return nil, fmt.Errorf("evm client: dial %s: %w", rpcURL, err)
	}

	if retry == nil {
		retry = &DefaultRetryConfig
	}
	if retry.MaxAttempts <= 0 {
		retry.MaxAttempts = 1
	}
	if retry.InitialBackoff <= 0 {
		retry.InitialBackoff = 100 * time.Millisecond
	}
	if retry.MaxBackoff <= 0 {
		retry.MaxBackoff = 2 * time.Second
	}
	if retry.BackoffFactor <= 0 {
		retry.BackoffFactor = 2.0
	}

	return &Client{
		rpcURL: rpcURL,
		ec:     ec,
		logger: logger,
		retry:  *retry,
	}, nil
}

// NewClientFromEthClient creates a client from an existing ethclient.Client (for testing).
func NewClientFromEthClient(ec *ethclient.Client, logger observe.Logger, retry *RetryConfig) *Client {
    if retry == nil {
        retry = &DefaultRetryConfig
    }
    return &Client{
        ec:     ec,
        logger: logger,
        retry:  *retry,
    }
}

// Close terminates the underlying RPC connection.
func (c *Client) Close() {
	c.ec.Close()
}

// withRetry executes an RPC call with exponential backoff.
// It logs each attempt and final error.
func (c *Client) withRetry(ctx context.Context, operation string, fn func() (interface{}, error)) (interface{}, error) {
	var lastErr error
	backoff := c.retry.InitialBackoff

	for attempt := 1; attempt <= c.retry.MaxAttempts; attempt++ {
		// Attempt the call.
		result, err := fn()
		if err == nil {
			c.logger.Debug("RPC call succeeded",
				map[string]interface{}{
					"operation": operation,
					"attempt":   attempt,
				})
			return result, nil
		}

		lastErr = err
		c.logger.Warn("RPC call failed",
			map[string]interface{}{
				"operation": operation,
				"attempt":   attempt,
				"error":     err.Error(),
			})

		// If last attempt, break out.
		if attempt == c.retry.MaxAttempts {
			break
		}

		// Wait for backoff, respecting context cancellation.
		timer := time.NewTimer(backoff)
		select {
		case <-ctx.Done():
			timer.Stop()
			return nil, ctx.Err()
		case <-timer.C:
		}

		// Increase backoff.
		backoff = time.Duration(float64(backoff) * c.retry.BackoffFactor)
		if backoff > c.retry.MaxBackoff {
			backoff = c.retry.MaxBackoff
		}
	}

	return nil, fmt.Errorf("%s: %w after %d attempts", operation, lastErr, c.retry.MaxAttempts)
}

// BalanceAt returns the wei balance of the given address at the specified block.
func (c *Client) BalanceAt(ctx context.Context, address common.Address, block *big.Int) (*big.Int, error) {
	result, err := c.withRetry(ctx, "BalanceAt", func() (interface{}, error) {
		return c.ec.BalanceAt(ctx, address, block)
	})
	if err != nil {
		return nil, err
	}
	return result.(*big.Int), nil
}

// CallContract executes a message call and returns the raw result data.
func (c *Client) CallContract(ctx context.Context, call ethereum.CallMsg, block *big.Int) ([]byte, error) {
	result, err := c.withRetry(ctx, "CallContract", func() (interface{}, error) {
		return c.ec.CallContract(ctx, call, block)
	})
	if err != nil {
		return nil, err
	}
	return result.([]byte), nil
}

// ChainID retrieves the chain ID of the connected network.
func (c *Client) ChainID(ctx context.Context) (*big.Int, error) {
	result, err := c.withRetry(ctx, "ChainID", func() (interface{}, error) {
		return c.ec.ChainID(ctx)
	})
	if err != nil {
		return nil, err
	}
	return result.(*big.Int), nil
}

// BlockNumber returns the number of the most recent block.
func (c *Client) BlockNumber(ctx context.Context) (uint64, error) {
	result, err := c.withRetry(ctx, "BlockNumber", func() (interface{}, error) {
		return c.ec.BlockNumber(ctx)
	})
	if err != nil {
		return 0, err
	}
	return result.(uint64), nil
}

// EstimateGas tries to estimate the gas needed for a transaction or call.
func (c *Client) EstimateGas(ctx context.Context, call ethereum.CallMsg) (uint64, error) {
	result, err := c.withRetry(ctx, "EstimateGas", func() (interface{}, error) {
		return c.ec.EstimateGas(ctx, call)
	})
	if err != nil {
		return 0, err
	}
	return result.(uint64), nil
}

// PendingNonceAt returns the account nonce of the given address in the pending state.
// This is needed for write operations (Phase 3).
func (c *Client) PendingNonceAt(ctx context.Context, address common.Address) (uint64, error) {
	result, err := c.withRetry(ctx, "PendingNonceAt", func() (interface{}, error) {
		return c.ec.PendingNonceAt(ctx, address)
	})
	if err != nil {
		return 0, err
	}
	return result.(uint64), nil
}

// SuggestGasPrice retrieves the currently suggested gas price.
func (c *Client) SuggestGasPrice(ctx context.Context) (*big.Int, error) {
	result, err := c.withRetry(ctx, "SuggestGasPrice", func() (interface{}, error) {
		return c.ec.SuggestGasPrice(ctx)
	})
	if err != nil {
		return nil, err
	}
	return result.(*big.Int), nil
}

// SuggestGasTipCap retrieves the currently suggested EIP‑1559 priority fee.
func (c *Client) SuggestGasTipCap(ctx context.Context) (*big.Int, error) {
	result, err := c.withRetry(ctx, "SuggestGasTipCap", func() (interface{}, error) {
		return c.ec.SuggestGasTipCap(ctx)
	})
	if err != nil {
		return nil, err
	}
	return result.(*big.Int), nil
}

// EOF: internal/blockchain/evm/client.go