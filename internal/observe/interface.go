// Package observe defines the observability contracts – logging, metrics,
// and distributed tracing. All components depend on these interfaces,
// allowing the observability backend to be swapped without changing business logic.
//
// File: internal/observe/interface.go

package observe

import "context"

// Logger provides structured logging capabilities.
type Logger interface {
	// Debug logs a message at debug level.
	Debug(msg string, fields ...map[string]interface{})

	// Info logs a message at info level.
	Info(msg string, fields ...map[string]interface{})

	// Warn logs a message at warn level.
	Warn(msg string, fields ...map[string]interface{})

	// Error logs a message at error level.
	Error(msg string, fields ...map[string]interface{})

	// With returns a child logger with the given fields always attached.
	With(fields map[string]interface{}) Logger
}

// Metrics allows recording of various metric types.
type Metrics interface {
	// Counter increments a counter metric.
	Counter(name string, value float64, labels ...map[string]string)

	// Histogram records a value in a histogram distribution.
	Histogram(name string, value float64, labels ...map[string]string)

	// Gauge sets a gauge to a specific value.
	Gauge(name string, value float64, labels ...map[string]string)
}

// Tracer creates spans for distributed tracing.
type Tracer interface {
	// StartSpan begins a new span with the given name, deriving context from the parent.
	// The returned context contains the newly created span.
	StartSpan(ctx context.Context, name string) (context.Context, Span)
}

// Span represents a single unit of work in a trace.
type Span interface {
	// End finishes the span.
	End()

	// SetAttributes attaches key‑value pairs to the span.
	SetAttributes(attrs map[string]interface{})

	// RecordError marks the span as failed and records the error.
	RecordError(err error)
}

// EOF: internal/observe/interface.go