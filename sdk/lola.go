// Package sdk is the primary entry point for LOLA OS.
// It provides a simple, idiomatic API for making agents blockchain‑native.
//
// Example:
//
//	rt := lola.Init()
//	rt.Run(context.Background(), func(ctx context.Context, rt *lola.Runtime) error {
//	    balance, err := rt.EVM().GetBalance(ctx, "0x...", nil)
//	    if err != nil {
//	        return err
//	    }
//	    fmt.Println("Balance:", balance)
//	    return nil
//	})
//
// File: sdk/lola.go

package sdk

import (
	"context"
	"fmt"
	"os"

	"github.com/joho/godotenv"

	"github.com/0xSemantic/lola-os/internal/config"
)

// Init creates a new LOLA OS runtime with configuration from environment
// and optional YAML files. It panics on unrecoverable errors; use TryInit
// if you need error handling.
func Init(opts ...Option) *Runtime {
	rt, err := TryInit(opts...)
	if err != nil {
		panic(err)
	}
	return rt
}

// TryInit attempts to create a runtime, returning an error on failure.
func TryInit(opts ...Option) (*Runtime, error) {
	// Apply options.
	opt := &options{
		configPaths: []string{"lola.yaml"},
		envPrefix:   "LOLA_",
	}
	for _, o := range opts {
		o(opt)
	}

	// Load .env file (if present).
	_ = godotenv.Load() // ignore error

	// Build configuration loaders.
	var loaders []config.Loader

	// 1. Defaults (built‑in profiles) are handled by loader's defaultConfig.
	// 2. YAML files.
	for _, path := range opt.configPaths {
		loaders = append(loaders, config.NewYamlLoader(path))
	}
	// 3. Environment variables.
	loaders = append(loaders, config.NewEnvLoader(opt.envPrefix))

	// Load config.
	cfg, err := config.LoadConfig(context.Background(), loaders...)
	if err != nil {
		return nil, fmt.Errorf("load config: %w", err)
	}

	// Override default chain if set.
	if opt.defaultChainID != "" {
		for id := range cfg.Chains {
			cfg.Chains[id].Default = (id == opt.defaultChainID)
		}
	}

	return newRuntime(cfg, opt)
}

// EOF: sdk/lola.go