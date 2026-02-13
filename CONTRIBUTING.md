# Contributing to LOLA OS

First off, thank you for considering contributing to LOLA OS. It’s people like you that make LOLA OS such a great tool. We welcome contributions of all kinds—whether it’s a typo fix, a new blockchain adapter, a security policy plugin, or a thoughtful discussion on our architecture.

**We are building the onchain operating system for agents, and every contribution matters.**

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
   - [Fork & Clone](#fork--clone)
   - [Build & Test](#build--test)
3. [Development Principles](#development-principles)
   - [SOLID Design](#solid-design)
   - [Self‑Documenting Code](#selfdocumenting-code)
   - [File Header Template](#file-header-template)
   - [Import Grouping](#import-grouping)
   - [Inline Comments](#inline-comments)
   - [End‑of‑File Marker](#endoffile-marker)
4. [Coding Standards](#coding-standards)
   - [Go Style](#go-style)
   - [Interface Design](#interface-design)
   - [Error Handling](#error-handling)
   - [Testing](#testing)
5. [Submitting Changes](#submitting-changes)
   - [Pull Request Process](#pull-request-process)
   - [Commit Messages](#commit-messages)
   - [Signing Your Work](#signing-your-work)
6. [Reporting Issues](#reporting-issues)
7. [Community & Support](#community--support)
8. [License](#license)

---

## Code of Conduct

This project and everyone participating in it is governed by the **LOLA OS Code of Conduct**. By participating, you are expected to uphold this code. Please report unacceptable behavior to [lola@0xsemantic.com](mailto:lola@0xsemantic.com).

[Read the full Code of Conduct →](CODE_OF_CONDUCT.md)

---

## Getting Started

### Fork & Clone

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/lola-os.git
   cd lola-os
   ```
3. Add the original repository as upstream:
   ```bash
   git remote add upstream https://github.com/0xSemantic/lola-os.git
   ```

### Build & Test

LOLA OS uses Go modules. Ensure you have Go 1.22+ installed.

```bash
# Download dependencies
go mod download

# Run all tests
make test

# Run linter
make lint

# Build the SDK (no standalone binary in V1 alpha)
go build ./...
```

All tests **must** pass before submitting a pull request.

---

## Development Principles

We take engineering rigor seriously. Every line of code in LOLA OS must adhere to two non‑negotiable principles: **SOLID design** and **self‑documenting code**.

### SOLID Design

| Principle | Application |
|-----------|-------------|
| **Single Responsibility** | A package, type, or function should have one clear responsibility. |
| **Open‑Closed** | Design interfaces that allow extension without modification. New chain adapters, security policies, or config providers never require changes to core packages. |
| **Liskov Substitution** | Any implementation of an interface must be safely substitutable. |
| **Interface Segregation** | Keep interfaces focused; a `Chain` interface does not include wallet methods. |
| **Dependency Inversion** | Depend on abstractions, not concretions. The `core.Engine` depends on `blockchain.Chain`, not `evm.EVMGateway`. |

### Self‑Documenting Code

Every `.go` file **must** follow this exact structure:

1. **Package documentation** – a multi‑line comment describing the package’s purpose, key types, and important interactions.
2. **File path comment** – a single line `// File: path/from/root.go`.
3. **Imports** – grouped logically (stdlib, external, internal).
4. **Code** – with strategic inline comments explaining *why*, not *what*.
5. **EOF marker** – `// EOF: path/from/root.go`.

#### File Header Template

```go
// Package example provides a reference implementation for LOLA OS components.
// It demonstrates the required self‑documentation structure.
//
// Key types:
//   - Component   : does X, depends on Y.
//   - Config      : holds settings for Z.
//
// This package implements the Fooer interface defined in internal/iface.
// It is intended to be used only via the SDK; direct imports are discouraged.
//
// File: internal/example/component.go

package example

import (
    "context"
    "fmt"

    "github.com/0xSemantic/lola-os/internal/iface"
)

// Component is responsible for ...
type Component struct {
    // ...
}

// NewComponent creates a Component with injected dependencies.
func NewComponent(cfg *Config, logger iface.Logger) *Component {
    // ...
}

// EOF: internal/example/component.go
```

**Every** exported symbol must have a `godoc` comment. Unexported symbols should have comments when their purpose is non‑obvious.

### Import Grouping

Imports must be grouped in three blocks, each separated by a blank line:

```go
import (
    "context"
    "fmt"
    "sync"

    "github.com/ethereum/go-ethereum/common"
    "github.com/prometheus/client_golang/prometheus"

    "github.com/0xSemantic/lola-os/internal/iface"
    "github.com/0xSemantic/lola-os/sdk/types"
)
```

1. Standard library
2. External dependencies (including `go-ethereum`, `prometheus`, etc.)
3. Internal LOLA OS packages

### Inline Comments

Comments should explain **why** the code exists, not **what** it does.  
Good: `// Use a buffered channel to prevent blocking the main event loop.`  
Bad: `// Create a channel.`

### End‑of‑File Marker

Every file must end with:

```go
// EOF: path/from/root.go
```

This makes it trivial to verify file completeness and prevents accidental truncation.

---

## Coding Standards

### Go Style

- Use `gofmt` (or `go fmt`) – no exceptions.
- Follow the recommendations in [Effective Go](https://golang.org/doc/effective_go) and [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments).
- Line length: aim for < 100 characters, but readability trumps strict limits.
- Use `camelCase` for unexported, `PascalCase` for exported identifiers.

### Interface Design

- Define interfaces **in the package that consumes them**, not in the package that implements them (exceptions: shared interfaces like `Chain` live in `internal/blockchain`).
- Keep interfaces **small** – one or two methods is ideal.
- Accept interfaces, return structs.

### Error Handling

- Errors should be wrapped with context using `fmt.Errorf("...: %w", err)`.
- Sentinel errors are defined at the package level (e.g., `var ErrNotFound = errors.New("not found")`).
- Do not panic; return errors.

### Testing

- All new code must be accompanied by **unit tests**.
- Use table‑driven tests where appropriate.
- Mock dependencies via interfaces (no brittle global state).
- Run `make test` locally before pushing; we enforce coverage thresholds in CI.
- Integration tests that hit real RPC endpoints are placed in `*_test.go` with a `//go:build integration` build tag.

---

## Submitting Changes

### Pull Request Process

1. **Create an issue** – for significant changes, open an issue first to discuss design. For trivial fixes (typos, docs), a direct PR is okay.
2. **Work in a feature branch** – branch from `main`, name it meaningfully: `feat/add-solana-adapter`, `fix/keystore-race`, `docs/update-readme`.
3. **Keep commits atomic** – each commit should do one thing. We encourage rebasing before opening a PR.
4. **Write good commit messages** – see [Commit Messages](#commit-messages) below.
5. **Open a draft pull request** early to get feedback.
6. **Ensure CI passes** – all tests and linters must be green.
7. **Request review** – at least one maintainer approval is required.
8. **Merge** – after approval, maintainers will merge your PR.

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat` – new feature for the user (e.g., new chain adapter, new SDK function).
- `fix` – bug fix.
- `docs` – documentation only.
- `style` – code style, formatting, no functional change.
- `refactor` – code change that neither fixes a bug nor adds a feature.
- `perf` – performance improvement.
- `test` – adding missing tests, refactoring tests.
- `chore` – updating build tasks, package manager, etc.

**Scope:** e.g., `evm`, `keystore`, `sdk`, `security`. Omit if not applicable.

**Example:**  
```
feat(evm): add support for EIP-1559 dynamic fees

Implements gas fee estimation using the new fee history API.
Falls back to legacy gas price if not available.

Closes #123
```

### Signing Your Work

We require all commits to be **signed** with a GPG key.  
[GitHub’s guide on signing commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)

---

## Reporting Issues

- **Bug reports** – use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include clear steps to reproduce, expected vs. actual behaviour, and your environment.
- **Feature requests** – use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md). Explain the use case and why it belongs in LOLA OS.
- **Security vulnerabilities** – **do not** open a public issue. Email [lola@0xsemantic.com](mailto:lola@0xsemantic.com) directly.

---

## Community & Support

- **Discord** – [https://discord.gg/lola-os](https://discord.gg/lola-os) – real‑time chat, help, and discussions.
- **Twitter** – [@0xSemantic](https://twitter.com/0xSemantic) – project updates.
- **GitHub Discussions** – [https://github.com/0xSemantic/lola-os/discussions](https://github.com/0xSemantic/lola-os/discussions) – long‑form ideas and questions.

We strive to be a welcoming and inclusive community. All contributions, questions, and comments are valued.

---

## License

By contributing, you agree that your contributions will be licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.

---

**Thank you for helping us make every agent blockchain‑native.**  
– The LOLA OS Team

[![Star History Chart](https://api.star-history.com/svg?repos=0xSemantic/lola-os&type=Date)](https://star-history.com/#0xSemantic/lola-os&Date)