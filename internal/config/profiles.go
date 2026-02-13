// Package config provides built‑in chain profiles.
//
// File: internal/config/profiles.go

package config

import (
	"time"
)

// DefaultChainProfiles returns the built‑in profiles for major EVM chains.
func DefaultChainProfiles() map[string]interface{} {
	return map[string]interface{}{
		"ethereum": map[string]interface{}{
			"chain_id":          1,
			"native_currency":   "ETH",
			"block_time":        "12s",
			"gas_price_limit":   "100 gwei",
			"confirmations":     2,
			"timeout":           "30s",
			"default":           true,
			"retry": map[string]interface{}{
				"max_attempts":    3,
				"initial_backoff": "100ms",
				"max_backoff":     "2s",
				"backoff_factor":  2.0,
			},
		},
		"polygon": map[string]interface{}{
			"chain_id":        137,
			"native_currency": "MATIC",
			"block_time":      "2s",
			"gas_price_limit": "100 gwei",
			"confirmations":   3,
			"timeout":         "30s",
			"default":         false,
			"retry": map[string]interface{}{
				"max_attempts":    3,
				"initial_backoff": "100ms",
				"max_backoff":     "2s",
				"backoff_factor":  2.0,
			},
		},
		"arbitrum": map[string]interface{}{
			"chain_id":        42161,
			"native_currency": "ETH",
			"block_time":      "0.25s",
			"gas_price_limit": "1 gwei",
			"confirmations":   2,
			"timeout":         "30s",
			"default":         false,
			"retry": map[string]interface{}{
				"max_attempts":    3,
				"initial_backoff": "100ms",
				"max_backoff":     "2s",
				"backoff_factor":  2.0,
			},
		},
		"optimism": map[string]interface{}{
			"chain_id":        10,
			"native_currency": "ETH",
			"block_time":      "2s",
			"gas_price_limit": "1 gwei",
			"confirmations":   2,
			"timeout":         "30s",
			"default":         false,
			"retry": map[string]interface{}{
				"max_attempts":    3,
				"initial_backoff": "100ms",
				"max_backoff":     "2s",
				"backoff_factor":  2.0,
			},
		},
		"base": map[string]interface{}{
			"chain_id":        8453,
			"native_currency": "ETH",
			"block_time":      "2s",
			"gas_price_limit": "1 gwei",
			"confirmations":   2,
			"timeout":         "30s",
			"default":         false,
			"retry": map[string]interface{}{
				"max_attempts":    3,
				"initial_backoff": "100ms",
				"max_backoff":     "2s",
				"backoff_factor":  2.0,
			},
		},
		"bsc": map[string]interface{}{
			"chain_id":        56,
			"native_currency": "BNB",
			"block_time":      "3s",
			"gas_price_limit": "5 gwei",
			"confirmations":   3,
			"timeout":         "30s",
			"default":         false,
			"retry": map[string]interface{}{
				"max_attempts":    3,
				"initial_backoff": "100ms",
				"max_backoff":     "2s",
				"backoff_factor":  2.0,
			},
		},
		"avalanche": map[string]interface{}{
			"chain_id":        43114,
			"native_currency": "AVAX",
			"block_time":      "2s",
			"gas_price_limit": "25 gwei",
			"confirmations":   2,
			"timeout":         "30s",
			"default":         false,
			"retry": map[string]interface{}{
				"max_attempts":    3,
				"initial_backoff": "100ms",
				"max_backoff":     "2s",
				"backoff_factor":  2.0,
			},
		},
		"goerli": map[string]interface{}{
			"chain_id":        5,
			"native_currency": "ETH",
			"block_time":      "12s",
			"gas_price_limit": "100 gwei",
			"confirmations":   2,
			"timeout":         "30s",
			"default":         false,
			"retry": map[string]interface{}{
				"max_attempts":    3,
				"initial_backoff": "100ms",
				"max_backoff":     "2s",
				"backoff_factor":  2.0,
			},
		},
		"sepolia": map[string]interface{}{
			"chain_id":        11155111,
			"native_currency": "ETH",
			"block_time":      "12s",
			"gas_price_limit": "100 gwei",
			"confirmations":   2,
			"timeout":         "30s",
			"default":         false,
			"retry": map[string]interface{}{
				"max_attempts":    3,
				"initial_backoff": "100ms",
				"max_backoff":     "2s",
				"backoff_factor":  2.0,
			},
		},
	}
}

// EOF: internal/config/profiles.go