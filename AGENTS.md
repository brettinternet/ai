# AGENTS.md

## Overview

This repository is an AI development environment and tools collection demonstrating Claude AI integration with various MCP servers. It provides a containerized development environment with automation, notifications, and GitHub integration tools.

## Setup

This project uses `mise` for dependencies. Claude's shell environment may not inherit access to executables installed with this method, so it may be required to run executables with `mise exec`. E.g. to run a `gh` command use `mise exec gh -- gh`.

## Core Commands

### Setup and Development

```bash
task init                  # Install dependencies and setup environment
task ai                    # Start Claude AI locally
task ai:docker             # Start Claude AI in Docker container
task -l                    # List all available tasks
```

## Architecture

### Task Automation System

The project uses Taskfile with modular organization:

- `Taskfile.dist.yaml` - Main task definitions and Docker commands
- `.taskfiles/setup.yaml` - Environment setup and mise installation
- `.taskfiles/scripts.yaml` - GitHub activity analysis scripts
- `.taskfiles/hooks.yaml` - Notification system integration
- `.taskfiles/mcp.yaml` - MCP server utilities

## Tools

### GitHub

- Always use `gh` CLI for all GitHub operations. Never construct raw API calls.
- For PRs: `gh pr view`, `gh pr diff`, `gh pr comment`
- For issues: `gh issue list`, `gh issue view`
- Never open GitHub browser URLs; use CLI output only

### Linear

- Use `linear` CLI or the Linear MCP server if available
- For issue lookup: query by branch name pattern (e.g. `ABC-123-...`)

### URLs

- For docs lookups, use `curl` + parse or use the web_fetch capability if available
- For GitHub-specific lookups, always prefer `gh` over browser
- For npm/pkg research: `npm info [package]` or `curl https://registry.npmjs.org/[package]`

### Worktrees

Put worktrees in @.trees if you decide to create one.

## What NOT to do

- Don't run `git push` without explicit instruction
- Don't open PRs without explicit instruction
- Don't edit files outside the current task scope
