// Package security defines the interfaces for enforcing security policies
// on agent operations. Policies are evaluated before any onchain write.
//
// Key types:
//   - EvaluationContext : carries information about the operation.
//   - Policy            : a single rule that can allow or deny.
//   - Enforcer          : aggregates policies and evaluates them.
//
// File: internal/security/interface.go

package security

import "context"

// EvaluationContext holds all data needed for policy decisions.
// Session will later contain agent identity, chain, etc.
type EvaluationContext struct {
	Tool    string                 `json:"tool"`
	Args    map[string]interface{} `json:"args"`
	Session interface{}            `json:"session"` // placeholder
}

// Policy is a single security rule.
// It returns nil if the operation is allowed, otherwise an error describing the denial.
type Policy interface {
	Check(ctx context.Context, evalCtx *EvaluationContext) error
}

// Enforcer manages a set of policies and evaluates them collectively.
// All policies must allow the operation for it to proceed.
type Enforcer interface {
	// AddPolicy appends a policy to the enforcer.
	AddPolicy(policy Policy)

	// Evaluate runs all policies against the given context.
	// If any policy returns an error, evaluation stops and that error is returned.
	Evaluate(ctx context.Context, evalCtx *EvaluationContext) error
}

// EOF: internal/security/interface.go