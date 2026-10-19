---
name: golang-project-layout
description: "Set up Go modules, package directories and go.work workspaces. Use for layout changes; read golang-best-practices first for service architecture when available."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code, Codex or similar harness, and for projects using Golang.
metadata:
  author: samber
  version: "1.4.2"
  openclaw:
    emoji: "📁"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - go
    install: []
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(golangci-lint:*) Bash(git:*) Agent AskUserQuestion
---

**Persona:** You are a Go project architect. You right-size structure to the problem — a script stays flat, a service gets layers only when justified by actual complexity.

**Scope:** Preserve explicit user choices and existing project structure. A tiny service may stay in one package with a root main.go. Ask a question only when an unresolved architecture or dependency decision materially changes the work; do not ask again for choices the user has already supplied.

# Go Project Layout

## Architecture Decision: Ask First

Start with the smallest structure that expresses the required behavior. A single-package service or CLI is a valid initial design. If the user requests a particular architecture, follow it; discuss alternatives only when there is a real unresolved tradeoff. Do not require an architecture selection ceremony for routine setup.

→ See `golang-design-patterns` skill for detailed architecture guides with file trees and code examples.

## Dependency Injection: Ask Next

Reuse existing wiring. For a small new program, explicit constructors are sufficient unless the user requests a DI library or lifecycle framework. Read `golang-dependency-injection` only when choosing or changing the injection approach is part of the task.

## 12-Factor App

For applications (services, APIs, workers), follow [12-Factor App](https://12factor.net/) conventions: config via environment variables, logs to stdout, stateless processes, graceful shutdown, backing services as attached resources, and admin tasks as one-off commands (e.g., `cmd/migrate/`).

## Quick Start: Choose Your Project Type

| Project Type | Use When | Key Directories |
| --- | --- | --- |
| **Small CLI or service** | One executable with a few behaviors | Module root package; split files by responsibility |
| **Library** | Reusable public Go API | Module root package; `internal/` only for genuinely private packages |
| **Multiple executables** | Distinct entry points or deployment lifecycles | `cmd/{name}/` and shared packages when useful |
| **Several business capabilities** | Responsibilities need separate packages | Capability packages; preserve existing naming |
| **Workspace** | Multiple modules with independent boundaries | `go.work` when needed, not one module per package by default |

## Module Naming Conventions

### Module Name (go.mod)

Your module path in `go.mod` should:

- **MUST match your repository URL**: `github.com/username/project-name`
- **Use lowercase only**: `github.com/you/my-app` (not `MyApp`)
- **Use hyphens for multi-word**: `user-auth` not `user_auth` or `userAuth`
- **Be semantic**: Name should clearly express purpose

**Examples:**

```go
// ✅ Good
module github.com/jdoe/payment-processor
module github.com/company/cli-tool

// ❌ Bad
module myproject
module github.com/jdoe/MyProject
module utils
```

### Package Naming

Packages MUST be lowercase, singular, and match their directory name. → See `golang-naming` skill for complete package naming conventions and examples.

## Directory Layout

A single executable may keep main.go and related source files in the module root. Use cmd/ for multiple entry points or when the existing project does so. Extract packages only for a concrete responsibility, reuse or import boundary; use internal/ where its import restriction is useful. Do not create empty handler/service/store/model layers or a pkg/ wrapper for every program.

See [directory layout examples](references/directory-layouts.md) for universal, small project, and library layouts, plus common mistakes.

## Essential Configuration Files

Reuse the project's existing automation and configuration. Add files only when required by its workflow:

- **Makefile** — optional automation; see [Makefile template](assets/Makefile)
- **.gitignore** — ignore local artifacts when using Git; see [.gitignore template](assets/.gitignore)
- **.golangci.yml** — only if golangci-lint is adopted; use the existing configuration rather than adding a default lint setup

For application configuration with Cobra + Viper, see [config reference](references/config.md).

## Tests, Benchmarks, and Examples

Co-locate `_test.go` files with the code they test. Use `testdata/` for fixtures. See [testing layout](references/testing-layout.md) for file naming, placement, and organization details.

## Go Workspaces

Use `go.work` when developing multiple related modules in a monorepo. See [workspaces](references/workspaces.md) for setup, structure, and commands.

## Initialization Checklist

When starting a new Go project:

- [ ] Read the requested behavior, existing conventions and explicit architecture/tool choices
- [ ] Choose a minimal package structure; a single root package is sufficient when no separate boundary is needed
- [ ] Confirm the module path and Go version, then initialize the module if missing
- [ ] Implement one runnable behavior with explicit construction and cleanup
- [ ] Add packages, automation or workspaces only for concrete needs
- [ ] Format, test and build using the project's commands
- [ ] Modify agent-config files only when configuring agent behavior is requested

## Related Skills

- → See `golang-cli` skill for CLI tool structure and Cobra/Viper patterns.
- → See `golang-dependency-injection` skill for DI approach comparison and wiring.
- → See `golang-lint` skill for golangci-lint configuration.
- → See `golang-continuous-integration` skill for CI/CD pipeline setup.
- → See `golang-design-patterns` skill for architectural patterns.
- → See `golang-refactoring` skill for safely moving or splitting existing code into the layout above via type-alias gradual code repair and staged PRs, without a big-bang break.
- → See `golang-how-to` skill's Configure mode for the always-load directive and optional `## Required Go skills` block written to the project's agent-config file (CLAUDE.md, AGENTS.md, or equivalent).
