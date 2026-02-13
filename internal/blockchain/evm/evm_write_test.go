// Package evm_test tests write operations (SendTransaction, DeployContract).
//
// File: internal/blockchain/evm/evm_write_test.go

package evm_test

import (
	"context"
	"math/big"
	"strings"
	"testing"
	"time"

	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/accounts/abi/bind/backends"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/blockchain"
	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
	"github.com/0xSemantic/lola-os/internal/observe"
)

const storageABI = `[
	{
		"inputs": [],
		"name": "retrieve",
		"outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [{"internalType": "uint256", "name": "num", "type": "uint256"}],
		"name": "store",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]`

const storageBytecode = "608060405234801561001057600080fd5b50610150806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c80632e64cec11461003b5780636057361d14610059575b600080fd5b610043610075565b60405161005091906100d9565b60405180910390f35b610073600480360381019061006e919061009d565b61007e565b005b60008054905090565b8060008190555050565b60008135905061009781610103565b92915050565b6000602082840312156100af57600080fd5b60006100bd84828501610088565b91505092915050565b6100cf816100f4565b82525050565b60006020820190506100ee60008301846100c6565b92915050565b6000819050919050565b61010c816100f4565b811461011757600080fd5b5056fea2646970667358221220404e37f487a89a932dca5e77faaf6ca2de3b991f93d230604b1b8daaef64766264736f6c63430008070033"

type noopLogger struct{}

func (n *noopLogger) Debug(string, ...map[string]interface{})            {}
func (n *noopLogger) Info(string, ...map[string]interface{})             {}
func (n *noopLogger) Warn(string, ...map[string]interface{})             {}
func (n *noopLogger) Error(string, ...map[string]interface{})            {}
func (n *noopLogger) With(map[string]interface{}) observe.Logger         { return n }

func TestEVMGateway_SendTransaction(t *testing.T) {
	// Setup simulated backend.
	privKey, err := crypto.GenerateKey()
	require.NoError(t, err)
	auth, err := bind.NewKeyedTransactorWithChainID(privKey, big.NewInt(1337))
	require.NoError(t, err)

	sim := backends.NewSimulatedBackend(types.GenesisAlloc{
		auth.From: {Balance: big.NewInt(1000000000000000000)}, // 1 ETH
	}, 10000000)

	// Create keystore wallet.
	tmpDir := t.TempDir()
	keyFile := tmpDir + "/wallet.key"
	passphrase := "test"
	wallet, err := evm.NewKeystore(keyFile, passphrase)
	require.NoError(t, err)

	// Create EVM gateway with simulated client.
	simBackend := sim.(*backends.SimulatedBackend)
	rpcClient := simBackend.RPCClient()
	ethCli := backends.NewSimulatedBackend(types.GenesisAlloc{}, 10000000).(*backends.SimulatedBackend).RPCClient()
	// Actually we need to use the same backend. Let's get the client from the existing sim.
	// The simulated backend's RPCClient is exported.
	ethCli = simBackend.RPCClient()
	client := evm.NewClientFromEthClient(ethclient.NewClient(ethCli), &noopLogger{}, nil)

	gateway := &evm.EVMGateway{
		Client: client,
		Logger: &noopLogger{},
		Wallet: wallet,
	}
	gateway.SetWallet(wallet)

	// Send ETH to a random address.
	to := crypto.PubkeyToAddress(*crypto.GenerateKey().Public().(*ecdsa.PublicKey))
	value := big.NewInt(1000000000000000) // 0.001 ETH
	txHash, err := gateway.SendTransaction(context.Background(), &blockchain.Transaction{
		To:    &to.Hex(),
		Value: value,
	})
	require.NoError(t, err)
	assert.NotEmpty(t, txHash)

	sim.Commit()

	// Check balance.
	bal, err := gateway.GetBalance(context.Background(), to.Hex(), blockchain.BlockNumberLatest)
	require.NoError(t, err)
	assert.Equal(t, value, bal)
}

func TestEVMGateway_DeployContract(t *testing.T) {
	// Setup simulated backend and wallet (same as above).
	privKey, _ := crypto.GenerateKey()
	auth, _ := bind.NewKeyedTransactorWithChainID(privKey, big.NewInt(1337))
	sim := backends.NewSimulatedBackend(types.GenesisAlloc{
		auth.From: {Balance: big.NewInt(1e18)},
	}, 10000000)
	simBackend := sim.(*backends.SimulatedBackend)
	rpcClient := simBackend.RPCClient()
	ethCli := ethclient.NewClient(rpcClient)
	client := evm.NewClientFromEthClient(ethCli, &noopLogger{}, nil)

	tmpDir := t.TempDir()
	keyFile := tmpDir + "/wallet.key"
	wallet, _ := evm.NewKeystore(keyFile, "test")

	gateway := &evm.EVMGateway{
		Client: client,
		Logger: &noopLogger{},
		Wallet: wallet,
	}

	// Deploy contract.
	bytecode := common.FromHex(storageBytecode)
	txHash, contractAddr, err := gateway.DeployContract(context.Background(), bytecode, nil)
	require.NoError(t, err)
	assert.NotEmpty(t, txHash)
	assert.NotEqual(t, common.Address{}.Hex(), contractAddr.Hex())

	sim.Commit()

	// Call contract to verify it's deployed.
	parsedABI, _ := abi.JSON(strings.NewReader(storageABI))
	data, err := parsedABI.Pack("retrieve")
	require.NoError(t, err)

	call := &blockchain.ContractCall{
		To:   contractAddr.Hex(),
		Data: data,
	}
	res, err := gateway.CallContract(context.Background(), call)
	require.NoError(t, err)

	// Decode result.
	ret := new(big.Int).SetBytes(res)
	assert.Equal(t, big.NewInt(0), ret)
}

// EOF: internal/blockchain/evm/evm_write_test.go