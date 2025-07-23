# Claude

## Hooks

While I've had issues in the past with commands installed in a local repo with `mise`, this appears to be fixed recently and does require a hook such as this:

```json
    "PreToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "eval \"$(mise activate zsh)\""
          }
        ]
      }
    ],
```
