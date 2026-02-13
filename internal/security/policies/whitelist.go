// Package policies provides address whitelist/blacklist policy.
//
// File: internal/security/policies/whitelist.go

package policies

import (
	"context"
	"fmt"

	"github.com/0xSemantic/lola-os/internal/security"
)

// WhitelistPolicy restricts destination addresses for write operations.
type WhitelistPolicy struct {
	allowed map[string]bool
	blocked map[string]bool
}

// NewWhitelistPolicy creates a policy with allowed and blocked address sets.
// If allowed is non‑empty, only those addresses are permitted.
// Blocked addresses are always denied, even if also in allowed (allowed takes precedence).
func NewWhitelistPolicy(allowed, blocked []string) *WhitelistPolicy {
	allowedSet := make(map[string]bool)
	for _, addr := range allowed {
		allowedSet[addr] = true
	}
	blockedSet := make(map[string]bool)
	for _, addr := range blocked {
		blockedSet[addr] = true
	}
	return &WhitelistPolicy{
		allowed: allowedSet,
		blocked: blockedSet,
	}
}

// Check implements security.Policy.
func (p *WhitelistPolicy) Check(ctx context.Context, evalCtx *security.EvaluationContext) error {
	// Extract 'to' address.
	toRaw, ok := evalCtx.Args["to"]
	if !ok {
		return nil // not a transfer/contract call
	}
	to, ok := toRaw.(string)
	if !ok {
		return nil // not a string
	}

	// Check whitelist.
	if len(p.allowed) > 0 {
		if !p.allowed[to] {
			return fmt.Errorf("address %s not in whitelist", to)
		}
	}
	// Check blacklist.
	if p.blocked[to] {
		return fmt.Errorf("address %s is blocked", to)
	}
	return nil
}

// EOF: internal/security/policies/whitelist.go