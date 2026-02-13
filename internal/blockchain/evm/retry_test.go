// Package evm_test tests retry logic and failure injection.
//
// File: internal/blockchain/evm/retry_test.go

package evm_test

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/common"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
	"github.com/0xSemantic/lola-os/internal/observe"
)

// failingRPCClient simulates an RPC client that fails a specified number of times.
type failingRPCClient struct {
	failCount   int
	attempts    int
	shouldFail  bool
}

func (f *failingRPCClient) ChainID(ctx context.Context) (*big.Int, error) {
	f.attempts++
	if f.failCount > 0 {
		f.failCount--
		return nil, errors.New("simulated RPC failure")
	}
	return big.NewInt(1), nil
}

// We need to embed a real ethclient.Client? This is tricky.
// Instead, we can create a mock Client that implements the methods we need.
// For simplicity, we'll use testify/mock and mock the client.

import (
	"github.com/stretchr/testify/mock"
)

type mockEthClient struct {
	mock.Mock
}

func (m *mockEthClient) ChainID(ctx context.Context) (*big.Int, error) {
	args := m.Called(ctx)
	return args.Get(0).(*big.Int), args.Error(1)
}

func (m *mockEthClient) Close() {}

func TestClient_WithRetry_SuccessAfterRetries(t *testing.T) {
	mockEC := new(mockEthClient)
	mockEC.On("ChainID", mock.Anything).Return(big.NewInt(1), nil).Once()
	// First two calls fail.
	mockEC.On("ChainID", mock.Anything).Return((*big.Int)(nil), errors.New("RPC failed")).Twice()

	client := &evm.Client{
		ec:     mockEC,
		logger: &observe.NoopLogger{},
		retry: evm.RetryConfig{
			MaxAttempts:    3,
			InitialBackoff: 1 * time.Millisecond,
			MaxBackoff:     5 * time.Millisecond,
			BackoffFactor:  2.0,
		},
	}

	ctx := context.Background()
	chainID, err := client.ChainID(ctx)
	require.NoError(t, err)
	assert.Equal(t, big.NewInt(1), chainID)

	mockEC.AssertNumberOfCalls(t, "ChainID", 3)
}

func TestClient_WithRetry_Exhausted(t *testing.T) {
	mockEC := new(mockEthClient)
	// All three calls fail.
	mockEC.On("ChainID", mock.Anything).Return((*big.Int)(nil), errors.New("RPC failed")).Times(3)

	client := &evm.Client{
		ec:     mockEC,
		logger: &observe.NoopLogger{},
		retry: evm.RetryConfig{
			MaxAttempts:    3,
			InitialBackoff: 1 * time.Millisecond,
			MaxBackoff:     5 * time.Millisecond,
			BackoffFactor:  2.0,
		},
	}

	ctx := context.Background()
	_, err := client.ChainID(ctx)
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "after 3 attempts")

	mockEC.AssertNumberOfCalls(t, "ChainID", 3)
}

func TestClient_WithRetry_ContextCancel(t *testing.T) {
	mockEC := new(mockEthClient)
	mockEC.On("ChainID", mock.Anything).Return((*big.Int)(nil), errors.New("RPC failed")).Maybe()

	client := &evm.Client{
		ec:     mockEC,
		logger: &observe.NoopLogger{},
		retry: evm.RetryConfig{
			MaxAttempts:    5,
			InitialBackoff: 10 * time.Millisecond,
			MaxBackoff:     50 * time.Millisecond,
			BackoffFactor:  2.0,
		},
	}

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Millisecond)
	defer cancel()

	_, err := client.ChainID(ctx)
	assert.ErrorIs(t, err, context.DeadlineExceeded)
}

// EOF: internal/blockchain/evm/retry_test.go