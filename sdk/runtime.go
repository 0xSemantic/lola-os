// Package sdk provides the public API for LOLA OS.
//
// File: sdk/runtime.go

package sdk

import (
	"context"
	"fmt"
	"sync"

	"github.com/0xSemantic/lola-os/internal/blockchain"
	"github.com/0xSemantic/lola-os/internal/blockchain/evm"
	"github.com/0xSemantic/lola-os/internal/config"
	"github.com/0xSemantic/lola-os/internal/core"
	"github.com/0xSemantic/lola-os/internal/observe"
	"github.com/0xSemantic/lola-os/internal/security"
	"github.com/0xSemantic/lola-os/internal/security/policies"
	"github.com/0xSemantic/lola-os/internal/tools"
	"github.com/0xSemantic/lola-os/sdk/evm"
)

// Runtime is the primary handle for LOLA OS operations.
// It holds the engine, configuration, and observability components.
type Runtime struct {
	engine   *core.Engine
	config   *config.Config
	logger   observe.Logger
	metrics  observe.Metrics
	tracer   observe.Tracer
	audit    *observe.AuditLogger
	chains   map[string]blockchain.Chain // chain ID -> Chain
	mu       sync.RWMutex
}

// newRuntime constructs a fully wired Runtime from configuration.
func newRuntime(cfg *config.Config, opts *options) (*Runtime, error) {
	// 1. Initialize logger.
	logger, err := observe.NewZapLogger(
		cfg.Observability.Logging.Level,
		cfg.Observability.Logging.Format,
		cfg.Observability.Logging.Output,
	)
	if err != nil {
		return nil, fmt.Errorf("init logger: %w", err)
	}

	// 2. Initialize metrics (if enabled).
	var metrics observe.Metrics = &observe.NoopMetrics{}
	if cfg.Observability.Metrics.Enabled {
		metrics = observe.NewPrometheusMetrics("lola", "agent")
		// Expose metrics endpoint in a goroutine if addr set.
		if cfg.Observability.Metrics.Addr != "" {
			go func() {
				http.Handle(cfg.Observability.Metrics.Path, metrics.(*observe.PrometheusMetrics).Handler())
				if err := http.ListenAndServe(cfg.Observability.Metrics.Addr, nil); err != nil {
					logger.Error("metrics server failed", map[string]interface{}{"error": err})
				}
			}()
		}
	}

	// 3. Initialize tracing (if enabled).
	var tracer observe.Tracer = &observe.NoopTracer{}
	if cfg.Observability.Tracing.Enabled {
		oteltracer, err := observe.NewOTelTracer(
			context.Background(),
			cfg.Observability.Tracing.Exporter,
			cfg.Observability.Tracing.Endpoint,
			cfg.Observability.Tracing.ServiceName,
		)
		if err != nil {
			logger.Warn("failed to init tracer, using noop", map[string]interface{}{"error": err})
		} else {
			tracer = oteltracer
		}
	}

	// 4. Initialize audit logger.
	audit, err := observe.NewAuditLogger(
		cfg.Observability.Audit.Path,
		cfg.Observability.Audit.Enabled,
	)
	if err != nil {
		return nil, fmt.Errorf("init audit: %w", err)
	}

	// 5. Initialize tool registry.
	reg := globalRegistry 

	// 6. Register built‑in tools.
	reg.Register("balance", builtin.Balance)
	reg.Register("transfer", builtin.Transfer)
	reg.Register("deploy", builtin.Deploy)

	// 7. Initialize security enforcer and add policies.
	enforcer := security.NewEnforcer()

	// Read‑only policy.
	if cfg.Security.ReadOnly || opts.readOnly {
		enforcer.AddPolicy(policies.NewReadOnlyPolicy())
	}

	// Transaction limits.
	if cfg.Security.MaxTransactionValue != nil {
		enforcer.AddPolicy(policies.NewLimitPolicy(cfg.Security.MaxTransactionValue, nil))
	}
	if cfg.Security.DailyLimit != nil {
		enforcer.AddPolicy(policies.NewLimitPolicy(nil, cfg.Security.DailyLimit))
	}

	// Whitelist/blacklist.
	if len(cfg.Security.AllowedAddresses) > 0 || len(cfg.Security.BlockedAddresses) > 0 {
		enforcer.AddPolicy(policies.NewWhitelistPolicy(
			cfg.Security.AllowedAddresses,
			cfg.Security.BlockedAddresses,
		))
	}

	// HITL.
	if cfg.Security.HITL != nil && cfg.Security.HITL.Enabled {
		enforcer.AddPolicy(policies.NewHITLPolicy(
			cfg.Security.HITL.Threshold,
			cfg.Security.HITL.Timeout,
			cfg.Security.HITL.Mode,
		))
	}

	// 8. Initialize engine.
	engine := core.NewEngine(reg, enforcer, logger)

	// 9. Initialize blockchain connections.
	chains := make(map[string]blockchain.Chain)
	for name, chainCfg := range cfg.Chains {
		if chainCfg.RPC == "" {
			continue
		}
		// Create wallet if keystore configured.
		var wallet blockchain.Wallet
		if cfg.Wallet != nil && cfg.Wallet.KeystorePath != "" && !cfg.Security.ReadOnly && !opts.readOnly {
			passphrase := cfg.Wallet.PassphraseEnv
			if passphrase == "" {
				passphrase = opts.keystorePass
			}
			if passphrase != "" {
				w, err := evm.NewKeystore(cfg.Wallet.KeystorePath, passphrase)
				if err != nil {
					logger.Warn("failed to load keystore, operating in read‑only",
						map[string]interface{}{"error": err, "path": cfg.Wallet.KeystorePath})
				} else {
					wallet = w
				}
			}
		}

		// Create retry config.
		retryCfg := &evm.RetryConfig{
			MaxAttempts:    chainCfg.RetryConfig.MaxAttempts,
			InitialBackoff: chainCfg.RetryConfig.InitialBackoff,
			MaxBackoff:     chainCfg.RetryConfig.MaxBackoff,
			BackoffFactor:  chainCfg.RetryConfig.BackoffFactor,
		}
		if opts.rpcRetries > 0 {
			retryCfg.MaxAttempts = opts.rpcRetries
		}
		if opts.rpcBackoff > 0 {
			retryCfg.InitialBackoff = opts.rpcBackoff
		}

		gw, err := evm.NewEVMGateway(context.Background(), chainCfg.RPC, logger, retryCfg, wallet)
		if err != nil {
			logger.Error("failed to connect to chain",
				map[string]interface{}{"chain": name, "rpc": chainCfg.RPC, "error": err})
			continue
		}
		chains[name] = gw
	}

	rt := &Runtime{
		engine:  engine,
		config:  cfg,
		logger:  logger,
		metrics: metrics,
		tracer:  tracer,
		audit:   audit,
		chains:  chains,
	}

	return rt, nil
}

