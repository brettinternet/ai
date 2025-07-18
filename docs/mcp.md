# MCP

https://docs.anthropic.com/en/docs/claude-code/mcp

## User

```sh
task mcp:setup-user
```

## Project

`.mcp.json`

```jsonc
{
  "mcpServers": {
    "graphiti": { // use instead of basic-memory
      "type": "sse",
      "url": "http://localhost:8000/sse"
    },
    "basic-memory": {
      "command": "uvx",
      "args": [
        "basic-memory",
        "mcp"
      ]
    },
    "context7": {
      "command": "bunx",
      "args": ["@upstash/context7-mcp"]
    },
    "sequential-thinking": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/arben-adm/mcp-sequential-thinking",
        "--with",
        "portalocker",
        "mcp-sequential-thinking"
      ]
    },
    "playwright": {
      "command": "bunx",
      "args": ["@playwright/mcp"]
    },
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena-mcp-server",
        "--enable-web-dashboard",
        "false",
        "--enable-gui-log-window",
        "false",
        "--context",
        "ide-assistant"
      ]
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."]
    },
    "filesystem": {
      "command": "bunx",
      "args": ["@modelcontextprotocol/server-filesystem", "."]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```
