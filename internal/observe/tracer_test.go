package observe_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/observe"
)

func TestOTelTracer_Stdout(t *testing.T) {
	ctx := context.Background()
	tracer, err := observe.NewOTelTracer(ctx, "stdout", "", "lola-test")
	require.NoError(t, err)
	defer tracer.Shutdown(ctx)

	ctx, span := tracer.StartSpan(ctx, "test-operation")
	span.SetAttributes(map[string]interface{}{"key": "value"})
	span.RecordError(nil) // no error
	span.End()

	// No panic.
}

func TestOTelTracer_InvalidExporter(t *testing.T) {
	_, err := observe.NewOTelTracer(context.Background(), "invalid", "", "test")
	assert.Error(t, err)
}

// EOF: internal/observe/tracer_test.go