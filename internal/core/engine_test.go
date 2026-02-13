// Package core tests the engine internals.
//
// File: internal/core/engine_test.go

package core

import (
	"context"
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/require"

	"github.com/0xSemantic/lola-os/internal/observe"
	"github.com/0xSemantic/lola-os/internal/security"
	"github.com/0xSemantic/lola-os/internal/tools"
)

// Mock implementations (same as above but unexported within the test file)
type mockRegistry struct {
	mock.Mock
}

func (m *mockRegistry) Register(name string, tool tools.Tool) error {
	args := m.Called(name, tool)
	return args.Error(0)
}
func (m *mockRegistry) Get(name string) (tools.Tool, error) {
	args := m.Called(name)
	return args.Get(0).(tools.Tool), args.Error(1)
}
func (m *mockRegistry) List() []string {
	args := m.Called()
	return args.Get(0).([]string)
}

type mockEnforcer struct {
	mock.Mock
}

func (m *mockEnforcer) AddPolicy(policy security.Policy) {
	m.Called(policy)
}
func (m *mockEnforcer) Evaluate(ctx context.Context, evalCtx *security.EvaluationContext) error {
	args := m.Called(ctx, evalCtx)
	return args.Error(0)
}

type mockLogger struct {
	mock.Mock
}

func (m *mockLogger) Debug(msg string, fields ...map[string]interface{}) {
	m.Called(msg, fields)
}
func (m *mockLogger) Info(msg string, fields ...map[string]interface{}) {
	m.Called(msg, fields)
}
func (m *mockLogger) Warn(msg string, fields ...map[string]interface{}) {
	m.Called(msg, fields)
}
func (m *mockLogger) Error(msg string, fields ...map[string]interface{}) {
	m.Called(msg, fields)
}
func (m *mockLogger) With(fields map[string]interface{}) observe.Logger {
	args := m.Called(fields)
	return args.Get(0).(observe.Logger)
}

func TestEngine_CreateAndGetSession(t *testing.T) {
	reg := new(mockRegistry)
	sec := new(mockEnforcer)
	log := new(mockLogger)

	log.On("With", mock.Anything).Return(log).Once()
	log.On("Info", "session created", mock.Anything).Return().Once()

	engine := NewEngine(reg, sec, log)
	sess := engine.CreateSession("ethereum")

	assert.NotEmpty(t, sess.ID)
	assert.Equal(t, "ethereum", sess.DefaultChainID)

	retrieved := engine.GetSession(sess.ID)
	assert.Equal(t, sess, retrieved)

	engine.CloseSession(sess.ID)
	assert.Nil(t, engine.GetSession(sess.ID))

	log.AssertExpectations(t)
}

func TestEngine_Execute_Success(t *testing.T) {
	reg := new(mockRegistry)
	sec := new(mockEnforcer)
	log := new(mockLogger)

	dummyTool := tools.Tool(func(ctx context.Context, args map[string]interface{}) (interface{}, error) {
		return "result", nil
	})

	reg.On("Get", "test").Return(dummyTool, nil).Once()
	sec.On("Evaluate", mock.Anything, mock.Anything).Return(nil).Once()

	log.On("With", mock.Anything).Return(log).Once()
	log.On("Info", "session created", mock.Anything).Return().Once()
	log.On("Info", "executing tool", mock.Anything).Return().Once()
	log.On("Info", "tool executed successfully", mock.Anything).Return().Once()

	engine := NewEngine(reg, sec, log)
	ctx := context.Background()

	result, err := engine.Execute(ctx, "test", map[string]interface{}{"key": "value"})
	require.NoError(t, err)
	assert.Equal(t, "result", result)

	reg.AssertExpectations(t)
	sec.AssertExpectations(t)
	log.AssertExpectations(t)
}

