// Package config defines the contract for loading configuration data.
// The Loader interface abstracts the source (env, file, etc.) and returns
// a raw map that can be parsed by higher‑level components.
//
// File: internal/config/interface.go

package config

import "context"

// Loader retrieves configuration from a specific source.
// Implementations must be safe for concurrent calls.
type Loader interface {
	// Load returns the entire configuration as a generic map.
	// The structure of the map depends on the source; downstream
	// code is responsible for validation and type assertion.
	Load(ctx context.Context) (map[string]interface{}, error)
}

// EOF: internal/config/interface.go