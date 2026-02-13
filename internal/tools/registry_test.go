// Package tools_test contains unit tests for the in‑memory registry.
//
// File: internal/tools/registry_test.go

package tools_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/tools"
	reg "github.com/0xSemantic/lola-os/internal/tools" // concrete package
)

func TestRegistry_RegisterAndGet(t *testing.T) {
	r := reg.New()

	// Dummy tool
	dummy := tools.Tool(func(ctx context.Context, args map[string]interface{}) (interface{}, error) {
		return "ok", nil
	})

	err := r.Register("test", dummy)
	require.NoError(t, err)

	// Duplicate registration
	err = r.Register("test", dummy)
	assert.ErrorIs(t, err, reg.ErrAlreadyExists)

	// Get existing
	tool, err := r.Get("test")
	require.NoError(t, err)
	assert.NotNil(t, tool)

	// Get non‑existing
	_, err = r.Get("missing")
	assert.ErrorIs(t, err, reg.ErrNotFound)
}

func TestRegistry_List(t *testing.T) {
	r := reg.New()
	dummy := func(context.Context, map[string]interface{}) (interface{}, error) { return nil, nil }

	_ = r.Register("a", dummy)
	_ = r.Register("b", dummy)

	list := r.List()
	assert.ElementsMatch(t, []string{"a", "b"}, list)
}

// EOF: internal/tools/registry_test.go