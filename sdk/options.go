// Package sdk provides functional options for configuring the LOLA OS runtime.
//
// File: sdk/options.go

package sdk

import (
	"time"

	"github.com/0xSemantic/lola-os/internal/config"
)

// Option configures the Runtime.
type Option func(*options)

type options struct {
	configPaths     []string
	envPrefix       string
	defaultChainID  string
	keystorePath    string
	keystorePass    string
	readOnly        bool
	rpcRetries      int
	rpcBackoff      time.Duration
}

// WithConfigFile adds a YAML configuration file to load.
// Can be called multiple times; later files override earlier ones.
func WithConfigFile(path string) Option {
	return func(o *options) {
		o.configPaths = append(o.configPaths, path)
	}
}

// WithEnvPrefix sets the prefix for environment variables (default "LOLA_").
func WithEnvPrefix(prefix string) Option {
	return func(o *options) {
		o.envPrefix = prefix
	}
}

// WithDefaultChain sets the default chain ID or name.
func WithDefaultChain(chainID string) Option {
	return func(o *options) {
		o.defaultChainID = chainID
	}
}

// WithKeystore configures an encrypted keystore.
func WithKeystore(path, passphrase string) Option {
	return func(o *options) {
		o.keystorePath = path
		o.keystorePass = passphrase
	}
}

// WithReadOnly forces read‑only mode, even if a private key is available.
func WithReadOnly() Option {
	return func(o *options) {
		o.readOnly = true
	}
}

// WithRPCRetries sets the number of RPC retry attempts.
func WithRPCRetries(retries int) Option {
	return func(o *options) {
		o.rpcRetries = retries
	}
}

// WithRPCBackoff sets the initial backoff duration for RPC retries.
func WithRPCBackoff(backoff time.Duration) Option {
	return func(o *options) {
		o.rpcBackoff = backoff
	}
}

// EOF: sdk/options.go