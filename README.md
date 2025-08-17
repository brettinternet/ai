# AI

A collection of AI configuration, tooling MCP servers, and research and prompt testing that can be used as a reference for other projects. This repository demonstrates how to set up an AI development environment and testing with various tools and integrations. See also my [MCP servers](https://github.com/brettinternet/mcp).

## Features

This project is meant to model features that users could implement independently in their own project.

- **Claude Configuration**: [settings](./claude), [hooks](.taskfiles/hooks.yaml), [slash commands](./.claude/commands), and [agents](./.claude/agents)
- **MCP Server Collection**: [MCP servers](./.mcp.json)
- **Docker Support**: Containerized Claude environment with proper user management
- **Task Automation**: [Taskfile](./.taskfiles)-based automation for common operations
- **Notification System**: Pushover integration for task completion notifications
- **Tool Management**: Mise for managing development [tools and dependencies](./mise.toml)
- **Documentation**: [prompts](./docs/prompts.md), [MCP servers](./docs/mcp.md), [agent findings](./docs/claude.md)
- **Prompt tests**: [Promptflow](./promptflow) tests
- **Real-time Whisper transcription**: [transcribe](./transcribe) and preparing to test ffmpeg v8's Whisper integration with [transcribe ffmpeg](./transcribe_ffmpeg/)

## Prerequisites

- [mise](https://mise.jdx.dev/) - tool management
- [Task](https://taskfile.dev/) - task commands

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
docker-compose up -d graphiti neo4j
```

Run all servers.

- [neo4j](https://github.com/neo4j/neo4j) graph database
- [graphiti](https://github.com/getzep/graphiti) knowledge graph MCP
- [promptfoo](https://github.com/promptfoo/promptfoo) prompt tester and security testing

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

- **Permissions**: Controlled access to tools and commands
- **MCP Servers**: Enabled server configurations
- **Hooks**: Notification triggers for events

### MCP Configuration

For user scoped MCPs, add the MCP configurations:

```sh
task mcp:setup-user
```

For project scoped MCPs, the `.mcp.json` file defines:

- **Graphiti**: Knowledge graph for memory context
- **basic-memory**: Context memory between sessions
- **Context7**: Library documentation lookup
- **Sequential Thinking**: Complex reasoning capabilities
- **Playwright**: Browser automation
- **Git**: Version control integration
- **Filesystem**: File operations
- **Fetch**: Web content retrieval

## Docker Configuration

The `Dockerfile.claude` provides:

- Debian-based container
- Claude user with sudo access
- Pre-installed development tools and additional dependencies with `mise`
- Volume mounting for configuration persistence

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
