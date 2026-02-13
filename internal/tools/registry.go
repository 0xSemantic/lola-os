// Package tools provides the concrete in‑memory implementation of the
// Registry interface. It is safe for concurrent use via an RWMutex.
//
// Key types:
//   - registry : internal map + mutex
//   - New()    : constructor
//
// File: internal/tools/registry.go

package tools

import (
	"errors"
	"sync"

	"github.com/0xSemantic/lola-os/internal/tools"
)

var (
	// ErrNotFound is returned when a tool name is not registered.
	ErrNotFound = errors.New("tool not found")

	// ErrAlreadyExists is returned when registering a name that already exists.
	ErrAlreadyExists = errors.New("tool already registered")
)

// registry implements tools.Registry using an in‑memory map protected by an RWMutex.
type registry struct {
	mu   sync.RWMutex
	data map[string]tools.Tool
}

// New creates a new, empty in‑memory registry.
func New() tools.Registry {
	return &registry{
		data: make(map[string]tools.Tool),
	}
}

// Register binds a name to a tool. Returns ErrAlreadyExists if the name is taken.
func (r *registry) Register(name string, tool tools.Tool) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.data[name]; exists {
		return ErrAlreadyExists
	}
	r.data[name] = tool
	return nil
}

// Get retrieves a tool by name. Returns ErrNotFound if not registered.
func (r *registry) Get(name string) (tools.Tool, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	tool, exists := r.data[name]
	if !exists {
		return nil, ErrNotFound
	}
	return tool, nil
}

// List returns the names of all registered tools in no particular order.
func (r *registry) List() []string {
	r.mu.RLock()
	defer r.mu.RUnlock()

	names := make([]string, 0, len(r.data))
	for name := range r.data {
		names = append(names, name)
	}
	return names
}

// EOF: internal/tools/registry.go