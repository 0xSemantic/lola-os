// Package evm provides transaction construction and signing utilities.
//
// File: internal/blockchain/evm/tx.go

package evm

import (
	"context"
	"fmt"
	"math/big"

	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"

	"github.com/0xSemantic/lola-os/internal/blockchain"
)

// TxBuilder builds and signs Ethereum transactions.
type TxBuilder struct {
	client  *Client
	wallet  blockchain.Wallet
	chainID *big.Int
	address common.Address
}

// NewTxBuilder creates a new transaction builder.
// It caches the chain ID and sender address.
func NewTxBuilder(ctx context.Context, client *Client, wallet blockchain.Wallet) (*TxBuilder, error) {
	chainID, err := client.ChainID(ctx)
	if err != nil {
		return nil, fmt.Errorf("txbuilder: get chain ID: %w", err)
	}
	address := common.HexToAddress(wallet.Address())
	return &TxBuilder{
		client:  client,
		wallet:  wallet,
		chainID: chainID,
		address: address,
	}, nil
}

// BuildTransfer constructs and signs a native currency transfer transaction.
// If gasPrice or gasFeeCap/gasTipCap are nil, they are automatically estimated.
// If gasLimit is 0, it is estimated.
// If nonce is nil, the next pending nonce is fetched.
func (b *TxBuilder) BuildTransfer(ctx context.Context, to string, value *big.Int, opts *TxOpts) (*types.Transaction, error) {
	if !common.IsHexAddress(to) {
		return nil, fmt.Errorf("txbuilder: invalid to address: %s", to)
	}
	toAddr := common.HexToAddress(to)

	nonce, err := b.resolveNonce(ctx, opts)
	if err != nil {
		return nil, err
	}

	// Determine transaction type and build.
	if opts != nil && opts.DynamicFee {
		return b.buildAndSignDynamicFee(ctx, &toAddr, value, nil, opts, nonce)
	}
	return b.buildAndSignLegacy(ctx, &toAddr, value, nil, opts, nonce)
}

// BuildContractCall constructs and signs a contract call transaction.
func (b *TxBuilder) BuildContractCall(ctx context.Context, to string, data []byte, value *big.Int, opts *TxOpts) (*types.Transaction, error) {
	if !common.IsHexAddress(to) {
		return nil, fmt.Errorf("txbuilder: invalid contract address: %s", to)
	}
	toAddr := common.HexToAddress(to)

	nonce, err := b.resolveNonce(ctx, opts)
	if err != nil {
		return nil, err
	}

	if opts != nil && opts.DynamicFee {
		return b.buildAndSignDynamicFee(ctx, &toAddr, value, data, opts, nonce)
	}
	return b.buildAndSignLegacy(ctx, &toAddr, value, data, opts, nonce)
}

// BuildDeploy constructs and signs a contract deployment transaction.
// The to address is nil.
func (b *TxBuilder) BuildDeploy(ctx context.Context, data []byte, opts *TxOpts) (*types.Transaction, error) {
	nonce, err := b.resolveNonce(ctx, opts)
	if err != nil {
		return nil, err
	}

	if opts != nil && opts.DynamicFee {
		return b.buildAndSignDynamicFee(ctx, nil, big.NewInt(0), data, opts, nonce)
	}
	return b.buildAndSignLegacy(ctx, nil, big.NewInt(0), data, opts, nonce)
}

// TxOpts holds optional transaction parameters.
type TxOpts struct {
	// GasLimit (0 = estimate).
	GasLimit uint64
	// GasPrice for legacy transactions (nil = estimate).
	GasPrice *big.Int
	// GasFeeCap for dynamic fee transactions (nil = estimate).
	GasFeeCap *big.Int
	// GasTipCap for dynamic fee transactions (nil = estimate).
	GasTipCap *big.Int
	// Nonce (nil = fetch next pending nonce).
	Nonce *uint64
	// DynamicFee forces EIP‑1559 transaction (if supported).
	DynamicFee bool
}

// resolveNonce gets the nonce from opts or fetches the pending nonce.
func (b *TxBuilder) resolveNonce(ctx context.Context, opts *TxOpts) (uint64, error) {
	if opts != nil && opts.Nonce != nil {
		return *opts.Nonce, nil
	}
	nonce, err := b.client.PendingNonceAt(ctx, b.address)
	if err != nil {
		return 0, fmt.Errorf("txbuilder: get nonce: %w", err)
	}
	return nonce, nil
}

