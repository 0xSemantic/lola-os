// Package builtin_test verifies the placeholder built‑in tools.
//
// File: internal/tools/builtin/builtin_test.go

package builtin_test

import (
	"context"
	"math/big"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/tools/builtin"
)

func TestBalance(t *testing.T) {
	ctx := context.Background()
	args := map[string]interface{}{"address": "0x123"}
	result, err := builtin.Balance(ctx, args)
	require.NoError(t, err)

	bal, ok := result.(*big.Int)
	assert.True(t, ok)
	assert.Equal(t, big.NewInt(1e18), bal)
}

func TestTransfer(t *testing.T) {
	ctx := context.Background()
	t.Run("valid", func(t *testing.T) {
		args := map[string]interface{}{
			"to":     "0xabc",
			"amount": big.NewInt(1000),
		}
		result, err := builtin.Transfer(ctx, args)
		require.NoError(t, err)

		txHash, ok := result.(string)
		assert.True(t, ok)
		assert.Equal(t, "0x0000000000000000000000000000000000000000000000000000000000001234", txHash)
	})

	t.Run("missing to", func(t *testing.T) {
		args := map[string]interface{}{"amount": big.NewInt(1000)}
		_, err := builtin.Transfer(ctx, args)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "missing 'to'")
	})

	t.Run("missing amount", func(t *testing.T) {
		args := map[string]interface{}{"to": "0xabc"}
		_, err := builtin.Transfer(ctx, args)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "missing 'amount'")
	})
}

// EOF: internal/tools/builtin/builtin_test.go