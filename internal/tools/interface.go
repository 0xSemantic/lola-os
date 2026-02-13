// Package tools defines the contract for executable units of work (tools)
// that can be registered, discovered, and invoked by the LOLA OS engine.
// Tools are the primary way agents interact with onchain capabilities.
//
// Key types:
//   - Tool     : function signature for any executable tool.
//   - Registry : interface for storing and retrieving tools by name.
//
// File: internal/tools/interface.go

package tools

import "context"

// Tool is a function that performs a specific operation.
// It receives a context and a map of arguments, and returns a result or an error.
type Tool func(ctx context.Context, args map[string]interface{}) (interface{}, error)

// Registry is a storage interface for tools.
// Implementations must be safe for concurrent read/write.
type Registry interface {
	// Register binds a name to a tool. Returns an error if the name already exists.
	Register(name string, tool Tool) error

	// Get retrieves a tool by name. Returns ErrNotFound if not registered.
	Get(name string) (Tool, error)

	// List returns the names of all registered tools.
	List() []string
}

// EOF: internal/tools/interface.go