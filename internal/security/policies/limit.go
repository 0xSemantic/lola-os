// Package policies provides concrete security policy implementations.
//
// File: internal/security/policies/limit.go

package policies

import (
	"context"
	"fmt"
	"math/big"
	"sync"
	"time"

	"github.com/0xSemantic/lola-os/internal/blockchain"
	"github.com/0xSemantic/lola-os/internal/config"
	"github.com/0xSemantic/lola-os/internal/security"
)

// LimitPolicy enforces per‑transaction and daily spending limits on native currency.
type LimitPolicy struct {
	mu               sync.RWMutex
	maxTxValue       *big.Int      // per‑transaction maximum (nil = no limit)
	dailyLimit       *big.Int      // daily total maximum (nil = no limit)
	dailySpent       map[string]*big.Int // address -> total spent in current rolling window
	dailyReset       map[string]time.Time // address -> last reset time
	window           time.Duration // 24h
}

type sessionIDer interface {
	GetID() string
}
if sid, ok := evalCtx.Session.(sessionIDer); ok {
    agentID = sid.GetID()
} else {
    agentID = "unknown"
}

// NewLimitPolicy creates a policy from configuration.
func NewLimitPolicy(maxTx, daily *config.Amount) *LimitPolicy {
	p := &LimitPolicy{
		dailySpent: make(map[string]*big.Int),
		dailyReset: make(map[string]time.Time),
		window:     24 * time.Hour,
	}
	if maxTx != nil {
		p.maxTxValue = new(big.Int).Set(maxTx.Wei)
	}
	if daily != nil {
		p.dailyLimit = new(big.Int).Set(daily.Wei)
	}
	return p
}

// Check implements security.Policy.
func (p *LimitPolicy) Check(ctx context.Context, evalCtx *security.EvaluationContext) error {
	// Only apply to transaction tools (send, transfer, etc.).
	// For simplicity, we check if the tool is one that sends value.
	if evalCtx.Tool != "transfer" && evalCtx.Tool != "send" && evalCtx.Tool != "swap" {
		return nil
	}

	// Extract amount.
	amountRaw, ok := evalCtx.Args["amount"]
	if !ok {
		return nil // tool without amount (e.g., deploy) not limited by value
	}
	amount, ok := amountRaw.(*big.Int)
	if !ok {
		return nil // ignore if not *big.Int
	}

	// Per‑transaction limit.
	if p.maxTxValue != nil && amount.Cmp(p.maxTxValue) > 0 {
		return fmt.Errorf("transaction value %s exceeds per‑tx limit %s",
			amount.String(), p.maxTxValue.String())
	}

	// Daily limit.
	if p.dailyLimit != nil {
		// Identify the agent/address. For now, use session ID as key.
		session, ok := evalCtx.Session.(interface{ GetID() string }) // we need session to have ID
		// Since Session is an interface{} in EvaluationContext, we need to cast.
		// We'll assume it has an ID field. We'll adjust later.
		// For now, use a placeholder "agent".
		agentID := "agent" // placeholder

		p.mu.Lock()
		defer p.mu.Unlock()

		now := time.Now().UTC()
		resetTime, exists := p.dailyReset[agentID]
		if !exists || now.Sub(resetTime) > p.window {
			// Reset window.
			p.dailySpent[agentID] = new(big.Int)
			p.dailyReset[agentID] = now
		}

		spent := p.dailySpent[agentID]
		newSpent := new(big.Int).Add(spent, amount)
		if newSpent.Cmp(p.dailyLimit) > 0 {
			return fmt.Errorf("daily limit %s exceeded, already spent %s, attempted +%s",
				p.dailyLimit.String(), spent.String(), amount.String())
		}
		p.dailySpent[agentID] = newSpent
	}

	return nil
}

// EOF: internal/security/policies/limit.go