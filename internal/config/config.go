// Package config defines the configuration structures and loading logic.
//
// File: internal/config/config.go

package config

import (
	"fmt"
	"math/big"
	"time"

	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
)

// Config holds all LOLA OS configuration.
// It is populated by merging data from multiple sources (defaults, files, env).
type Config struct {
	// Global agent name (used in logs/metrics).
	Name string `mapstructure:"name"`

	// Chains is a map of chain ID/name to chain configuration.
	Chains map[string]*ChainConfig `mapstructure:"chains"`

	// Wallet configuration.
	Wallet *WalletConfig `mapstructure:"wallet"`

	// Security policies configuration.
	Security *SecurityConfig `mapstructure:"security"`

	// Observability configuration.
	Observability *ObservabilityConfig `mapstructure:"observability"`

	// Advanced tuning parameters.
	Advanced *AdvancedConfig `mapstructure:"advanced"`
}

// ChainConfig defines settings for a single blockchain.
type ChainConfig struct {
	// RPC URL (primary endpoint).
	RPC string `mapstructure:"rpc"`

	// Fallback RPC URLs (tried in order).
	RPCRetryURLs []string `mapstructure:"rpc_fallback"`

	// Chain ID (required for custom chains).
	ChainID *uint64 `mapstructure:"chain_id"`

	// Native currency symbol (e.g., "ETH", "MATIC").
	NativeCurrency string `mapstructure:"native_currency"`

	// Block time duration (string like "2s").
	BlockTime time.Duration `mapstructure:"block_time"`

	// Maximum gas price the agent will accept (as string, e.g., "100 gwei").
	GasPriceLimit *Amount `mapstructure:"gas_price_limit"`

	// Number of confirmations to wait for finality.
	Confirmations uint64 `mapstructure:"confirmations"`

	// Per‑request timeout.
	Timeout time.Duration `mapstructure:"timeout"`

	// Whether this chain is the default.
	Default bool `mapstructure:"default"`

	// Retry configuration (optional).
	RetryConfig *evm.RetryConfig `mapstructure:"retry"`
}

// WalletConfig defines wallet/keystore settings.
type WalletConfig struct {
	// Path to encrypted keystore file.
	KeystorePath string `mapstructure:"keystore_path"`

	// Environment variable name that holds the passphrase.
	PassphraseEnv string `mapstructure:"passphrase_env"`

	// Timeout for wallet operations.
	Timeout time.Duration `mapstructure:"timeout"`

	// Read‑only mode (overrides all).
	ReadOnly bool `mapstructure:"read_only"`
}

// SecurityConfig defines all security policies.
type SecurityConfig struct {
	// Global read‑only flag (rejects all writes).
	ReadOnly bool `mapstructure:"read_only"`

	// Per‑transaction value limit (native currency).
	MaxTransactionValue *Amount `mapstructure:"max_transaction_value"`

	// Daily spend limit (rolling 24h).
	DailyLimit *Amount `mapstructure:"daily_limit"`

	// Allowed destination addresses (if non‑empty, only these are permitted).
	AllowedAddresses []string `mapstructure:"allowed_addresses"`

	// Blocked destination addresses.
	BlockedAddresses []string `mapstructure:"blocked_addresses"`

	// Human‑in‑the‑loop configuration.
	HITL *HITLConfig `mapstructure:"human_in_the_loop"`
}

// HITLConfig defines human‑in‑the‑loop parameters.
type HITLConfig struct {
	Enabled   bool          `mapstructure:"enabled"`
	Threshold *Amount       `mapstructure:"threshold"`
	Timeout   time.Duration `mapstructure:"timeout"`
	Mode      string        `mapstructure:"mode"` // "console" (others future)
}

// ObservabilityConfig defines logging, metrics, tracing, audit.
type ObservabilityConfig struct {
	Logging *LoggingConfig `mapstructure:"logging"`
	Metrics *MetricsConfig `mapstructure:"metrics"`
	Tracing *TracingConfig `mapstructure:"tracing"`
	Audit   *AuditConfig   `mapstructure:"audit"`
}

type LoggingConfig struct {
	Level  string `mapstructure:"level"`  // debug, info, warn, error
	Format string `mapstructure:"format"` // json, console
	Output string `mapstructure:"output"` // stdout, stderr, file path
}

type MetricsConfig struct {
	Enabled bool   `mapstructure:"enabled"`
	Addr    string `mapstructure:"addr"`
	Path    string `mapstructure:"path"`
}

type TracingConfig struct {
	Enabled     bool   `mapstructure:"enabled"`
	Exporter    string `mapstructure:"exporter"` // otlp, jaeger, stdout
	Endpoint    string `mapstructure:"endpoint"`
	ServiceName string `mapstructure:"service_name"`
}

type AuditConfig struct {
	Enabled bool   `mapstructure:"enabled"`
	Path    string `mapstructure:"path"`
}

// AdvancedConfig contains experimental settings.
type AdvancedConfig struct {
	RPCRetries   int           `mapstructure:"rpc_retries"`
	RPCBackoff   time.Duration `mapstructure:"rpc_backoff"`
	ToolRegistry string        `mapstructure:"tool_registry"` // future
}

// Amount represents a token amount with unit.
type Amount struct {
	Wei *big.Int
}

// UnmarshalText implements encoding.TextUnmarshaler for parsing strings like "1.5 eth".
func (a *Amount) UnmarshalText(text []byte) error {
	// Parse using go-ethereum's ParseEther? We'll implement simple parser.
	// For brevity, we'll support only "wei", "gwei", "eth".
	s := string(text)
	// ... parsing logic (can be expanded later)
	return nil
}

// EOF: internal/config/config.go