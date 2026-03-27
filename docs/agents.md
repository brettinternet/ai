# Agents

Tips: https://mitchellh.com/writing/my-ai-adoption-journey

## Work efficiently

### Use worktrees

Here are my simple functions to create and clean up git worktrees: https://github.com/brettinternet/dotfiles/blob/719e59211d997757aedcdf9a0bfe569df2e7414c/darwin/.functions/shortcuts.sh#L29-L81

### Turn off notifications

In Claude Code, run `/notifications off` or add to your settings:

```json
// ~/.claude/settings.json
{
  "notifications": false
}
```

Don't let the agent interrupt you, you should interrupt the agent, or revisit the agent in natural breaks from your work.
