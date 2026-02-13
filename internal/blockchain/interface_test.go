// Package blockchain_test verifies the blockchain interfaces using mocks.
// It ensures the contracts are correct and can be implemented.
//
// File: internal/blockchain/interface_test.go

package blockchain_test

import (
	"context"
	"math/big"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"github.com/0xSemantic/lola-os/internal/blockchain"
)

// MockChain implements blockchain.Chain for testing.
type MockChain struct {
	mock.Mock
}

func (m *MockChain) GetBalance(ctx context.Context, address string, block blockchain.BlockNumber) (*big.Int, error) {
	args := m.Called(ctx, address, block)
	return args.Get(0).(*big.Int), args.Error(1)
}

func (m *MockChain) SendTransaction(ctx context.Context, tx *blockchain.Transaction) (string, error) {
	args := m.Called(ctx, tx)
	return args.String(0), args.Error(1)
}

func (m *MockChain) CallContract(ctx context.Context, call *blockchain.ContractCall) ([]byte, error) {
	args := m.Called(ctx, call)
	return args.Get(0).([]byte), args.Error(1)
}

func (m *MockChain) ChainID(ctx context.Context) (*big.Int, error) {
	args := m.Called(ctx)
	return args.Get(0).(*big.Int), args.Error(1)
}

func (m *MockChain) BlockNumber(ctx context.Context) (uint64, error) {
	args := m.Called(ctx)
	return args.Get(0).(uint64), args.Error(1)
}

func (m *MockChain) EstimateGas(ctx context.Context, call *blockchain.ContractCall) (uint64, error) {
	args := m.Called(ctx, call)
	return args.Get(0).(uint64), args.Error(1)
}

// MockWallet implements blockchain.Wallet for testing.
type MockWallet struct {
	mock.Mock
}

func (m *MockWallet) Sign(digest []byte) ([]byte, error) {
	args := m.Called(digest)
	return args.Get(0).([]byte), args.Error(1)
}

func (m *MockWallet) Address() string {
	args := m.Called()
	return args.String(0)
}

// MockContract implements blockchain.Contract for testing.
type MockContract struct {
	mock.Mock
}

func (m *MockContract) Call(ctx context.Context, method string, args ...interface{}) ([]interface{}, error) {
	callArgs := m.Called(ctx, method, args)
	return callArgs.Get(0).([]interface{}), callArgs.Error(1)
}

func (m *MockContract) Transact(ctx context.Context, method string, args ...interface{}) (string, error) {
	callArgs := m.Called(ctx, method, args)
	return callArgs.String(0), callArgs.Error(1)
}

func TestChainInterface(t *testing.T) {
	ctx := context.Background()
	mockChain := new(MockChain)

	// Simulate GetBalance
	expectedBalance := big.NewInt(1000)
	mockChain.On("GetBalance", ctx, "0x123", blockchain.BlockNumberLatest).Return(expectedBalance, nil)

	balance, err := mockChain.GetBalance(ctx, "0x123", blockchain.BlockNumberLatest)
	assert.NoError(t, err)
	assert.Equal(t, expectedBalance, balance)

	mockChain.AssertExpectations(t)
}

func TestWalletInterface(t *testing.T) {
	mockWallet := new(MockWallet)
	digest := []byte("digest")
	sig := []byte("signature")
	mockWallet.On("Sign", digest).Return(sig, nil)
	mockWallet.On("Address").Return("0xabc")

	s, err := mockWallet.Sign(digest)
	assert.NoError(t, err)
	assert.Equal(t, sig, s)
	assert.Equal(t, "0xabc", mockWallet.Address())
}

func TestContractInterface(t *testing.T) {
	ctx := context.Background()
	mockContract := new(MockContract)
	method := "transfer"
	args := []interface{}{"0xaddr", big.NewInt(100)}

	mockContract.On("Call", ctx, method, args).Return([]interface{}{true}, nil)
	mockContract.On("Transact", ctx, method, args).Return("0xhash", nil)

	res, err := mockContract.Call(ctx, method, args...)
	assert.NoError(t, err)
	assert.Equal(t, true, res[0])

	hash, err := mockContract.Transact(ctx, method, args...)
	assert.NoError(t, err)
	assert.Equal(t, "0xhash", hash)
}

// EOF: internal/blockchain/interface_test.go