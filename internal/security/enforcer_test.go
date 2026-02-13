// Package security_test tests the enforcer.
//
// File: internal/security/enforcer_test.go

package security_test

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"github.com/0xSemantic/lola-os/internal/security"
)

type MockPolicy struct {
	mock.Mock
}

func (m *MockPolicy) Check(ctx context.Context, evalCtx *security.EvaluationContext) error {
	args := m.Called(ctx, evalCtx)
	return args.Error(0)
}

func TestEnforcer_Empty(t *testing.T) {
	e := security.NewEnforcer()
	err := e.Evaluate(context.Background(), &security.EvaluationContext{})
	assert.NoError(t, err)
}

func TestEnforcer_AllAllow(t *testing.T) {
	e := security.NewEnforcer()
	p1 := new(MockPolicy)
	p2 := new(MockPolicy)

	p1.On("Check", mock.Anything, mock.Anything).Return(nil)
	p2.On("Check", mock.Anything, mock.Anything).Return(nil)

	e.AddPolicy(p1)
	e.AddPolicy(p2)

	err := e.Evaluate(context.Background(), &security.EvaluationContext{})
	assert.NoError(t, err)

	p1.AssertExpectations(t)
	p2.AssertExpectations(t)
}

func TestEnforcer_FirstDenies(t *testing.T) {
	e := security.NewEnforcer()
	p1 := new(MockPolicy)
	p2 := new(MockPolicy)

	denyErr := errors.New("denied")
	p1.On("Check", mock.Anything, mock.Anything).Return(denyErr)
	// p2 should not be called.

	e.AddPolicy(p1)
	e.AddPolicy(p2)

	err := e.Evaluate(context.Background(), &security.EvaluationContext{})
	assert.ErrorIs(t, err, denyErr)

	p1.AssertExpectations(t)
	p2.AssertNotCalled(t, "Check")
}

// EOF: internal/security/enforcer_test.go