// Package core provides the central orchestration engine and session management.
//
// File: internal/core/session.go

package core

import (
	"time"

	"github.com/google/uuid"
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
}

// NewSession creates a new session with a fresh UUID and a logger that includes
// the session ID as a structured field.
func NewSession(logger observe.Logger, defaultChainID string) *Session {
	sessionID := uuid.New().String()

	sessionLogger := logger.With(map[string]interface{}{
		"session_id": sessionID,
	})

	return &Session{
		ID:             sessionID,
		CreatedAt:      time.Now().UTC(),
		Logger:         sessionLogger,
		DefaultChainID: defaultChainID,
	}
}

// EOF: internal/core/session.go