# Workflow

1. Build up the context for what you're working on, this is the rewind checkpoint
2. Perform a task, but at a stopping point you should rewind (double escape) the context checkpoint
   - You can do this with multiple chats (for Claude Code, run `/resume` and select the context checkpoint)
3. Describe to the agent that your developer finished the task and to [provide feedback](../.claude/commands/feedback.md)

> [!NOTE]
> It appears that LLMs can provide more honest with feedback to a third party (e.g. "my developer")
