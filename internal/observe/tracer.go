// Package observe provides OpenTelemetry tracing.
//
// File: internal/observe/tracer.go

package observe

import (
	"context"
	"fmt"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/jaeger"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
	"go.opentelemetry.io/otel/exporters/stdout/stdouttrace"
	"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	semconv "go.opentelemetry.io/otel/semconv/v1.4.0"
	"go.opentelemetry.io/otel/trace"
)

// OTelTracer implements Tracer using OpenTelemetry.
type OTelTracer struct {
	tracer trace.Tracer
	provider *sdktrace.TracerProvider
}

// NewOTelTracer creates a new OpenTelemetry tracer with the given exporter.
// Supported exporters: "otlp", "jaeger", "stdout".
func NewOTelTracer(ctx context.Context, exporterType, endpoint, serviceName string) (*OTelTracer, error) {
	var exporter sdktrace.SpanExporter
	var err error

	switch exporterType {
	case "otlp":
		exporter, err = otlptracegrpc.New(ctx,
			otlptracegrpc.WithEndpoint(endpoint),
			otlptracegrpc.WithInsecure(),
		)
	case "jaeger":
		exporter, err = jaeger.New(jaeger.WithCollectorEndpoint(
			jaeger.WithEndpoint(endpoint),
		))
	case "stdout":
		exporter, err = stdouttrace.New(
			stdouttrace.WithPrettyPrint(),
		)
	default:
		return nil, fmt.Errorf("unknown exporter type: %s", exporterType)
	}
	if err != nil {
		return nil, fmt.Errorf("create exporter: %w", err)
	}

	// Create resource with service name.
	res, err := resource.New(ctx,
		resource.WithAttributes(
			semconv.ServiceNameKey.String(serviceName),
		),
	)
	if err != nil {
		return nil, fmt.Errorf("create resource: %w", err)
	}

	// Create tracer provider.
	tp := sdktrace.NewTracerProvider(
		sdktrace.WithBatcher(exporter),
		sdktrace.WithResource(res),
	)
	otel.SetTracerProvider(tp)

	tracer := tp.Tracer("lola-os")
	return &OTelTracer{
		tracer:   tracer,
		provider: tp,
	}, nil
}

// StartSpan begins a new span with the given name.
// It returns a context containing the span and the span itself.
func (o *OTelTracer) StartSpan(ctx context.Context, name string) (context.Context, Span) {
	ctx, span := o.tracer.Start(ctx, name)
	return ctx, &OTelSpan{span: span}
}

// Shutdown flushes and shuts down the tracer provider.
func (o *OTelTracer) Shutdown(ctx context.Context) error {
	return o.provider.Shutdown(ctx)
}

// OTelSpan implements Span for OpenTelemetry.
type OTelSpan struct {
	span trace.Span
}

// End finishes the span.
func (o *OTelSpan) End() {
	o.span.End()
}

// SetAttributes attaches key‑value pairs to the span.
func (o *OTelSpan) SetAttributes(attrs map[string]interface{}) {
	var attributes []attribute.KeyValue
	for k, v := range attrs {
		attributes = append(attributes, attribute.Any(k, v))
	}
	o.span.SetAttributes(attributes...)
}

// RecordError marks the span as failed and records the error.
func (o *OTelSpan) RecordError(err error) {
	o.span.RecordError(err)
	o.span.SetStatus(sdktrace.StatusError, err.Error())
}

// EOF: internal/observe/tracer.go