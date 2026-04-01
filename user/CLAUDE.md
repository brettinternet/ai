# User Preferences

## Communication Style

- Be terse and direct. Skip preamble, filler phrases, and trailing summaries.
- Lead with the answer or action, not the reasoning.
- Use plain text over bullet lists when a sentence suffices.

## Tools

- Use `gh` CLI for all GitHub operations. Never construct raw API calls or open browser URLs.
- Use `mise exec <tool> -- <cmd>` when a tool is installed via mise and may not be in PATH.
- Use `chrome-devtools` tool to verify browser changes when working with web UI.

## Git

- Never run `git push` without explicit instruction.
- Never open PRs without explicit instruction.
- When committing, do not add Claude as a co-author. Omit any `Co-Authored-By` trailer.
