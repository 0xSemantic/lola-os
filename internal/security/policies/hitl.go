// Package policies provides human‑in‑the‑loop policy with console approval.
//
// File: internal/security/policies/hitl.go

package policies

import (
	"bufio"
	"context"
	"fmt"
	"math/big"
	"os"
	"strings"
	"time"

	"github.com/0xSemantic/lola-os/internal/config"
	"github.com/0xSemantic/lola-os/internal/security"
)

// HITLPolicy pauses execution and requests human approval for transactions above threshold.
type HITLPolicy struct {
	threshold *big.Int
	timeout   time.Duration
	mode      string // "console"
}

// NewHITLPolicy creates a human‑in‑the‑loop policy from config.
func NewHITLPolicy(threshold *config.Amount, timeout time.Duration, mode string) *HITLPolicy {
	var thresh *big.Int
	if threshold != nil {
		thresh = new(big.Int).Set(threshold.Wei)
	}
	if mode == "" {
		mode = "console"
	}
	if timeout == 0 {
		timeout = 5 * time.Minute
	}
	return &HITLPolicy{
		threshold: thresh,
		timeout:   timeout,
		mode:      mode,
	}
}

// Check implements security.Policy.
func (p *HITLPolicy) Check(ctx context.Context, evalCtx *security.EvaluationContext) error {
	// Only apply to tools that send value.
	if evalCtx.Tool != "transfer" && evalCtx.Tool != "send" && evalCtx.Tool != "swap" {
		return nil
	}

	// Extract amount.
	amountRaw, ok := evalCtx.Args["amount"]
	if !ok {
		return nil
	}
	amount, ok := amountRaw.(*big.Int)
	if !ok {
		return nil
	}

	// Check threshold.
	if p.threshold == nil || amount.Cmp(p.threshold) <= 0 {
		return nil
	}

	// Request approval.
	switch p.mode {
	case "console":
		return p.consoleApprove(evalCtx)
	default:
		return fmt.Errorf("unsupported HITL mode: %s", p.mode)
	}
}

func (p *HITLPolicy) consoleApprove(evalCtx *security.EvaluationContext) error {
	fmt.Printf("\n=== HUMAN APPROVAL REQUIRED ===\n")
	fmt.Printf("Tool: %s\n", evalCtx.Tool)
	fmt.Printf("Arguments: %v\n", evalCtx.Args)
	fmt.Printf("Threshold: %s wei\n", p.threshold.String())
	fmt.Printf("Amount: %s wei\n", evalCtx.Args["amount"].(*big.Int).String())
	fmt.Printf("Approve? (y/N): ")

	// Use buffered reader with timeout.
	reader := bufio.NewReader(os.Stdin)
	ch := make(chan string)
	errCh := make(chan error)

	go func() {
		response, err := reader.ReadString('\n')
		if err != nil {
			errCh <- err
			return
		}
		ch <- strings.TrimSpace(response)
	}()

	select {
	case <-time.After(p.timeout):
		return fmt.Errorf("human approval timed out after %v", p.timeout)
	case err := <-errCh:
		return fmt.Errorf("error reading input: %w", err)
	case response := <-ch:
		response = strings.ToLower(response)
		if response != "y" && response != "yes" {
			return fmt.Errorf("human rejected transaction")
		}
	}
	fmt.Println("Transaction approved.")
	return nil
}

// EOF: internal/security/policies/hitl.go