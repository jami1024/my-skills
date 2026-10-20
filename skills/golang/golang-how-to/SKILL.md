---
name: golang-how-to
description: "Route Go tasks to the smallest relevant skill set. Use before Go coding, review or debugging; include golang-best-practices only for new services, cross-layer work or architecture review."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code, Codex or similar harness. Requires git.
metadata:
  author: samber
  version: "1.4.2"
  openclaw:
    emoji: "🧭"
    homepage: https://github.com/samber/cc-skills-golang
    requires:
      bins:
        - git
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(git:*) Agent AskUserQuestion LSP Bash(gopls:*) mcp__gopls__*
---

**Persona:** Route Go tasks to the smallest useful set of skills. Read the task and existing project conventions before choosing guidance. Do not load skills merely because they are adjacent topics.

**Modes:**

- **Orchestrate** — choose one primary skill, then add secondary skills only for concrete needs uncovered by the task or code.
- **Disambiguate** — when two skills seem to overlap, show the boundary table. See [disambiguation.md](references/disambiguation.md).
- **Configure** — write the always-load directive for `golang-how-to` itself, plus an optional `## Required Go skills` block, to the project's agent-config file (CLAUDE.md, AGENTS.md, or equivalent). Follow [project-config.md](references/project-config.md).

**Questions:** In Configure mode, reuse the requested targets and skill set. Ask only about unresolved choices that affect the write; use an available question tool or concise prose. A complete configuration request needs no extra approval round.

**Tooling:** Routing requires no extra tools. Use the harness's existing code intelligence when available. Load `golang-gopls` only for Go semantic navigation or refactoring; if a tool is missing, explain the limitation instead of automatically installing an unpinned version.

## Skill loading

1. User requirements and existing project conventions take precedence over community defaults. Directory names, test organization and implementation order are preferences, not reasons to restructure an existing project.
2. Before consulting the topic table, classify whether the task crosses handler/service/store or changes service architecture. If it does, and local `golang-best-practices` is registered, read and finish that blueprint first in a separate read call; do not batch it with topic reads. Then select only the remaining topic guidance needed for the work. For a single-topic task such as naming, error handling, concurrency, tests or profiling, go directly to that topic without loading the project blueprint.
3. Start with one primary skill and zero to two secondary skills that the task actually needs. The table's **Also load** column lists candidates, not an unconditional bundle. Load further guidance later only when a new requirement or finding justifies it; do not reread already loaded skills.
4. Library-specific skills apply when that library is in the project or explicitly requested. Do not add a dependency to make a skill applicable. Run the project's existing checks without loading a separate testing skill unless test design is part of the work.
5. If `golang-best-practices` or a requested topic is not registered, use available project guidance and report the missing resource. Do not claim to have loaded it or require installation to proceed.

