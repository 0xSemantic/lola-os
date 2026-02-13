// Package evm_test contains integration‑style tests using a simulated Ethereum backend.
//
// File: internal/blockchain/evm/evm_test.go

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
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/blockchain"
	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
	"github.com/0xSemantic/lola-os/internal/observe"
)

// A simple storage contract for testing.
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

func TestEVMGateway_ReadOperations(t *testing.T) {
	// Setup simulated backend.
	privKey, err := crypto.GenerateKey()
	require.NoError(t, err)
	auth, err := bind.NewKeyedTransactorWithChainID(privKey, big.NewInt(1337))
	require.NoError(t, err)

	sim := backends.NewSimulatedBackend(types.GenesisAlloc{
		auth.From: {Balance: big.NewInt(1000000000000000000)}, // 1 ETH
	}, 10000000)

	// Deploy storage contract.
	parsedABI, err := abi.JSON(strings.NewReader(storageABI))
	require.NoError(t, err)
	_, _, contract, err := bind.DeployContract(auth, parsedABI, common.FromHex(storageBytecode), sim)
	require.NoError(t, err)
	sim.Commit()

	// Create EVM gateway pointing to the simulated backend.
	logger := &noopLogger{}
	// Simulated backend doesn't support HTTP; we use a custom dialer.
	// We'll use the client directly. For testing, we bypass the gateway's client factory.
	// Better: we can use the simulated backend's RPC client via `sim.RPCClient()`.
	// We'll create a client that wraps the simulated backend.
	// However, the evm.Client expects an ethclient.Client. The simulated backend
	// can be wrapped with `backends.NewSimulatedBackend` and then we can use
	// `ethclient.NewClient(sim.RPCClient())`.

	simClient := backends.NewSimulatedBackend(types.GenesisAlloc{}, 10000000).(*backends.SimulatedBackend)
	// Actually we already have `sim`, we need to create an ethclient from its RPC client.
	// We'll do:
	ec := backends.NewSimulatedBackend(types.GenesisAlloc{}, 10000000).(*backends.SimulatedBackend)
	rpcClient := ec.RPCClient()
	ethCli := ethclient.NewClient(rpcClient)
	// But this creates a new backend; we need to keep the same one.
	// Simpler: we can use the existing `sim` and extract its RPC client.
	// The simulated backend's RPCClient is unexported, but we can use:
	// rpcClient := sim.RPCClient() // This is not exported? Actually it is: func (b *SimulatedBackend) RPCClient() *rpc.Client
	// Let's assert that sim is *SimulatedBackend.
	simBackend, ok := sim.(*backends.SimulatedBackend)
	require.True(t, ok, "sim is not *SimulatedBackend")
	rpcClient := simBackend.RPCClient()
	ethCli := ethclient.NewClient(rpcClient)

	// We need to create an evm.Client that uses this ethCli.
	// Since evm.Client normally dials a URL, we need a constructor that accepts an existing client.
	// We'll add a test helper: NewClientFromEthClient.
	// We'll define it here for testing only.
	client := &evm.Client{
		ec:     ethCli,
		logger: logger,
		retry:  evm.DefaultRetryConfig,
	}

	// Create gateway with this client (we'll add a method to set client for testing).
	gateway := &evm.EVMGateway{
		client: client,
		logger: logger,
	}

	// Test GetBalance.
	balance, err := gateway.GetBalance(context.Background(), auth.From.Hex(), blockchain.BlockNumberLatest)
	require.NoError(t, err)
	assert.Equal(t, big.NewInt(1000000000000000000), balance)

	// Test CallContract on the deployed contract.
	// The contract's retrieve() should return 0 initially.
	call := &blockchain.ContractCall{
		To:   contract.Hex(),
		Data: common.Hex2Bytes("2e64cec1"), // retrieve() signature
	}
	data, err := gateway.CallContract(context.Background(), call)
	require.NoError(t, err)
	// Decode uint256.
	ret := new(big.Int).SetBytes(data)
	assert.Equal(t, big.NewInt(0), ret)

	// Test ChainID.
	chainID, err := gateway.ChainID(context.Background())
	require.NoError(t, err)
	assert.Equal(t, big.NewInt(1337), chainID)

	// Test BlockNumber.
	blockNum, err := gateway.BlockNumber(context.Background())
	require.NoError(t, err)
	assert.GreaterOrEqual(t, blockNum, uint64(1)) // at least one block after deployment

	// Test EstimateGas for a call.
	estCall := &blockchain.ContractCall{
		To:   contract.Hex(),
		Data: common.Hex2Bytes("6057361d000000000000000000000000000000000000000000000000000000000000002a"), // store(42)
	}
	gas, err := gateway.EstimateGas(context.Background(), estCall)
	require.NoError(t, err)
	assert.Greater(t, gas, uint64(0))

	// Test SendTransaction – should error.
	_, err = gateway.SendTransaction(context.Background(), &blockchain.Transaction{})
	assert.ErrorContains(t, err, "not implemented")
}

func TestBoundContract_Call(t *testing.T) {
	// Setup simulated backend and deploy contract (same as above).
	privKey, _ := crypto.GenerateKey()
	auth, _ := bind.NewKeyedTransactorWithChainID(privKey, big.NewInt(1337))
	sim := backends.NewSimulatedBackend(types.GenesisAlloc{
		auth.From: {Balance: big.NewInt(1e18)},
	}, 10000000)
	parsedABI, _ := abi.JSON(strings.NewReader(storageABI))
	_, _, contract, _ := bind.DeployContract(auth, parsedABI, common.FromHex(storageBytecode), sim)
	sim.Commit()

	simBackend := sim.(*backends.SimulatedBackend)
	rpcClient := simBackend.RPCClient()
	ethCli := ethclient.NewClient(rpcClient)

	logger := &noopLogger{}
	client := &evm.Client{
		ec:     ethCli,
		logger: logger,
		retry:  evm.DefaultRetryConfig,
	}
	gateway := &evm.EVMGateway{client: client, logger: logger}

	// Create BoundContract.
	bound, err := evm.NewBoundContract(contract.Hex(), storageABI, gateway)
	require.NoError(t, err)

	// Call retrieve().
	result, err := bound.Call(context.Background(), "retrieve")
	require.NoError(t, err)
	assert.Len(t, result, 1)
	val, ok := result[0].(*big.Int)
	assert.True(t, ok)
	assert.Equal(t, big.NewInt(0), val)

	// Test unknown method.
	_, err = bound.Call(context.Background(), "nonexistent")
	assert.ErrorContains(t, err, "not found")

	// Test Transact – should error.
	_, err = bound.Transact(context.Background(), "store", big.NewInt(42))
	assert.ErrorContains(t, err, "not implemented")
}

// EOF: internal/blockchain/evm/evm_test.go