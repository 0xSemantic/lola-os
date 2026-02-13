// Package observe_test verifies the observability interfaces using mocks.
//
// File: internal/observe/interface_test.go

package observe_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	"github.com/0xSemantic/lola-os/internal/observe"
)

// MockLogger implements observe.Logger for testing.
type MockLogger struct {
	mock.Mock
}

func (m *MockLogger) Debug(msg string, fields ...map[string]interface{}) {
	m.Called(msg, fields)
}
func (m *MockLogger) Info(msg string, fields ...map[string]interface{}) {
	m.Called(msg, fields)
}
func (m *MockLogger) Warn(msg string, fields ...map[string]interface{}) {
	m.Called(msg, fields)
}
func (m *MockLogger) Error(msg string, fields ...map[string]interface{}) {
	m.Called(msg, fields)
}
func (m *MockLogger) With(fields map[string]interface{}) observe.Logger {
	args := m.Called(fields)
	return args.Get(0).(observe.Logger)
}

// MockMetrics implements observe.Metrics for testing.
type MockMetrics struct {
	mock.Mock
}

func (m *MockMetrics) Counter(name string, value float64, labels ...map[string]string) {
	m.Called(name, value, labels)
}
func (m *MockMetrics) Histogram(name string, value float64, labels ...map[string]string) {
	m.Called(name, value, labels)
}
func (m *MockMetrics) Gauge(name string, value float64, labels ...map[string]string) {
	m.Called(name, value, labels)
}

// MockTracer implements observe.Tracer for testing.
type MockTracer struct {
	mock.Mock
}

func (m *MockTracer) StartSpan(ctx context.Context, name string) (context.Context, observe.Span) {
	args := m.Called(ctx, name)
	return args.Get(0).(context.Context), args.Get(1).(observe.Span)
}

// MockSpan implements observe.Span for testing.
type MockSpan struct {
	mock.Mock
}

func (m *MockSpan) End() {
	m.Called()
}
func (m *MockSpan) SetAttributes(attrs map[string]interface{}) {
	m.Called(attrs)
}
func (m *MockSpan) RecordError(err error) {
	m.Called(err)
}

func TestLoggerInterface(t *testing.T) {
	mockLogger := new(MockLogger)
	mockLogger.On("Info", "test", []map[string]interface{}{{"key": "value"}}).Return()
	mockLogger.Info("test", map[string]interface{}{"key": "value"})
	mockLogger.AssertExpectations(t)
}

func TestMetricsInterface(t *testing.T) {
	mockMetrics := new(MockMetrics)
	mockMetrics.On("Counter", "requests", 1.0, []map[string]string{{"chain": "eth"}}).Return()
	mockMetrics.Counter("requests", 1.0, map[string]string{"chain": "eth"})
	mockMetrics.AssertExpectations(t)
}

func TestTracerInterface(t *testing.T) {
	ctx := context.Background()
	mockTracer := new(MockTracer)
	mockSpan := new(MockSpan)
	mockTracer.On("StartSpan", ctx, "operation").Return(ctx, mockSpan)
	mockSpan.On("End").Return()
	mockSpan.On("RecordError", mock.Anything).Return()

	newCtx, span := mockTracer.StartSpan(ctx, "operation")
	assert.Equal(t, ctx, newCtx)
	span.End()
	span.RecordError(nil)

	mockTracer.AssertExpectations(t)
	mockSpan.AssertExpectations(t)
}

// EOF: internal/observe/interface_test.go