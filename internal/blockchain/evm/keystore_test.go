// Package evm_test tests keystore operations.
//
// File: internal/blockchain/evm/keystore_test.go

package evm_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/ethereum/go-ethereum/crypto"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
)

func TestKeystore_CreateAndLoad(t *testing.T) {
	// Use temporary directory.
	tmpDir := t.TempDir()
	keyFile := filepath.Join(tmpDir, "test.key")
	passphrase := "testpass123"

	// Create new keystore.
	ks, err := evm.NewKeystore(keyFile, passphrase)
	require.NoError(t, err)
	assert.NotEmpty(t, ks.Address())
	assert.FileExists(t, keyFile)

	// Load existing keystore.
	ks2, err := evm.NewKeystore(keyFile, passphrase)
	require.NoError(t, err)
	assert.Equal(t, ks.Address(), ks2.Address())

	// Sign a digest.
	digest := crypto.Keccak256Hash([]byte("hello")).Bytes()
	sig, err := ks.Sign(digest)
	require.NoError(t, err)
	assert.Len(t, sig, 65)

	// Verify signature.
	pubKey, err := crypto.SigToPub(digest, sig)
	require.NoError(t, err)
	addr := crypto.PubkeyToAddress(*pubKey)
	assert.Equal(t, ks.Address(), addr.Hex())
}

func TestKeystore_WrongPassphrase(t *testing.T) {
	tmpDir := t.TempDir()
	keyFile := filepath.Join(tmpDir, "test.key")
	passphrase := "correct"

	_, err := evm.NewKeystore(keyFile, passphrase)
	require.NoError(t, err)

	// Load with wrong passphrase.
	_, err = evm.NewKeystore(keyFile, "wrong")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "decrypt")
}

// EOF: internal/blockchain/evm/keystore_test.go