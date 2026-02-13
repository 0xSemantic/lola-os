// Package observe provides no‑op implementations of observability interfaces.
// These are used when logging/metrics/tracing are disabled or in tests.
//
// File: internal/observe/noop.go

package observe

import (
	"context"
)

// NoopLogger is a Logger that discards all output.
type NoopLogger struct{}

func (n *NoopLogger) Debug(msg string, fields ...map[string]interface{}) {}
func (n *NoopLogger) Info(msg string, fields ...map[string]interface{})  {}
func (n *NoopLogger) Warn(msg string, fields ...map[string]interface{})  {}
func (n *NoopLogger) Error(msg string, fields ...map[string]interface{}) {}
func (n *NoopLogger) With(fields map[string]interface{}) Logger          { return n }

// NoopMetrics is a Metrics that does nothing.
type NoopMetrics struct{}

func (n *NoopMetrics) Counter(name string, value float64, labels ...map[string]string) {}
func (n *NoopMetrics) Histogram(name string, value float64, labels ...map[string]string) {}
func (n *NoopMetrics) Gauge(name string, value float64, labels ...map[string]string)    {}

// NoopTracer is a Tracer that creates no‑op spans.
type NoopTracer struct{}

func (n *NoopTracer) StartSpan(ctx context.Context, name string) (context.Context, Span) {
	return ctx, &NoopSpan{}
}

// NoopSpan is a Span that does nothing.
type NoopSpan struct{}

func (n *NoopSpan) End()                                       {}
func (n *NoopSpan) SetAttributes(attrs map[string]interface{}) {}
func (n *NoopSpan) RecordError(err error)                      {}

// EOF: internal/observe/noop.go