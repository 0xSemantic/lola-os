// Package builtin_test verifies the built‑in tools.
//
// File: internal/tools/builtin/builtin_test.go

package builtin_test

import (
	"context"
	"math/big"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/blockchain"
	"github.com/0xSemantic/lola-os/internal/core"
	"github.com/0xSemantic/lola-os/internal/observe"
	"github.com/0xSemantic/lola-os/internal/tools/builtin"
)

type mockChain struct {
	mock.Mock
}

func (m *mockChain) GetBalance(ctx context.Context, address string, block blockchain.BlockNumber) (*big.Int, error) {
	args := m.Called(ctx, address, block)
	return args.Get(0).(*big.Int), args.Error(1)
}
func (m *mockChain) SendTransaction(ctx context.Context, tx *blockchain.Transaction) (string, error) {
	args := m.Called(ctx, tx)
	return args.String(0), args.Error(1)
}
func (m *mockChain) CallContract(ctx context.Context, call *blockchain.ContractCall) ([]byte, error) {
	args := m.Called(ctx, call)
	return args.Get(0).([]byte), args.Error(1)
}
func (m *mockChain) ChainID(ctx context.Context) (*big.Int, error) {
	args := m.Called(ctx)
	return args.Get(0).(*big.Int), args.Error(1)
}
func (m *mockChain) BlockNumber(ctx context.Context) (uint64, error) {
	args := m.Called(ctx)
	return args.Get(0).(uint64), args.Error(1)
}
func (m *mockChain) EstimateGas(ctx context.Context, call *blockchain.ContractCall) (uint64, error) {
	args := m.Called(ctx, call)
	return args.Get(0).(uint64), args.Error(1)
}

type noopLogger struct{}

func (n *noopLogger) Debug(string, ...map[string]interface{})            {}
func (n *noopLogger) Info(string, ...map[string]interface{})             {}
func (n *noopLogger) Warn(string, ...map[string]interface{})             {}
func (n *noopLogger) Error(string, ...map[string]interface{})            {}
func (n *noopLogger) With(map[string]interface{}) observe.Logger         { return n }

func TestBalance(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		ctx := context.Background()
		chain := new(mockChain)
		logger := &noopLogger{}

		// Create a session with the mock chain.
		sess := core.NewSession(logger, "", chain)
		ctx = core.ContextWithSession(ctx, sess)

		expectedBalance := big.NewInt(12345)
		chain.On("GetBalance", ctx, "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7", blockchain.BlockNumberLatest).
			Return(expectedBalance, nil)

		args := map[string]interface{}{
			"address": "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7",
		}
		result, err := builtin.Balance(ctx, args)
		require.NoError(t, err)

		bal, ok := result.(*big.Int)
		assert.True(t, ok)
		assert.Equal(t, expectedBalance, bal)

		chain.AssertExpectations(t)
	})

	t.Run("missing address", func(t *testing.T) {
		ctx := context.Background()
		logger := &noopLogger{}
		sess := core.NewSession(logger, "", new(mockChain))
		ctx = core.ContextWithSession(ctx, sess)

		args := map[string]interface{}{}
		_, err := builtin.Balance(ctx, args)
		assert.ErrorContains(t, err, "missing 'address'")
	})

	t.Run("no session", func(t *testing.T) {
		ctx := context.Background()
		args := map[string]interface{}{"address": "0x123"}
		_, err := builtin.Balance(ctx, args)
		assert.ErrorContains(t, err, "no session")
	})

	t.Run("no chain in session", func(t *testing.T) {
		ctx := context.Background()
		logger := &noopLogger{}
		sess := core.NewSession(logger, "", nil) // nil chain
		ctx = core.ContextWithSession(ctx, sess)

		args := map[string]interface{}{"address": "0x123"}
		_, err := builtin.Balance(ctx, args)
		assert.ErrorContains(t, err, "no blockchain chain available")
	})
}

func TestTransfer(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		ctx := context.Background()
		chain := new(mockChain)
		logger := &noopLogger{}

		// Setup mock chain to expect SendTransaction.
		to := "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7"
		amount := big.NewInt(1000)
		expectedTxHash := "0xabc123"

		chain.On("SendTransaction", ctx, mock.MatchedBy(func(tx *blockchain.Transaction) bool {
			return tx.To != nil && *tx.To == to && tx.Value.Cmp(amount) == 0
		})).Return(expectedTxHash, nil)

		sess := core.NewSession(logger, "", chain)
		ctx = core.ContextWithSession(ctx, sess)

		args := map[string]interface{}{
			"to":     to,
			"amount": amount,
		}
		result, err := builtin.Transfer(ctx, args)
		require.NoError(t, err)

		txHash, ok := result.(string)
		assert.True(t, ok)
		assert.Equal(t, expectedTxHash, txHash)

		chain.AssertExpectations(t)
	})

	// ... error cases
}


// EOF: internal/tools/builtin/builtin_test.go