package policies_test

import (
	"context"
	"math/big"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/config"
	"github.com/0xSemantic/lola-os/internal/security"
	"github.com/0xSemantic/lola-os/internal/security/policies"
)

type mockSession struct {
	id string
}

func (m *mockSession) GetID() string { return m.id }

func TestLimitPolicy_PerTx(t *testing.T) {
	maxTx := config.MustParseAmount("1 eth")
	policy := policies.NewLimitPolicy(maxTx, nil)

	ctx := context.Background()
	evalCtx := &security.EvaluationContext{
		Tool:    "transfer",
		Args:    map[string]interface{}{"amount": big.NewInt(2e18)}, // 2 eth
		Session: &mockSession{id: "s1"},
	}
	err := policy.Check(ctx, evalCtx)
	assert.ErrorContains(t, err, "exceeds per‑tx limit")
}

func TestLimitPolicy_DailyLimit(t *testing.T) {
	daily := config.MustParseAmount("1 eth")
	policy := policies.NewLimitPolicy(nil, daily)

	ctx := context.Background()
	sess := &mockSession{id: "s1"}
	evalCtx := &security.EvaluationContext{
		Tool:    "transfer",
		Args:    map[string]interface{}{"amount": big.NewInt(5e17)}, // 0.5 eth
		Session: sess,
	}
	err := policy.Check(ctx, evalCtx)
	assert.NoError(t, err)

	// Second transaction: 0.5 + 0.5 = 1.0 (equal to limit, allowed)
	evalCtx.Args["amount"] = big.NewInt(5e17)
	err = policy.Check(ctx, evalCtx)
	assert.NoError(t, err)

	// Third: 0.5 more = 1.5 > limit
	evalCtx.Args["amount"] = big.NewInt(5e17)
	err = policy.Check(ctx, evalCtx)
	assert.ErrorContains(t, err, "daily limit exceeded")
}