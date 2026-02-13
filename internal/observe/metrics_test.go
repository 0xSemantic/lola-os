package observe_test

import (
	"testing"

	"github.com/stretchr/testify/assert"

	"github.com/0xSemantic/lola-os/internal/observe"
)

func TestPrometheusMetrics_Counter(t *testing.T) {
	metrics := observe.NewPrometheusMetrics("test", "metrics")
	metrics.Counter("requests", 1, map[string]string{"chain": "eth"})
	metrics.Counter("requests", 2, map[string]string{"chain": "polygon"})
	// No panic.
}

func TestPrometheusMetrics_Histogram(t *testing.T) {
	metrics := observe.NewPrometheusMetrics("test", "metrics")
	metrics.Histogram("duration", 0.5, map[string]string{"method": "eth_call"})
	metrics.Histogram("duration", 0.7)
}

func TestPrometheusMetrics_Gauge(t *testing.T) {
	metrics := observe.NewPrometheusMetrics("test", "metrics")
	metrics.Gauge("connections", 5)
	metrics.Gauge("connections", 3)
}

// EOF: internal/observe/metrics_test.go