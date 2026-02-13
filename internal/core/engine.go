// Package core provides the central orchestration engine for LOLA OS.
// It manages agent sessions, tool dispatch, security policy enforcement,
// and coordinates all blockchain interactions through abstract interfaces.
//
// Key types:
//   - Engine      : main orchestrator; created via NewEngine()
//   - Session     : holds per‑invocation context (see session.go)
//
// Engine depends only on interfaces (ToolRegistry, Enforcer, Logger, Chain),
// making it completely agnostic to specific implementations.
//
// File: internal/core/engine.go

package core

import (
	"context"
	"fmt"
	"sync"

	"github.com/0xSemantic/lola-os/internal/blockchain"
	"github.com/0xSemantic/lola-os/internal/observe"
	"github.com/0xSemantic/lola-os/internal/security"
	"github.com/0xSemantic/lola-os/internal/tools"
)

// Engine orchestrates agent operations.
type Engine struct {
	registry tools.Registry
	security security.Enforcer
	logger   observe.Logger

	mu       sync.RWMutex
	sessions map[string]*Session // active sessions, keyed by ID
}

// NewEngine creates a fully wired Engine instance.
// All dependencies are injected – no hidden global state.
func NewEngine(
	registry tools.Registry,
	enforcer security.Enforcer,
	logger observe.Logger,
) *Engine {
	return &Engine{
		registry: registry,
		security: enforcer,
		logger:   logger,
		sessions: make(map[string]*Session),
	}
}

// CreateSession initializes a new agent session and stores it in the engine.
// The session is automatically logged with its ID.
// If chain is nil, the session will have no blockchain capabilities.
func (e *Engine) CreateSession(defaultChainID string, chain blockchain.Chain) *Session {
	sess := NewSession(e.logger, defaultChainID, chain)

	e.mu.Lock()
	defer e.mu.Unlock()
	e.sessions[sess.ID] = sess

	sess.Logger.Info("session created", map[string]interface{}{
		"default_chain": defaultChainID,
		"has_chain":     chain != nil,
	})
	return sess
}

// GetSession retrieves an active session by its ID.
// Returns nil if the session does not exist.
func (e *Engine) GetSession(id string) *Session {
	e.mu.RLock()
	defer e.mu.RUnlock()
	return e.sessions[id]
}

// CloseSession removes a session and performs cleanup.
func (e *Engine) CloseSession(id string) {
	e.mu.Lock()
	defer e.mu.Unlock()
	if sess, exists := e.sessions[id]; exists {
		sess.Logger.Info("session closed")
		delete(e.sessions, id)
	}
}

// Execute runs a tool by name with the given arguments.
// It resolves the tool, applies security policies, and executes the tool function.
//
// The context may contain a Session; if present, its logger and security context
// are used. Otherwise, a transient session is created.
func (e *Engine) Execute(ctx context.Context, toolName string, args map[string]interface{}) (interface{}, error) {
	// 1. Resolve tool from registry.
	tool, err := e.registry.Get(toolName)
	if err != nil {
		return nil, fmt.Errorf("execute: %w", err)
	}

	// 2. Extract or create session.
	sess := SessionFromContext(ctx)
	if sess == nil {
		// No session attached; create a transient one with no chain.
		sess = e.CreateSession("", nil)
		ctx = ContextWithSession(ctx, sess)
		defer e.CloseSession(sess.ID)
	}

	evalCtx := &security.EvaluationContext{
		Tool:    toolName,
		Args:    args,
		Session: sess,
	}

	// 3. Run security policies.
	if err := e.security.Evaluate(ctx, evalCtx); err != nil {
		sess.Logger.Warn("security policy blocked execution",
			map[string]interface{}{"tool": toolName, "reason": err.Error()})
		return nil, fmt.Errorf("execute: security policy denied: %w", err)
	}

	// 4. Execute the tool.
	sess.Logger.Info("executing tool", map[string]interface{}{
		"tool": toolName,
		"args": args,
	})
	result, err := tool(ctx, args)
	if err != nil {
		sess.Logger.Error("tool execution failed",
			map[string]interface{}{"tool": toolName, "error": err.Error()})
		return nil, fmt.Errorf("execute: tool %q failed: %w", toolName, err)
	}

	sess.Logger.Info("tool executed successfully", map[string]interface{}{
		"tool": toolName,
	})
	return result, nil
}

// EOF: internal/core/engine.go