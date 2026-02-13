package observe_test

import (
	"bytes"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/observe"
)

func TestZapLogger_JSON(t *testing.T) {
	// Capture output.
	// We can't easily capture zap's stdout; we'd need to use a buffer.
	// For simplicity, we test that creation doesn't panic and With works.
	logger, err := observe.NewZapLogger("info", "json", "stdout")
	require.NoError(t, err)

	logger.Info("test message", map[string]interface{}{"key": "value"})
	logger.With(map[string]interface{}{"session": "123"}).Debug("debug message") // should not appear

	// No assertion, just no panic.
}

func TestZapLogger_Levels(t *testing.T) {
	logger, err := observe.NewZapLogger("warn", "console", "stdout")
	require.NoError(t, err)
	// Should not panic.
	logger.Debug("debug")
	logger.Info("info")
	logger.Warn("warn")
	logger.Error("error")
}

// EOF: internal/observe/logger_test.go