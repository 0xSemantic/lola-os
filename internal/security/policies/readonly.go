// Package policies provides a global read‑only policy.
//
// File: internal/security/policies/readonly.go

package policies

import (
	"context"
	"errors"

	"github.com/0xSemantic/lola-os/internal/security"
)

// ReadOnlyPolicy rejects all write operations.
type ReadOnlyPolicy struct{}

// NewReadOnlyPolicy creates a new read‑only policy.
func NewReadOnlyPolicy() *ReadOnlyPolicy {
	return &ReadOnlyPolicy{}
}

// Check implements security.Policy.
func (p *ReadOnlyPolicy) Check(ctx context.Context, evalCtx *security.EvaluationContext) error {
	// List of tools that perform writes.
	writeTools := map[string]bool{
		"transfer": true,
		"send":     true,
		"swap":     true,
		"deploy":   true,
		"approve":  true,
	}
	if writeTools[evalCtx.Tool] {
		return errors.New("read‑only mode: write operations are disabled")
	}
	return nil
}

// EOF: internal/security/policies/readonly.go