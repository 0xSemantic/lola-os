// Package config provides environment variable loader.
//
// File: internal/config/env.go

package config

import (
	"context"
	"os"
	"strings"
)

// EnvLoader loads configuration from environment variables.
// It expects variables with prefix "LOLA_" (e.g., LOLA_DEFAULT_CHAIN).
type EnvLoader struct {
	prefix string
}

// NewEnvLoader creates a loader that reads env vars with the given prefix.
func NewEnvLoader(prefix string) *EnvLoader {
	if prefix == "" {
		prefix = "LOLA_"
	}
	return &EnvLoader{prefix: prefix}
}

// Load reads all environment variables with the configured prefix,
// converts them to a nested map using underscores as path separators.
func (l *EnvLoader) Load(ctx context.Context) (map[string]interface{}, error) {
	result := make(map[string]interface{})
	for _, env := range os.Environ() {
		if !strings.HasPrefix(env, l.prefix) {
			continue
		}
		parts := strings.SplitN(env, "=", 2)
		key := strings.TrimPrefix(parts[0], l.prefix)
		value := parts[1]

		// Convert key to path: LOLA_CHAINS_ETHEREUM_RPC -> chains.ethereum.rpc
		path := strings.Split(strings.ToLower(key), "_")
		insertIntoMap(result, path, value)
	}
	return result, nil
}

// insertIntoMap recursively inserts a value into a nested map.
func insertIntoMap(m map[string]interface{}, path []string, value string) {
	if len(path) == 0 {
		return
	}
	if len(path) == 1 {
		m[path[0]] = value
		return
	}
	next, ok := m[path[0]]
	if !ok {
		next = make(map[string]interface{})
		m[path[0]] = next
	}
	if nextMap, ok := next.(map[string]interface{}); ok {
		insertIntoMap(nextMap, path[1:], value)
	} else {
		// Overwrite with map.
		newMap := make(map[string]interface{})
		m[path[0]] = newMap
		insertIntoMap(newMap, path[1:], value)
	}
}

// EOF: internal/config/env.go