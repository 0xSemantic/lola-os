// Package security_test verifies the security interfaces using mocks.
//
// File: internal/security/interface_test.go

package security_test

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"github.com/0xSemantic/lola-os/internal/security"
)

// MockPolicy implements security.Policy for testing.
type MockPolicy struct {
	mock.Mock
}

func (m *MockPolicy) Check(ctx context.Context, evalCtx *security.EvaluationContext) error {
	args := m.Called(ctx, evalCtx)
	return args.Error(0)
}

// MockEnforcer implements security.Enforcer for testing.
type MockEnforcer struct {
	mock.Mock
}

func (m *MockEnforcer) AddPolicy(policy security.Policy) {
	m.Called(policy)
}

func (m *MockEnforcer) Evaluate(ctx context.Context, evalCtx *security.EvaluationContext) error {
	args := m.Called(ctx, evalCtx)
	return args.Error(0)
}

func TestPolicyInterface(t *testing.T) {
	ctx := context.Background()
	evalCtx := &security.EvaluationContext{
		Tool: "send",
		Args: map[string]interface{}{"to": "0x123"},
	}

	mockPolicy := new(MockPolicy)
	mockPolicy.On("Check", ctx, evalCtx).Return(nil)

	err := mockPolicy.Check(ctx, evalCtx)
	assert.NoError(t, err)
	mockPolicy.AssertExpectations(t)
}

func TestEnforcerInterface(t *testing.T) {
	ctx := context.Background()
	evalCtx := &security.EvaluationContext{Tool: "swap"}
	mockPolicy := new(MockPolicy)
	mockEnforcer := new(MockEnforcer)

	mockEnforcer.On("AddPolicy", mockPolicy).Return()
	mockEnforcer.On("Evaluate", ctx, evalCtx).Return(nil)

	mockEnforcer.AddPolicy(mockPolicy)
	err := mockEnforcer.Evaluate(ctx, evalCtx)
	assert.NoError(t, err)

	mockEnforcer.AssertExpectations(t)
}

// EOF: internal/security/interface_test.go