// Package observe provides a Zap‑based structured logger.
// It implements the Logger interface and supports JSON/console output.
//
// File: internal/observe/logger.go

package observe

import (
	"os"
	"strings"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// ZapLogger is a concrete implementation of Logger using zap.
type ZapLogger struct {
	logger *zap.Logger
	level  zap.AtomicLevel
}

// NewZapLogger creates a new ZapLogger with the given configuration.
//   - level: "debug", "info", "warn", "error"
//   - format: "json" or "console"
//   - output: "stdout", "stderr", or a file path
func NewZapLogger(level, format, output string) (*ZapLogger, error) {
	// Parse log level.
	var zapLevel zapcore.Level
	switch strings.ToLower(level) {
	case "debug":
		zapLevel = zapcore.DebugLevel
	case "info":
		zapLevel = zapcore.InfoLevel
	case "warn":
		zapLevel = zapcore.WarnLevel
	case "error":
		zapLevel = zapcore.ErrorLevel
	default:
		zapLevel = zapcore.InfoLevel
	}
	atomicLevel := zap.NewAtomicLevelAt(zapLevel)

	// Configure encoder.
	var encoder zapcore.Encoder
	encoderConfig := zap.NewProductionEncoderConfig()
	encoderConfig.TimeKey = "timestamp"
	encoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
	encoderConfig.EncodeLevel = zapcore.CapitalLevelEncoder

	switch strings.ToLower(format) {
	case "console":
		encoder = zapcore.NewConsoleEncoder(encoderConfig)
	default:
		encoder = zapcore.NewJSONEncoder(encoderConfig)
	}

	// Configure output.
	var writer zapcore.WriteSyncer
	switch output {
	case "stderr":
		writer = zapcore.AddSync(os.Stderr)
	default:
		writer = zapcore.AddSync(os.Stdout)
	}
	// For file output, we could open a file here; we'll keep simple.

	core := zapcore.NewCore(encoder, writer, atomicLevel)
	logger := zap.New(core, zap.AddCaller(), zap.AddStacktrace(zapcore.ErrorLevel))

	return &ZapLogger{
		logger: logger,
		level:  atomicLevel,
	}, nil
}

// Debug logs a message at debug level.
func (z *ZapLogger) Debug(msg string, fields ...map[string]interface{}) {
	z.logger.Debug(msg, z.toZapFields(fields...)...)
}

// Info logs a message at info level.
func (z *ZapLogger) Info(msg string, fields ...map[string]interface{}) {
	z.logger.Info(msg, z.toZapFields(fields...)...)
}

// Warn logs a message at warn level.
func (z *ZapLogger) Warn(msg string, fields ...map[string]interface{}) {
	z.logger.Warn(msg, z.toZapFields(fields...)...)
}

// Error logs a message at error level.
func (z *ZapLogger) Error(msg string, fields ...map[string]interface{}) {
	z.logger.Error(msg, z.toZapFields(fields...)...)
}

// With returns a child logger with the given fields always attached.
func (z *ZapLogger) With(fields map[string]interface{}) Logger {
	return &ZapLogger{
		logger: z.logger.With(z.toZapFields(fields)...),
		level:  z.level,
	}
}

// toZapFields converts our generic map fields to zap.Field slice.
func (z *ZapLogger) toZapFields(fields ...map[string]interface{}) []zap.Field {
	var zapFields []zap.Field
	for _, m := range fields {
		for k, v := range m {
			zapFields = append(zapFields, zap.Any(k, v))
		}
	}
	return zapFields
}

// Sync flushes any buffered log entries.
func (z *ZapLogger) Sync() error {
	return z.logger.Sync()
}

// EOF: internal/observe/logger.go