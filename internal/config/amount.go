// Package config provides amount parsing with units.
//
// File: internal/config/amount.go

package config

import (
	"fmt"
	"math/big"
	"strconv"
	"strings"
)

// Amount represents a token amount with unit.
type Amount struct {
	Wei *big.Int
}

// ParseAmount parses a string like "1.5 eth", "100 gwei", "5000 wei".
func ParseAmount(s string) (*Amount, error) {
	s = strings.TrimSpace(s)
	parts := strings.Fields(s)
	if len(parts) != 2 {
		return nil, fmt.Errorf("invalid amount format: %q", s)
	}
	valueStr, unit := parts[0], strings.ToLower(parts[1])

	valueFloat, err := strconv.ParseFloat(valueStr, 64)
	if err != nil {
		return nil, fmt.Errorf("parse number: %w", err)
	}

	var wei *big.Int
	switch unit {
	case "wei":
		wei = big.NewInt(int64(valueFloat))
	case "gwei":
		// 1 gwei = 1e9 wei
		wei = new(big.Int).Mul(big.NewInt(int64(valueFloat*1e9)), big.NewInt(1))
	case "eth":
		// 1 eth = 1e18 wei
		wei = new(big.Int).Mul(big.NewInt(int64(valueFloat*1e18)), big.NewInt(1))
	default:
		return nil, fmt.Errorf("unknown unit: %s", unit)
	}
	return &Amount{Wei: wei}, nil
}

// MustParseAmount panics if parsing fails.
func MustParseAmount(s string) *Amount {
	a, err := ParseAmount(s)
	if err != nil {
		panic(err)
	}
	return a
}

// EOF: internal/config/amount.go