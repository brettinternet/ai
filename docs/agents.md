# Agents

Tips: https://mitchellh.com/writing/my-ai-adoption-journey

## Work efficiently

### Use worktrees

Here are my simple functions to create and clean up git worktrees: https://github.com/brettinternet/dotfiles/blob/a43ba3d6c42acfd657dfaf2064d5820fb8757364/darwin/.functions/dev.sh#L24-L118

### Turn off notifications

In Claude Code, run `/notifications off` or add to your settings:

```json
// ~/.claude/settings.json
{
    "notifications": false
}
```

Don't let the agent interrupt you, you should interrupt the agent, or revisit the agent in natural breaks from your work.
