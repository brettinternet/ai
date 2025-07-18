# AI Tools Collection

An incomprehensive collection of Claude AI and MCP tools configuration that can be used as a reference for other projects. This repository demonstrates how to set up an AI development environment with various tools and integrations.

## Features

This project is meant to model features that users could implement independently in their own project.

-   **Claude AI Integration**: Claude Code configuration with permissions and hooks
-   **MCP Server Collection**: Multiple MCP servers including:
    -   Context7 for library documentation
    -   Sequential thinking for complex reasoning
    -   Playwright for browser automation
    -   Git integration for version control
    -   Filesystem operations
    -   Web fetch capabilities
-   **Docker Support**: Containerized Claude environment with proper user management
-   **Task Automation**: Taskfile-based automation for common operations
-   **Notification System**: Pushover integration for task completion notifications
-   **Tool Management**: Mise for managing development tools and dependencies

## Prerequisites

-   [mise](https://mise.jdx.dev/) - tool management
-   [Task](https://taskfile.dev/) - commands
-   [Claude Code](https://claude.ai/code) - AI agent

## Usage

Setup project dependencies and generate `.env`

```sh
task init
```

Setup user MCPs

```sh
task mcp:setup-user
```

Run the Graphiti and Neo4j containers for local MCP server.

```sh
docker-compose up -d
```

Claude has access to tooling installed with `mise` since it inherits the user's shell. Run an executable in "bash mode" by prefixing the Claude input with `!`, which represents the available shell Claude has when running tools. What Claude calls "Bash" it actually means whatever shell you're running since `! echo $SHELL` outputs `/bin/zsh` in my environment.

### Prompts

1. Ask Claude to summarize your work from yesterday. Claude then runs `task github:myactivity` or `task github:myactivity DAY=fri` to pull GitHub activity and summarize the work.

### Running Claude AI

**Local execution**:

```sh
task ai
```

**Docker execution**:

```sh
task ai:docker
```

## Configuration

### Claude Settings

The `.claude/settings.json` file contains:

-   **Permissions**: Controlled access to tools and commands
-   **MCP Servers**: Enabled server configurations
-   **Hooks**: Notification triggers for events

### MCP Configuration

For user scoped MCPs, add the MCP configurations:

```sh
task mcp:setup-user
```

For project scoped MCPs, the `.mcp.json` file defines:

-   **Context7**: Library documentation lookup
-   **Sequential Thinking**: Complex reasoning capabilities
-   **Playwright**: Browser automation
-   **Git**: Version control integration
-   **Filesystem**: File operations
-   **Fetch**: Web content retrieval

## Docker Configuration

The `Dockerfile.claude` provides:

-   Debian-based container
-   Claude user with sudo access
-   Pre-installed development tools and additional dependencies with `mise`
-   Volume mounting for configuration persistence

## Customization

### Adding New MCP Servers

1. Add server configuration to `.mcp.json`
1. Enable server in `.claude/settings.json` or `.claude/settings.local.json`

### Custom Notifications

1. Configure Pushover credentials in `.env`
1. Customize hooks in `.claude/settings.json` or `.claude/settings.local.json`
1. Add new notification tasks in `.taskfiles/hooks.yaml`

### Tool Integration

1. Add tools to `mise.toml`
1. Create tasks in `Taskfile.dist.yaml`
1. Update permissions in `.claude/settings.json` or `.claude/settings.local.json`
