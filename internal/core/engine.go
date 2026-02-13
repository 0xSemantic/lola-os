// Package core provides the central orchestration engine for LOLA OS.
// It manages agent sessions, tool dispatch, security policy enforcement,
// and coordinates all blockchain interactions through abstract interfaces.
//
// Key types:
//   - Engine      : main orchestrator; created via NewEngine()
//   - Session     : holds per‑invocation context (see session.go)
//
// Engine depends only on interfaces (ToolRegistry, Enforcer, Logger),
// making it completely agnostic to specific implementations.
//
// File: internal/core/engine.go

package core

import (
	"context"
	"fmt"
	"sync"

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
func (e *Engine) CreateSession(defaultChainID string) *Session {
	sess := NewSession(e.logger, defaultChainID)

	e.mu.Lock()
	defer e.mu.Unlock()
	e.sessions[sess.ID] = sess

	sess.Logger.Info("session created", map[string]interface{}{
		"default_chain": defaultChainID,
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
// are used. Otherwise, a background session is assumed.
func (e *Engine) Execute(ctx context.Context, toolName string, args map[string]interface{}) (interface{}, error) {
	// 1. Resolve tool from registry.
	tool, err := e.registry.Get(toolName)
	if err != nil {
		return nil, fmt.Errorf("execute: %w", err)
	}

	// 2. Extract or create evaluation context.
	session := sessionFromContext(ctx)
	if session == nil {
		// If no session is attached, create a transient one.
		session = e.CreateSession("")
		ctx = contextWithSession(ctx, session)
	}

	evalCtx := &security.EvaluationContext{
		Tool:    toolName,
		Args:    args,
		Session: session,
	}

	// 3. Run security policies.
	if err := e.security.Evaluate(ctx, evalCtx); err != nil {
		session.Logger.Warn("security policy blocked execution",
			map[string]interface{}{"tool": toolName, "reason": err.Error()})
		return nil, fmt.Errorf("execute: security policy denied: %w", err)
	}

	// 4. Execute the tool.
	session.Logger.Info("executing tool", map[string]interface{}{
		"tool": toolName,
		"args": args,
	})
	result, err := tool(ctx, args)
	if err != nil {
		session.Logger.Error("tool execution failed",
			map[string]interface{}{"tool": toolName, "error": err.Error()})
		return nil, fmt.Errorf("execute: tool %q failed: %w", toolName, err)
	}

	session.Logger.Info("tool executed successfully", map[string]interface{}{
		"tool": toolName,
	})
	return result, nil
}

// sessionFromContext extracts a Session pointer from the context.
// Returns nil if no session is attached.
func sessionFromContext(ctx context.Context) *Session {
	if s, ok := ctx.Value(sessionContextKey{}).(*Session); ok {
		return s
	}
	return nil
}

// contextWithSession attaches a Session to a context.
func contextWithSession(ctx context.Context, sess *Session) context.Context {
	return context.WithValue(ctx, sessionContextKey{}, sess)
}

// sessionContextKey is an unexported type for context keys to avoid collisions.
type sessionContextKey struct{}

// EOF: internal/core/engine.go