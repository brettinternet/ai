# CLAUDE.md

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

### GitHub Activity Analysis

Use this script to determine what was accomplished on the previous working day.

```bash
# Get recent GitHub activity for standup reports
task github:myactivity DAY=thu REPOS=org/repo1,org/repo2
GITHUB_REPOS=org/repo task github:activity DAY=friday
task github:myactivity REPOS=org/repo                      # Defaults to last workday
GITHUB_ORG=org task github:activity                        # all repos
```

**Standup Summary Instructions:**
When the user asks for their standup summary, summary of yesterday's work, or what they accomplished, automatically run the GitHub activity script `task github:myactivity` and provide a concise summary formatted for standup meetings. To get a summary for another user, find the user on GitHub and put the username as an argument to `task github:activity -- `.

The summary should be:

- **Brief and accessible**: 2-5 bullet points maximum
- **Focus on outcomes**: What was accomplished, not technical details
- **Standup-friendly**: Easy to recite in a team meeting
- **Consolidate**: Combine related actions such as a commit, push and PR for the same related work
- **Action-oriented**: Use active language describing completed work
- **Specific and linked**: Include specific PR numbers, commit references, and GitHub links for easy access
- **Avoid vague statements**: Replace generic phrases like "reviewed multiple PRs" with specific PR numbers and links

Format example:
- Enhanced device simulation with function generation feature in [PR #1234](https://github.com/org/repo/pull/1234)
- Improved development environment configuration with [commit abc1234](https://github.com/org/repo/commit/abc1234567890)
- Reviewed and approved [PR #5678](https://github.com/org/repo/pull/5678) for authentication improvements

**Important**: Always include GitHub links for PRs, commits, and other relevant items. Never use vague descriptions like "reviewed multiple PRs" - instead specify which PRs were reviewed with their numbers and links.

Write the result of this summary to a new file in this repository under a `/tmp` directory.

### Notifications

```bash
task hooks:pushover:test   # Test Pushover notifications
task hooks:sound           # Play system sound
```

### Docker

```bash
task docker:build         # Build Claude container image
task docker:run            # Run Claude container
```

## Architecture

### Task Automation System

The project uses Taskfile with modular organization:
- `Taskfile.dist.yaml` - Main task definitions and Docker commands
- `.taskfiles/setup.yaml` - Environment setup and mise installation
- `.taskfiles/scripts.yaml` - GitHub activity analysis scripts
- `.taskfiles/hooks.yaml` - Notification system integration
- `.taskfiles/mcp.yaml` - MCP server utilities

### MCP Server Configuration

Located in `.mcp.json`, provides access to:
- **Context7**: Library documentation lookup via `@upstash/context7-mcp`
- **Sequential Thinking**: Complex reasoning via `@modelcontextprotocol/server-sequential-thinking`
- **Playwright**: Browser automation via `@playwright/mcp`
- **Serena**: IDE assistant via `git+https://github.com/oraios/serena`
- **Git**: Version control integration via `mcp-server-git`
- **Filesystem**: File operations via `@modelcontextprotocol/server-filesystem`
- **Fetch**: Web content retrieval via `mcp-server-fetch`

### Claude Configuration

Claude settings in `.claude/settings.json` define:
- **Permissions**: Controlled access to bash commands, Docker, web fetching, and MCP servers
- **Hooks**: Automated Pushover notifications and sound alerts on task completion/stop events
- **Enabled Servers**: All MCP servers are enabled by default

### Environment Configuration

Environment variables in `.env` (copied from `example.env`):
- `GITHUB_ORG`: GitHub organization for activity analysis
- `PUSHOVER_TOKEN`: Pushover API token for notifications
- `PUSHOVER_USER`: Pushover user key for notifications

### Tool Management

Uses `mise.toml` for development tool installation:
- Node.js ecosystem (bun, node LTS)
- GitHub CLI and JSON processing (gh, jq)
- Task runner and AI tools (task, claude-code, ccusage)
- Python environment (uv for package management)

### GitHub Activity Analysis

The `scripts/github-activity.sh` script provides detailed GitHub event analysis:
- Timezone-aware date filtering (handles UTC vs local time)
- Commit message deduplication (identifies force pushes)
- User-specific filtering with flexible author matching
- Support for single or multiple repository analysis
- Detailed event information including commit messages, PR descriptions, and branch operations

### Docker Environment

`Dockerfile.claude` creates a development container with:
- Debian-based environment with Claude user
- Volume mounting for configuration persistence
- User ID mapping for file permission consistency
- Pre-installed development tools via mise

## Key Development Patterns

### Adding New Scripts

1. Create script in `scripts/` directory
2. Add task definition in `.taskfiles/scripts.yaml`
3. Update permissions in `.claude/settings.json` if needed

### MCP Server Integration

1. Add server configuration to `.mcp.json`
2. Enable server in `.claude/settings.json` `enabledMcpjsonServers`
3. Add any required permissions to `permissions.allow`

### Notification Customization

1. Configure credentials in `.env`
2. Modify hook triggers in `.claude/settings.json`
3. Create custom notification tasks in `.taskfiles/hooks.yaml`

### Environment Variables

The project requires `GITHUB_ORG` environment variable for GitHub integration. Set this in `.env` file for the GitHub activity analysis to function properly.
