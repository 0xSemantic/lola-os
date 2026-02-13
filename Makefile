.PHONY: test lint tidy help

GO ?= go
GOLANGCI_LINT ?= golangci-lint

test:
	$(GO) test -v -race -coverprofile=coverage.out ./...
	$(GO) tool cover -html=coverage.out -o coverage.html

lint:
	$(GOLANGCI_LINT) run ./...

tidy:
	$(GO) mod tidy
	$(GO) mod verify

help:
	@echo "Available targets:"
	@echo "  test   - run unit tests with race detector and coverage"
	@echo "  lint   - run golangci-lint"
	@echo "  tidy   - tidy go.mod and verify dependencies"
	@echo "  help   - print this help"