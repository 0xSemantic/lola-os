// Package sdk provides tool registration.
//
// File: sdk/tools.go

package sdk

import (
	"context"

	"github.com/0xSemantic/lola-os/internal/tools"
)

// ToolFunc is the signature for a custom tool.
type ToolFunc func(ctx context.Context, args map[string]interface{}) (interface{}, error)

var globalRegistry = tools.New()

// RegisterTool registers a tool globally.
// Tools registered this way are available to all runtimes.
func RegisterTool(name string, fn ToolFunc) {
	if err := globalRegistry.Register(name, fn); err != nil {
		panic(err)
	}
}

// EOF: sdk/tools.go