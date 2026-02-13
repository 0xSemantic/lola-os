//go:build integration
// Package policies_test contains integration tests with simulated backend.
//
// File: internal/security/policies/integration_test.go

package policies_test

import (
	"context"
	"math/big"
	"testing"

	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/accounts/abi/bind/backends"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
	"github.com/0xSemantic/lola-os/internal/core"
	"github.com/0xSemantic/lola-os/internal/observe"
	"github.com/0xSemantic/lola-os/internal/security"
	"github.com/0xSemantic/lola-os/internal/security/policies"
	"github.com/0xSemantic/lola-os/internal/tools"
	"github.com/0xSemantic/lola-os/internal/tools/builtin"
)

func TestPolicy_DailyLimit_Integration(t *testing.T) {
	// Setup simulated backend.
	privKey, _ := crypto.GenerateKey()
	auth, _ := bind.NewKeyedTransactorWithChainID(privKey, big.NewInt(1337))
	sim := backends.NewSimulatedBackend(types.GenesisAlloc{
		auth.From: {Balance: big.NewInt(1e18)},
	}, 10000000)
	simBackend := sim.(*backends.SimulatedBackend)
	rpcClient := simBackend.RPCClient()
	ethCli := ethclient.NewClient(rpcClient)
	logger := &observe.NoopLogger{}
	client := evm.NewClientFromEthClient(ethCli, logger, nil)

	// Create wallet.
	tmpDir := t.TempDir()
	keyFile := tmpDir + "/wallet.key"
	wallet, _ := evm.NewKeystore(keyFile, "test")
	gw, _ := evm.NewEVMGateway(context.Background(), "sim", logger, nil, wallet)
	gw.SetClient(client) // we need a method to set client; we'll add for testing.

	// Setup enforcer with daily limit.
	enforcer := security.NewEnforcer()
	dailyLimit := config.MustParseAmount("0.5 eth")
	enforcer.AddPolicy(policies.NewLimitPolicy(nil, dailyLimit))

	// Setup engine.
	reg := tools.New()
	reg.Register("transfer", builtin.Transfer)
	engine := core.NewEngine(reg, enforcer, logger)

	// Create session with chain.
	sess := engine.CreateSession("", gw)
	ctx := core.ContextWithSession(context.Background(), sess)

	// Send transaction of 0.3 ETH (should pass).
	args := map[string]interface{}{
		"to":     "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7",
		"amount": big.NewInt(300000000000000000),
	}
	_, err := engine.Execute(ctx, "transfer", args)
	require.NoError(t, err)
	sim.Commit()

	// Send another 0.3 ETH (should exceed daily limit).
	_, err = engine.Execute(ctx, "transfer", args)
	assert.ErrorContains(t, err, "daily limit exceeded")
}

// EOF: internal/security/policies/integration_test.go