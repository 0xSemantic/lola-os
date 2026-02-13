# LOLA OS Makefile
# File: Makefile

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
GO         ?= go
GOLANGCI_LINT ?= golangci-lint
VERSION    ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
LDFLAGS    := -ldflags "-X main.version=$(VERSION)"
MODULE     := github.com/0xSemantic/lola-os

# ----------------------------------------------------------------------
# Phony targets
# ----------------------------------------------------------------------
.PHONY: all build test lint tidy clean examples help release push

all: tidy lint test build examples

# ----------------------------------------------------------------------
# Build & Verify
# ----------------------------------------------------------------------
build:
	@echo ">>> Building all packages"
	$(GO) build ./...

# ----------------------------------------------------------------------
# Testing
# ----------------------------------------------------------------------
test:
	@echo ">>> Running unit tests with race detector"
	$(GO) test -v -race -coverprofile=coverage.out ./...
	$(GO) tool cover -html=coverage.out -o coverage.html

test-integration:
	@echo ">>> Running integration tests (requires -tags=integration)"
	$(GO) test -v -tags=integration ./...

bench:
	@echo ">>> Running benchmarks"
	$(GO) test -bench=. -benchmem ./...

# ----------------------------------------------------------------------
# Code Quality
# ----------------------------------------------------------------------
lint:
	@echo ">>> Running golangci-lint"
	$(GOLANGCI_LINT) run ./...

tidy:
	@echo ">>> Tidying go.mod and verifying"
	$(GO) mod tidy
	$(GO) mod verify

fmt:
	@echo ">>> Formatting code"
	$(GO) fmt ./...

vet:
	@echo ">>> Running go vet"
	$(GO) vet ./...

# ----------------------------------------------------------------------
# Examples (ensure they compile)
# ----------------------------------------------------------------------
examples:
	@echo ">>> Building all examples"
	@for ex in sdk/examples/*/; do \
		echo "   Building $$ex"; \
		(cd $$ex && $(GO) build) || exit 1; \
	done

# ----------------------------------------------------------------------
# Release Management
# ----------------------------------------------------------------------
release: tidy lint test examples
	@echo ">>> All checks passed. Ready to release."
	@echo ">>> Current version: $(VERSION)"
	@echo ">>> To create a new tag, run:"
	@echo "    git tag -a v1.0.0-alpha.x -m \"Release v1.0.0-alpha.x\""
	@echo "    git push origin v1.0.0-alpha.x"

tag:
	@if [ -z "$(TAG)" ]; then \
		echo "Usage: make tag TAG=v1.0.0-alpha.1"; \
		exit 1; \
	fi
	git tag -a $(TAG) -m "Release $(TAG)"
	git push origin $(TAG)

# ----------------------------------------------------------------------
# Clean
# ----------------------------------------------------------------------
clean:
	@echo ">>> Cleaning generated files"
	rm -f coverage.out coverage.html
	$(GO) clean ./...

# ----------------------------------------------------------------------
# Help
# ----------------------------------------------------------------------
help:
	@echo "LOLA OS Makefile"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Build & Verify:"
	@echo "  build         - compile all packages"
	@echo ""
	@echo "Testing:"
	@echo "  test          - run unit tests with coverage"
	@echo "  test-integration - run integration tests (requires -tags=integration)"
	@echo "  bench         - run benchmarks"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          - run golangci-lint"
	@echo "  tidy          - tidy go.mod and verify"
	@echo "  fmt           - format all code"
	@echo "  vet           - run go vet"
	@echo ""
	@echo "Examples:"
	@echo "  examples      - compile all example agents"
	@echo ""
	@echo "Release:"
	@echo "  release       - run all checks and print instructions"
	@echo "  tag TAG=...   - create and push a git tag"
	@echo ""
	@echo "Utility:"
	@echo "  clean         - remove generated files"
	@echo "  help          - show this message"