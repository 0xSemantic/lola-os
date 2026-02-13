// Package evm provides an encrypted keystore implementing blockchain.Wallet.
// It uses AES-256-GCM for encryption and scrypt for key derivation.
//
// File: internal/blockchain/evm/keystore.go

package evm

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/ecdsa"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
	"golang.org/x/crypto/scrypt"
)

// Keystore implements blockchain.Wallet using an encrypted file on disk.
// The private key is encrypted with AES-256-GCM; the encryption key is derived
// from a passphrase using scrypt (N=32768, r=8, p=1).
type Keystore struct {
	address    common.Address
	privateKey *ecdsa.PrivateKey
	keyFile    string
}

// keystoreJSON represents the on‑disk encrypted format.
type keystoreJSON struct {
	Address string `json:"address"`
	Crypto  struct {
		CipherText   string `json:"ciphertext"`
		CipherParams struct {
			IV string `json:"iv"`
		} `json:"cipherparams"`
		KDF       string `json:"kdf"`
		KDFParams struct {
			N     int    `json:"n"`
			R     int    `json:"r"`
			P     int    `json:"p"`
			Salt  string `json:"salt"`
			DKLen int    `json:"dklen"`
		} `json:"kdfparams"`
	} `json:"crypto"`
}

// NewKeystore creates or loads an encrypted keystore.
// If the key file exists, it is decrypted and the wallet is initialized.
// If it does not exist, a new private key is generated, encrypted, and saved.
func NewKeystore(keyFile, passphrase string) (*Keystore, error) {
	// Check if file exists.
	if _, err := os.Stat(keyFile); err == nil {
		// Load existing.
		return loadKeystore(keyFile, passphrase)
	} else if !os.IsNotExist(err) {
		return nil, fmt.Errorf("keystore: stat file: %w", err)
	}

	// Generate new private key.
	privateKey, err := crypto.GenerateKey()
	if err != nil {
		return nil, fmt.Errorf("keystore: generate key: %w", err)
	}
	address := crypto.PubkeyToAddress(privateKey.PublicKey)

	// Encrypt and save.
	if err := saveKeystore(keyFile, passphrase, privateKey, address); err != nil {
		return nil, err
	}

	return &Keystore{
		address:    address,
		privateKey: privateKey,
		keyFile:    keyFile,
	}, nil
}

// loadKeystore reads, decrypts, and parses an existing keystore file.
func loadKeystore(keyFile, passphrase string) (*Keystore, error) {
	data, err := os.ReadFile(keyFile)
	if err != nil {
		return nil, fmt.Errorf("keystore: read file: %w", err)
	}

	var ks keystoreJSON
	if err := json.Unmarshal(data, &ks); err != nil {
		return nil, fmt.Errorf("keystore: parse JSON: %w", err)
	}

	// Derive key from passphrase using scrypt.
	salt, err := hex.DecodeString(ks.Crypto.KDFParams.Salt)
	if err != nil {
		return nil, fmt.Errorf("keystore: decode salt: %w", err)
	}
	dk, err := scrypt.Key([]byte(passphrase), salt, ks.Crypto.KDFParams.N, ks.Crypto.KDFParams.R, ks.Crypto.KDFParams.P, ks.Crypto.KDFParams.DKLen)
	if err != nil {
		return nil, fmt.Errorf("keystore: scrypt: %w", err)
	}

	// Decrypt ciphertext.
	iv, err := hex.DecodeString(ks.Crypto.CipherParams.IV)
	if err != nil {
		return nil, fmt.Errorf("keystore: decode iv: %w", err)
	}
	ciphertext, err := hex.DecodeString(ks.Crypto.CipherText)
	if err != nil {
		return nil, fmt.Errorf("keystore: decode ciphertext: %w", err)
	}

	block, err := aes.NewCipher(dk[:32])
	if err != nil {
		return nil, fmt.Errorf("keystore: new cipher: %w", err)
	}
	aesgcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, fmt.Errorf("keystore: new GCM: %w", err)
	}

	plaintext, err := aesgcm.Open(nil, iv, ciphertext, nil)
	if err != nil {
		return nil, fmt.Errorf("keystore: decrypt: %w", err)
	}

	// Parse private key.
	privateKey, err := crypto.ToECDSA(plaintext)
	if err != nil {
		return nil, fmt.Errorf("keystore: parse private key: %w", err)
	}
	address := common.HexToAddress(ks.Address)

	return &Keystore{
		address:    address,
		privateKey: privateKey,
		keyFile:    keyFile,
	}, nil
}

// saveKeystore encrypts a private key and writes it to disk.
func saveKeystore(keyFile, passphrase string, privateKey *ecdsa.PrivateKey, address common.Address) error {
	// Generate random salt and IV.
	salt := make([]byte, 32)
	if _, err := rand.Read(salt); err != nil {
		return fmt.Errorf("keystore: generate salt: %w", err)
	}
	iv := make([]byte, 12) // GCM standard nonce size
	if _, err := rand.Read(iv); err != nil {
		return fmt.Errorf("keystore: generate iv: %w", err)
	}

	// Derive key.
	dk, err := scrypt.Key([]byte(passphrase), salt, 32768, 8, 1, 32)
	if err != nil {
		return fmt.Errorf("keystore: scrypt: %w", err)
	}

	// Encrypt private key bytes.
	block, err := aes.NewCipher(dk)
	if err != nil {
		return fmt.Errorf("keystore: new cipher: %w", err)
	}
	aesgcm, err := cipher.NewGCM(block)
	if err != nil {
		return fmt.Errorf("keystore: new GCM: %w", err)
	}
	privateKeyBytes := crypto.FromECDSA(privateKey)
	ciphertext := aesgcm.Seal(nil, iv, privateKeyBytes, nil)

	// Build JSON.
	var ks keystoreJSON
	ks.Address = address.Hex()
	ks.Crypto.CipherText = hex.EncodeToString(ciphertext)
	ks.Crypto.CipherParams.IV = hex.EncodeToString(iv)
	ks.Crypto.KDF = "scrypt"
	ks.Crypto.KDFParams.N = 32768
	ks.Crypto.KDFParams.R = 8
	ks.Crypto.KDFParams.P = 1
	ks.Crypto.KDFParams.Salt = hex.EncodeToString(salt)
	ks.Crypto.KDFParams.DKLen = 32

	data, err := json.MarshalIndent(ks, "", "  ")
	if err != nil {
		return fmt.Errorf("keystore: marshal JSON: %w", err)
	}

	// Ensure directory exists.
	if err := os.MkdirAll(filepath.Dir(keyFile), 0700); err != nil {
		return fmt.Errorf("keystore: create directory: %w", err)
	}

	// Write file with restrictive permissions.
	if err := os.WriteFile(keyFile, data, 0600); err != nil {
		return fmt.Errorf("keystore: write file: %w", err)
	}

	return nil
}

// Sign implements blockchain.Wallet.
// It signs the provided digest (32‑byte hash) using ECDSA.
func (k *Keystore) Sign(digest []byte) ([]byte, error) {
	sig, err := crypto.Sign(digest, k.privateKey)
	if err != nil {
		return nil, fmt.Errorf("keystore: sign: %w", err)
	}
	// Return 65‑byte signature [R || S || V] with V in {0,1}.
	return sig, nil
}

// Address implements blockchain.Wallet.
func (k *Keystore) Address() string {
	return k.address.Hex()
}

// Path returns the file path of the keystore.
func (k *Keystore) Path() string {
	return k.keyFile
}

// EOF: internal/blockchain/evm/keystore.go