| Intent | Primary | Also load |
| --- | --- | --- |
| Design an API, choose a pattern | `golang-design-patterns` | `golang-structs-interfaces`, `golang-naming` |
| Name a type, function, or package | `golang-naming` | `golang-code-style` |
| Handle errors idiomatically | `golang-error-handling` | `golang-safety` (nil-heavy code) |
| Write goroutines, channels, sync | `golang-concurrency` | `golang-context` (if cancellation) |
| Pass deadlines / cancel operations | `golang-context` | `golang-concurrency` (if goroutines) |
| Design structs, embed, use interfaces | `golang-structs-interfaces` | `golang-design-patterns` |
| Database queries and transactions | For cross-layer store/biz changes, read local `golang-best-practices` first when registered, then `golang-database`; otherwise `golang-database` | `golang-error-handling` for error translation; `golang-context` for cancellation behavior |
| Build a gRPC service | `golang-grpc` | `golang-testing`, `golang-error-handling` |
| Build a GraphQL API | `golang-graphql` | `golang-testing`, `golang-error-handling` |
| Build a CLI command tree | `golang-spf13-cobra` | `golang-cli`, `golang-spf13-viper` (if config) |
| Layer config from flags/env/file | `golang-spf13-viper` | `golang-spf13-cobra` |
| Write tests | `golang-testing` | `golang-stretchr-testify` (if using testify) |
| Apply optimization patterns | `golang-performance` | `golang-benchmark` (measure first) |
| Measure with pprof / benchstat | `golang-benchmark` | `golang-performance` (fix), `golang-troubleshooting` (root cause) |
| Debug a panic or unexpected behavior | `golang-troubleshooting` | `golang-safety`, `golang-benchmark` (if perf-related) |
| Monitor in production | `golang-observability` | `golang-performance` (if SLO breach) |
| Audit security vulnerabilities | `golang-security` | `golang-safety`, `golang-lint` |
| Review formatting and style | `golang-code-style` | `golang-naming`, `golang-lint` |
| Refactor or restructure existing code | `golang-refactoring` | `golang-naming`, `golang-code-style`, `golang-project-layout` |
| Configure golangci-lint | `golang-lint` | `golang-code-style` |
| Write godoc / README / CHANGELOG | `golang-documentation` | `golang-naming` |
| Set up a new service or change cross-layer architecture | local `golang-best-practices` when registered; otherwise `golang-project-layout` | `golang-project-layout` for layout details; DI or lint only if requested |
| Organize a standalone library, CLI module, or Go workspace | `golang-project-layout` | `golang-design-patterns` only for a concrete design question |
| Set up CI/CD pipeline | `golang-continuous-integration` | `golang-lint`, `golang-security` |
| Choose a library | `golang-popular-libraries` | relevant library-specific skill |
| Look up a package's docs, versions, importers, or CVEs | `golang-pkg-go-dev` | `golang-dependency-management` |
| Navigate, diagnose, or refactor local code (definitions, references, rename) | `golang-gopls` | — |
| Adopt new Go language features | `golang-modernize` | `golang-lint` |
| Use samber/lo (slice/map helpers) | `golang-samber-lo` | `golang-data-structures`, `golang-performance` |
| Use samber/oops (structured errors) | `golang-samber-oops` | `golang-error-handling` |
| Use log/slog | `golang-samber-slog` | `golang-observability`, `golang-error-handling` |
| Use dependency injection | `golang-dependency-injection` | `golang-google-wire` or `golang-uber-dig` or `golang-uber-fx` or `golang-samber-do` |

Load skills by their names and paths in the current harness's inventory. `samber/cc-skills-golang@<name>` identifies upstream provenance; this local collection registers bare names such as `golang-testing`. `golang-best-practices` is an optional local skill, not part of the upstream catalog.

## Tool and boundary guidance

Use existing harness tools first; routing does not require installation. Load the owning topic only when its details are needed:

| Need | Guidance |
| --- | --- |
| Local definitions, references, diagnostics or refactoring | `golang-gopls` |
| Published package docs, versions, importers or licenses | `golang-pkg-go-dev` |
| Whole-module reachable vulnerability audit | `golang-security` |
| Non-Go documentation | Official documentation or an available documentation tool |

Read [disambiguation.md](references/disambiguation.md) only for overlapping intents; read [by-category.md](references/by-category.md) only to browse the full catalog. Do not preload both references for an already clear task.

## Configure mode

Write an always-load directive for `golang-how-to` itself to the project's agent-config file (CLAUDE.md, AGENTS.md, GEMINI.md, Cursor rules, or Copilot instructions — whichever the project's harness reads), and optionally force-trigger specific secondary skills too.

Modify agent-config files only when the user requests agent configuration, such as `/golang-how-to configure`. Creating a Go project alone does not authorize persistent skill-loading rules. Reuse the requested targets and skill set without asking again; ask only about unresolved choices that affect the write. Follow [project-config.md](references/project-config.md).

---

This skill is not exhaustive. Refer to individual skill files and the official Go documentation for detailed guidance.

If you encounter a bug or unexpected behavior in this skill plugin, open an issue at <https://github.com/samber/cc-skills-golang/issues>.