// buildAndSignLegacy constructs and signs a legacy transaction.
func (b *TxBuilder) buildAndSignLegacy(ctx context.Context, to *common.Address, value *big.Int, data []byte, opts *TxOpts, nonce uint64) (*types.Transaction, error) {
	var gasPrice *big.Int
	var gasLimit uint64

	if opts != nil {
		gasPrice = opts.GasPrice
		gasLimit = opts.GasLimit
	}

	// Estimate gas if not provided.
	if gasLimit == 0 {
		callMsg := ethereum.CallMsg{
			From:     b.address,
			To:       to,
			Value:    value,
			Data:     data,
			GasPrice: gasPrice,
		}
		est, err := b.client.EstimateGas(ctx, callMsg)
		if err != nil {
			return nil, fmt.Errorf("txbuilder: estimate gas: %w", err)
		}
		gasLimit = est
	}

	// Suggest gas price if not provided.
	if gasPrice == nil {
		price, err := b.client.SuggestGasPrice(ctx)
		if err != nil {
			return nil, fmt.Errorf("txbuilder: suggest gas price: %w", err)
		}
		gasPrice = price
	}

	// Build unsigned transaction.
	unsignedTx := types.NewTx(&types.LegacyTx{
		Nonce:    nonce,
		To:       to,
		Value:    value,
		Gas:      gasLimit,
		GasPrice: gasPrice,
		Data:     data,
	})

	// Sign.
	return b.signTransaction(unsignedTx)
}

// buildAndSignDynamicFee constructs and signs an EIP‑1559 transaction.
func (b *TxBuilder) buildAndSignDynamicFee(ctx context.Context, to *common.Address, value *big.Int, data []byte, opts *TxOpts, nonce uint64) (*types.Transaction, error) {
	var gasFeeCap, gasTipCap *big.Int
	var gasLimit uint64

	if opts != nil {
		gasFeeCap = opts.GasFeeCap
		gasTipCap = opts.GasTipCap
		gasLimit = opts.GasLimit
	}

	// Get header for base fee.
	header, err := b.client.ec.HeaderByNumber(ctx, nil)
	if err != nil {
		return nil, fmt.Errorf("txbuilder: get header for base fee: %w", err)
	}
	if header.BaseFee == nil {
		// Chain does not support EIP‑1559; fall back to legacy.
		return b.buildAndSignLegacy(ctx, to, value, data, opts, nonce)
	}

	// Estimate gas if not provided.
	if gasLimit == 0 {
		callMsg := ethereum.CallMsg{
			From:      b.address,
			To:        to,
			Value:     value,
			Data:      data,
			GasFeeCap: gasFeeCap,
			GasTipCap: gasTipCap,
		}
		est, err := b.client.EstimateGas(ctx, callMsg)
		if err != nil {
			return nil, fmt.Errorf("txbuilder: estimate gas: %w", err)
		}
		gasLimit = est
	}

	// Suggest tip if not provided.
	if gasTipCap == nil {
		tip, err := b.client.SuggestGasTipCap(ctx)
		if err != nil {
			return nil, fmt.Errorf("txbuilder: suggest gas tip cap: %w", err)
		}
		gasTipCap = tip
	}

	// Suggest fee cap if not provided: (base fee * 2) + tip.
	if gasFeeCap == nil {
		feeCap := new(big.Int).Mul(header.BaseFee, big.NewInt(2))
		feeCap.Add(feeCap, gasTipCap)
		gasFeeCap = feeCap
	}

	// Build unsigned transaction.
	unsignedTx := types.NewTx(&types.DynamicFeeTx{
		Nonce:     nonce,
		To:        to,
		Value:     value,
		Gas:       gasLimit,
		GasFeeCap: gasFeeCap,
		GasTipCap: gasTipCap,
		Data:      data,
	})

	// Sign.
	return b.signTransaction(unsignedTx)
}

// signTransaction signs an unsigned transaction using the wallet.
func (b *TxBuilder) signTransaction(unsignedTx *types.Transaction) (*types.Transaction, error) {
	signer := types.LatestSignerForChainID(b.chainID)
	hash := signer.Hash(unsignedTx)

	signature, err := b.wallet.Sign(hash.Bytes())
	if err != nil {
		return nil, fmt.Errorf("txbuilder: sign: %w", err)
	}

	// Adjust V for chain ID (EIP‑155). The signature from crypto.Sign is [R || S || V] with V = 27/28.
	// signer.SignatureValues expects V = 0/1.
	// We need to normalize: if signature[64] >= 27, subtract 27.
	if len(signature) != 65 {
		return nil, fmt.Errorf("txbuilder: invalid signature length: %d", len(signature))
	}
	v := signature[64]
	if v >= 27 {
		v -= 27
	}
	signature[64] = v

	signedTx, err := unsignedTx.WithSignature(signer, signature)
	if err != nil {
		return nil, fmt.Errorf("txbuilder: apply signature: %w", err)
	}
	return signedTx, nil
}

// EOF: internal/blockchain/evm/tx.go