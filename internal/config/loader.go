// Package config provides configuration loading from multiple sources.
//
// File: internal/config/loader.go

package config

import (
	"context"
	"fmt"

	"github.com/mitchellh/mapstructure"
	"reflect"
)

// Loader defines the interface for configuration sources.
type Loader interface {
	Load(ctx context.Context) (map[string]interface{}, error)
}

// LoadConfig loads and merges configuration from multiple sources.
// Sources are processed in order: defaults, profiles, file, env.
// Returns the fully populated Config struct.
func LoadConfig(ctx context.Context, loaders ...Loader) (*Config, error) {
	// Start with defaults.
	merged := defaultConfig()

	for _, loader := range loaders {
		data, err := loader.Load(ctx)
		if err != nil {
			return nil, fmt.Errorf("config loader %T: %w", loader, err)
		}
		// Merge (simple map merge, overwriting keys).
		merged = mergeMaps(merged, data)
	}

	// Decode map into Config struct.
	var cfg Config
	decoder, err := mapstructure.NewDecoder(&mapstructure.DecoderConfig{
		Result:     &cfg,
		TagName:    "mapstructure",
		DecodeHook: mapstructure.ComposeDecodeHookFunc(
			mapstructure.StringToTimeDurationHookFunc(),
			stringToAmountHookFunc(),
		),
	})
	if err != nil {
		return nil, fmt.Errorf("create decoder: %w", err)
	}
	if err := decoder.Decode(merged); err != nil {
		return nil, fmt.Errorf("decode config: %w", err)
	}

	// Post‑load validation and enrichment.
	if err := validateConfig(&cfg); err != nil {
		return nil, fmt.Errorf("config validation: %w", err)
	}

	return &cfg, nil
}

// defaultConfig returns the built‑in default configuration.
func defaultConfig() map[string]interface{} {
	return map[string]interface{}{
		"chains":    DefaultChainProfiles(),
		"security": map[string]interface{}{
			"read_only": false,
		},
		"observability": map[string]interface{}{
			"logging": map[string]interface{}{
				"level":  "info",
				"format": "json",
				"output": "stdout",
			},
			"metrics": map[string]interface{}{
				"enabled": false,
				"addr":    ":9090",
				"path":    "/metrics",
			},
			"audit": map[string]interface{}{
				"enabled": false,
				"path":    "./lola.audit.log",
			},
		},
		"advanced": map[string]interface{}{
			"rpc_retries": 3,
			"rpc_backoff": "100ms",
		},
	}
}

// mergeMaps recursively merges src into dst.
func mergeMaps(dst, src map[string]interface{}) map[string]interface{} {
	for k, v := range src {
		if vm, ok := v.(map[string]interface{}); ok {
			if dm, ok := dst[k].(map[string]interface{}); ok {
				dst[k] = mergeMaps(dm, vm)
			} else {
				dst[k] = vm
			}
		} else {
			dst[k] = v
		}
	}
	return dst
}

// stringToAmountHookFunc converts string amounts to *Amount.
func stringToAmountHookFunc() mapstructure.DecodeHookFunc {
	return func(f, t reflect.Type, data interface{}) (interface{}, error) {
		if f.Kind() != reflect.String || t != reflect.TypeOf(&Amount{}) {
			return data, nil
		}
		return ParseAmount(data.(string))
	}
}

// validateConfig performs semantic validation.
func validateConfig(cfg *Config) error {
	// Ensure at least one chain is configured.
	if len(cfg.Chains) == 0 {
		return fmt.Errorf("no chains configured")
	}
	// Ensure each chain has an RPC URL or a chain ID (for profile fallback?).
	for name, chain := range cfg.Chains {
		if chain.RPC == "" {
			// Check if it's a built‑in profile with a public fallback.
			// For now, just warn; we can allow empty RPC if profile has default? We'll require RPC.
			return fmt.Errorf("chain %q: missing RPC URL", name)
		}
	}
	return nil
}

// EOF: internal/config/loader.go