// Package evm_test contains benchmarks for critical paths.
//
// File: internal/blockchain/evm/benchmark_test.go

package evm_test

import (
	"context"
	"math/big"
	"testing"

	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/accounts/abi/bind/backends"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"

	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
	"github.com/0xSemantic/lola-os/internal/observe"
)

func BenchmarkGetBalance(b *testing.B) {
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

	gw := &evm.EVMGateway{
		Client: client,
		Logger: logger,
	}

	addr := auth.From.Hex()
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		_, err := gw.GetBalance(context.Background(), addr, nil)
		if err != nil {
			b.Fatal(err)
		}
	}
}

func BenchmarkSendTransaction(b *testing.B) {
	// Setup with wallet.
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
	tmpDir := b.TempDir()
	keyFile := tmpDir + "/wallet.key"
	wallet, _ := evm.NewKeystore(keyFile, "test")

	gw := &evm.EVMGateway{
		Client: client,
		Logger: logger,
		Wallet: wallet,
	}

	to := "0x742d35Cc6634C0532925a3b844Bc9e90F1A6B1E7"
	value := big.NewInt(1000)

	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		_, err := gw.SendTransaction(context.Background(), &blockchain.Transaction{
			To:    &to,
			Value: value,
		})
		if err != nil {
			b.Fatal(err)
		}
		// Commit block for each transaction? Not needed for benchmark.
	}
}

// EOF: internal/blockchain/evm/benchmark_test.go