func TestEngine_Execute_ToolNotFound(t *testing.T) {
	reg := new(mockRegistry)
	sec := new(mockEnforcer)
	log := new(mockLogger)

	reg.On("Get", "missing").Return(nil, tools.ErrNotFound).Once()

	log.On("With", mock.Anything).Return(log).Once()
	log.On("Info", "session created", mock.Anything).Return().Once()

	engine := NewEngine(reg, sec, log)
	ctx := context.Background()

	_, err := engine.Execute(ctx, "missing", nil)
	assert.ErrorIs(t, err, tools.ErrNotFound)

	reg.AssertExpectations(t)
	sec.AssertNotCalled(t, "Evaluate")
}

func TestEngine_Execute_SecurityDenied(t *testing.T) {
	reg := new(mockRegistry)
	sec := new(mockEnforcer)
	log := new(mockLogger)

	dummyTool := tools.Tool(func(ctx context.Context, args map[string]interface{}) (interface{}, error) {
		return "result", nil
	})
	reg.On("Get", "test").Return(dummyTool, nil).Once()

	denyErr := errors.New("daily limit exceeded")
	sec.On("Evaluate", mock.Anything, mock.Anything).Return(denyErr).Once()

	log.On("With", mock.Anything).Return(log).Once()
	log.On("Info", "session created", mock.Anything).Return().Once()
	log.On("Warn", "security policy blocked execution", mock.Anything).Return().Once()

	engine := NewEngine(reg, sec, log)
	ctx := context.Background()

	_, err := engine.Execute(ctx, "test", nil)
	assert.ErrorContains(t, err, "security policy denied")
	assert.ErrorIs(t, err, denyErr)

	reg.AssertExpectations(t)
	sec.AssertExpectations(t)
	log.AssertExpectations(t)
}

func TestEngine_Execute_ToolError(t *testing.T) {
	reg := new(mockRegistry)
	sec := new(mockEnforcer)
	log := new(mockLogger)

	toolErr := errors.New("rpc failed")
	failingTool := tools.Tool(func(ctx context.Context, args map[string]interface{}) (interface{}, error) {
		return nil, toolErr
	})
	reg.On("Get", "test").Return(failingTool, nil).Once()
	sec.On("Evaluate", mock.Anything, mock.Anything).Return(nil).Once()

	log.On("With", mock.Anything).Return(log).Once()
	log.On("Info", "session created", mock.Anything).Return().Once()
	log.On("Info", "executing tool", mock.Anything).Return().Once()
	log.On("Error", "tool execution failed", mock.Anything).Return().Once()

	engine := NewEngine(reg, sec, log)
	ctx := context.Background()

	_, err := engine.Execute(ctx, "test", nil)
	assert.ErrorIs(t, err, toolErr)

	reg.AssertExpectations(t)
	sec.AssertExpectations(t)
	log.AssertExpectations(t)
}

func TestEngine_Execute_WithExistingSession(t *testing.T) {
	reg := new(mockRegistry)
	sec := new(mockEnforcer)
	log := new(mockLogger)

	dummyTool := tools.Tool(func(ctx context.Context, args map[string]interface{}) (interface{}, error) {
		return "ok", nil
	})
	reg.On("Get", "test").Return(dummyTool, nil).Once()
	sec.On("Evaluate", mock.Anything, mock.Anything).Return(nil).Once()

	log.On("With", mock.Anything).Return(log).Once()
	log.On("Info", "session created", mock.Anything).Return().Once()
	// No additional session creation logs because we attach existing session.
	log.On("Info", "executing tool", mock.Anything).Return().Once()
	log.On("Info", "tool executed successfully", mock.Anything).Return().Once()

	engine := NewEngine(reg, sec, log)
	sess := engine.CreateSession("polygon")
	ctx := contextWithSession(context.Background(), sess)

	_, err := engine.Execute(ctx, "test", nil)
	assert.NoError(t, err)

	reg.AssertExpectations(t)
	sec.AssertExpectations(t)
	log.AssertExpectations(t)
}

// EOF: internal/core/engine_test.go