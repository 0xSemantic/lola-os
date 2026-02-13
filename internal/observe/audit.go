// Package observe provides an append‑only audit log for onchain writes.
//
// File: internal/observe/audit.go

package observe

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

// AuditEntry represents a single audit record.
type AuditEntry struct {
	Timestamp   time.Time              `json:"timestamp"`
	SessionID   string                 `json:"session_id"`
	AgentName   string                 `json:"agent_name,omitempty"`
	Chain       string                 `json:"chain"`
	TxHash      string                 `json:"tx_hash"`
	From        string                 `json:"from"`
	To          string                 `json:"to"`
	Value       string                 `json:"value,omitempty"` // wei as string
	Data        string                 `json:"data,omitempty"`  // hex
	PolicyResults []string             `json:"policy_results,omitempty"`
	Extra       map[string]interface{} `json:"extra,omitempty"`
}

// AuditLogger is an append‑only audit log for onchain write operations.
type AuditLogger struct {
	mu       sync.Mutex
	file     *os.File
	encoder  *json.Encoder
	enabled  bool
}

// NewAuditLogger creates or appends to an audit log file.
// If the file does not exist, it is created with permissions 0600.
// If enabled is false, the logger discards all entries.
func NewAuditLogger(path string, enabled bool) (*AuditLogger, error) {
	if !enabled {
		return &AuditLogger{enabled: false}, nil
	}

	// Ensure directory exists.
	if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
		return nil, fmt.Errorf("audit: create directory: %w", err)
	}

	// Open file for append, create if not exists.
	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
	if err != nil {
		return nil, fmt.Errorf("audit: open file: %w", err)
	}

	return &AuditLogger{
		file:    f,
		encoder: json.NewEncoder(f),
		enabled: true,
	}, nil
}

// Log records an audit entry.
func (a *AuditLogger) Log(entry *AuditEntry) error {
	if !a.enabled || a.file == nil {
		return nil
	}
	a.mu.Lock()
	defer a.mu.Unlock()
	if entry.Timestamp.IsZero() {
		entry.Timestamp = time.Now().UTC()
	}
	return a.encoder.Encode(entry)
}

// Close flushes and closes the audit log file.
func (a *AuditLogger) Close() error {
	if a.file != nil {
		return a.file.Close()
	}
	return nil
}

// EOF: internal/observe/audit.go