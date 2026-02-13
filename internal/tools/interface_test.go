// Package tools_test verifies the tools interfaces using mocks.
//
// File: internal/tools/interface_test.go

package tools_test

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"github.com/0xSemantic/lola-os/internal/tools"
)

// MockRegistry implements tools.Registry for testing.
type MockRegistry struct {
	mock.Mock
}

func (m *MockRegistry) Register(name string, tool tools.Tool) error {
	args := m.Called(name, tool)
	return args.Error(0)
}

func (m *MockRegistry) Get(name string) (tools.Tool, error) {
	args := m.Called(name)
	return args.Get(0).(tools.Tool), args.Error(1)
}

func (m *MockRegistry) List() []string {
	args := m.Called()
	return args.Get(0).([]string)
}

func TestRegistryInterface(t *testing.T) {
	mockReg := new(MockRegistry)

	// Dummy tool
	dummyTool := tools.Tool(func(ctx context.Context, args map[string]interface{}) (interface{}, error) {
		return nil, nil
	})

	mockReg.On("Register", "test", dummyTool).Return(nil)
	mockReg.On("Get", "test").Return(dummyTool, nil)
	mockReg.On("List").Return([]string{"test"})

	err := mockReg.Register("test", dummyTool)
	assert.NoError(t, err)

	tool, err := mockReg.Get("test")
	assert.NoError(t, err)
	assert.NotNil(t, tool)

	list := mockReg.List()
	assert.Contains(t, list, "test")

	mockReg.AssertExpectations(t)
}

// EOF: internal/tools/interface_test.go