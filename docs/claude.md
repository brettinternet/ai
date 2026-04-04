# Claude

## Auth

- https://code.claude.com/docs/en/authentication#credential-management

## Context

Inject additional context from outside CLAUDE.md with:

```sh
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir /path/to/another-project
```

Or you can add this to `CLAUDE.md`:

```md
@~/.claude/my-project-instructions.md
```

Use rules specific to directories: https://code.claude.com/docs/en/memory#organize-rules-with-claude/rules/

## Worktrees

Add `.trees` to `.gitignore`.

```bash
wt-new() {
  local branch=$1
  git worktree add -b "$branch" ".trees/$branch" main
  tmux new-window -n "$branch" -c "$(pwd)/.trees/$branch"
  tmux send-keys "claude" Enter
}
```
