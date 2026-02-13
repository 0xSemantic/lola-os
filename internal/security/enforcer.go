// Package security provides a pluggable policy enforcer.
// It aggregates multiple policies and evaluates them; all must allow.
//
// File: internal/security/enforcer.go

package security

import (
	"context"
	"fmt"
	"sync"
)

// Enforcer aggregates and evaluates security policies.
// It is safe for concurrent use.
type Enforcer struct {
	mu       sync.RWMutex
	policies []Policy
}

// NewEnforcer creates an empty enforcer.
func NewEnforcer() *Enforcer {
	return &Enforcer{
		policies: make([]Policy, 0),
	}
}

// AddPolicy appends a policy to the enforcer.
func (e *Enforcer) AddPolicy(policy Policy) {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.policies = append(e.policies, policy)
}

// Evaluate runs all policies against the given context.
// If any policy returns an error, evaluation stops immediately and that error is returned.
// Returns nil if all policies allow the operation.
func (e *Enforcer) Evaluate(ctx context.Context, evalCtx *EvaluationContext) error {
	e.mu.RLock()
	policies := make([]Policy, len(e.policies))
	copy(policies, e.policies)
	e.mu.RUnlock()

	for _, p := range policies {
		if err := p.Check(ctx, evalCtx); err != nil {
			return fmt.Errorf("policy %T: %w", p, err)
		}
	}
	return nil
}

// EOF: internal/security/enforcer.go