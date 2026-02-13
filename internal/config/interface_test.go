// Package config_test verifies the config interfaces using mocks.
//
// File: internal/config/interface_test.go

package config_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"github.com/0xSemantic/lola-os/internal/config"
)

// MockLoader implements config.Loader for testing.
type MockLoader struct {
	mock.Mock
}

func (m *MockLoader) Load(ctx context.Context) (map[string]interface{}, error) {
	args := m.Called(ctx)
	return args.Get(0).(map[string]interface{}), args.Error(1)
}

func TestLoaderInterface(t *testing.T) {
	ctx := context.Background()
	mockLoader := new(MockLoader)

	expectedCfg := map[string]interface{}{
		"chain":  "ethereum",
		"rpc":    "https://...",
		"wallet": map[string]interface{}{"type": "keystore"},
	}
	mockLoader.On("Load", ctx).Return(expectedCfg, nil)

	cfg, err := mockLoader.Load(ctx)
	assert.NoError(t, err)
	assert.Equal(t, expectedCfg, cfg)

	mockLoader.AssertExpectations(t)
}

// EOF: internal/config/interface_test.go