// Run executes an agent function within a session.
func (r *Runtime) Run(ctx context.Context, fn func(context.Context, *Runtime) error) error {
	// Determine default chain ID.
	defaultChain := r.config.Chains[r.getDefaultChainID()]
	var chain blockchain.Chain
	if defaultChain != nil {
		chain = r.chains[r.getDefaultChainID()]
	}

	sess := r.engine.CreateSession(r.getDefaultChainID(), chain)
	ctx = core.ContextWithSession(ctx, sess)
	defer r.engine.CloseSession(sess.ID)

	// Add logger and tracer to context.
	ctx = context.WithValue(ctx, loggerKey{}, sess.Logger)
	if r.tracer != nil {
		ctx, _ = r.tracer.StartSpan(ctx, "agent-run")
	}

	return fn(ctx, r)
}

// getDefaultChainID returns the configured default chain.
func (r *Runtime) getDefaultChainID() string {
	for id, chain := range r.config.Chains {
		if chain.Default {
			return id
		}
	}
	// Fallback to first chain.
	for id := range r.config.Chains {
		return id
	}
	return ""
}

// Execute runs a tool by name.
func (r *Runtime) Execute(ctx context.Context, name string, args map[string]interface{}) (interface{}, error) {
	return r.engine.Execute(ctx, name, args)
}

// Close cleans up resources (audit log, tracer, etc.).
func (r *Runtime) Close() error {
	if r.audit != nil {
		r.audit.Close()
	}
	if tracer, ok := r.tracer.(*observe.OTelTracer); ok {
		tracer.Shutdown(context.Background())
	}
	if logger, ok := r.logger.(*observe.ZapLogger); ok {
		logger.Sync()
	}
	return nil
}

// loggerKey is a context key for the logger.
type loggerKey struct{}

// EVM returns an EVM client for the chain associated with the current session.
// The context must contain a session (i.e., be from inside Run).
func (r *Runtime) EVM(ctx context.Context) (*evm.Client, error) {
	sess := core.SessionFromContext(ctx)
	if sess == nil {
		return nil, fmt.Errorf("evm client: no session in context (must be called inside Run)")
	}
	if sess.Chain == nil {
		return nil, fmt.Errorf("evm client: no blockchain chain in session")
	}
	return evm.NewClient(sess), nil
}

// EOF: sdk/runtime.go