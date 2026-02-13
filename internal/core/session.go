// Package core provides the central orchestration engine and session management.
//
// File: internal/core/session.go

package core

import (
	"context"
	"time"

	"github.com/google/uuid"

	"github.com/0xSemantic/lola-os/internal/blockchain"
	"github.com/0xSemantic/lola-os/internal/observe"
)

// Session holds per‑invocation context for an agent run.
// It is created when an agent starts a new logical session and is used
// to correlate logs, traces, and security decisions.
type Session struct {
	// ID is a globally unique identifier for this session.
	ID string

	// CreatedAt is the timestamp when the session was created.
	CreatedAt time.Time

	// Logger is a child logger pre‑populated with the session ID.
	Logger observe.Logger

	// DefaultChainID (optional) indicates which blockchain the agent prefers.
	DefaultChainID string

	// Chain is the blockchain interface used by tools during this session.
	// May be nil if no blockchain is available (read‑only mode still possible?).
	Chain blockchain.Chain
}

// NewSession creates a new session with a fresh UUID and a logger that includes
// the session ID as a structured field.
func NewSession(logger observe.Logger, defaultChainID string, chain blockchain.Chain) *Session {
	sessionID := uuid.New().String()

	sessionLogger := logger.With(map[string]interface{}{
		"session_id": sessionID,
	})

	return &Session{
		ID:             sessionID,
		CreatedAt:      time.Now().UTC(),
		Logger:         sessionLogger,
		DefaultChainID: defaultChainID,
		Chain:          chain,
	}
}

// SetChain updates the blockchain interface for this session.
func (s *Session) SetChain(chain blockchain.Chain) {
	s.Chain = chain
}

// SessionFromContext extracts the Session from the context.
// Returns nil if no session is attached.
func SessionFromContext(ctx context.Context) *Session {
	if s, ok := ctx.Value(sessionContextKey{}).(*Session); ok {
		return s
	}
	return nil
}

// ContextWithSession attaches a Session to a context.
func ContextWithSession(ctx context.Context, sess *Session) context.Context {
	return context.WithValue(ctx, sessionContextKey{}, sess)
}

// sessionContextKey is an unexported type for context keys to avoid collisions.
type sessionContextKey struct{}

// EOF: internal/core/session.go