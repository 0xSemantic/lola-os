// Package observe provides Prometheus‑based metrics.
//
// File: internal/observe/metrics.go

package observe

import (
	"net/http"
	"sync"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// PrometheusMetrics implements Metrics using Prometheus.
type PrometheusMetrics struct {
	mu         sync.RWMutex
	counters   map[string]*prometheus.CounterVec
	histograms map[string]*prometheus.HistogramVec
	gauges     map[string]*prometheus.GaugeVec
	namespace  string
	subsystem  string
}

// NewPrometheusMetrics creates a new Prometheus metrics registry.
// If namespace/subsystem are provided, they are prefixed to metric names.
func NewPrometheusMetrics(namespace, subsystem string) *PrometheusMetrics {
	return &PrometheusMetrics{
		counters:   make(map[string]*prometheus.CounterVec),
		histograms: make(map[string]*prometheus.HistogramVec),
		gauges:     make(map[string]*prometheus.GaugeVec),
		namespace:  namespace,
		subsystem:  subsystem,
	}
}

// Counter increments a counter metric.
// If the metric does not exist, it is registered automatically.
// Labels are optional key‑value pairs; all label keys must be consistent per metric.
func (p *PrometheusMetrics) Counter(name string, value float64, labels ...map[string]string) {
	p.mu.Lock()
	defer p.mu.Unlock()

	counter, exists := p.counters[name]
	if !exists {
		labelKeys := p.extractLabelKeys(labels...)
		counter = promauto.NewCounterVec(
			prometheus.CounterOpts{
				Namespace: p.namespace,
				Subsystem: p.subsystem,
				Name:      name,
				Help:      "Counter " + name,
			},
			labelKeys,
		)
		p.counters[name] = counter
	}

	// Add labels.
	if len(labels) > 0 && len(labels[0]) > 0 {
		counter.With(labels[0]).Add(value)
	} else {
		counter.With(prometheus.Labels{}).Add(value)
	}
}

// Histogram records a value in a histogram distribution.
func (p *PrometheusMetrics) Histogram(name string, value float64, labels ...map[string]string) {
	p.mu.Lock()
	defer p.mu.Unlock()

	hist, exists := p.histograms[name]
	if !exists {
		labelKeys := p.extractLabelKeys(labels...)
		hist = promauto.NewHistogramVec(
			prometheus.HistogramOpts{
				Namespace: p.namespace,
				Subsystem: p.subsystem,
				Name:      name,
				Help:      "Histogram " + name,
				Buckets:   prometheus.DefBuckets,
			},
			labelKeys,
		)
		p.histograms[name] = hist
	}

	if len(labels) > 0 && len(labels[0]) > 0 {
		hist.With(labels[0]).Observe(value)
	} else {
		hist.With(prometheus.Labels{}).Observe(value)
	}
}

// Gauge sets a gauge to a specific value.
func (p *PrometheusMetrics) Gauge(name string, value float64, labels ...map[string]string) {
	p.mu.Lock()
	defer p.mu.Unlock()

	gauge, exists := p.gauges[name]
	if !exists {
		labelKeys := p.extractLabelKeys(labels...)
		gauge = promauto.NewGaugeVec(
			prometheus.GaugeOpts{
				Namespace: p.namespace,
				Subsystem: p.subsystem,
				Name:      name,
				Help:      "Gauge " + name,
			},
			labelKeys,
		)
		p.gauges[name] = gauge
	}

	if len(labels) > 0 && len(labels[0]) > 0 {
		gauge.With(labels[0]).Set(value)
	} else {
		gauge.With(prometheus.Labels{}).Set(value)
	}
}

// Handler returns an HTTP handler for Prometheus metrics scraping.
func (p *PrometheusMetrics) Handler() http.Handler {
	return promhttp.Handler()
}

// extractLabelKeys merges all label maps and returns a slice of unique keys.
func (p *PrometheusMetrics) extractLabelKeys(labels ...map[string]string) []string {
	keySet := make(map[string]bool)
	for _, m := range labels {
		for k := range m {
			keySet[k] = true
		}
	}
	keys := make([]string, 0, len(keySet))
	for k := range keySet {
		keys = append(keys, k)
	}
	return keys
}

// EOF: internal/observe/metrics.go