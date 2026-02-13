package observe_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/observe"
)

func TestAuditLogger_Log(t *testing.T) {
	tmpDir := t.TempDir()
	path := filepath.Join(tmpDir, "audit.log")

	logger, err := observe.NewAuditLogger(path, true)
	require.NoError(t, err)
	defer logger.Close()

	entry := &observe.AuditEntry{
		SessionID: "sess123",
		Chain:     "ethereum",
		TxHash:    "0xabc",
		From:      "0xfrom",
		To:        "0xto",
		Value:     "1000",
	}
	err = logger.Log(entry)
	require.NoError(t, err)

	// Check file exists and contains the entry.
	data, err := os.ReadFile(path)
	require.NoError(t, err)
	assert.Contains(t, string(data), "sess123")
}

func TestAuditLogger_Disabled(t *testing.T) {
	logger, err := observe.NewAuditLogger("", false)
	require.NoError(t, err)
	err = logger.Log(&observe.AuditEntry{})
	assert.NoError(t, err) // no panic
}

// EOF: internal/observe/audit_test.go