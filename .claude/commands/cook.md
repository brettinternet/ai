Time to cook!

1. Open @todo.md or find "TODO:" tasks in the repository and identify any steps not marked as completed.
1. Find the first phase with unfinished tasks. Give an agent a copy of that
   phase's prompt that is focused only the incomplete tasks. The agent should
   be told to go through each task and complete the following:
   - Double-check if that task is truly unfinished (if uncertain, ask for clarification).
   - If they confirm it's already done, they can skip it.
   - They should make sure that the tests pass, and the program builds/runs.
   - Have them commit the changes to your repository with a clear commit message.
   - Report back that they've fully completed the task.
1. Update the TODO item to mark the tasks that the agent completed.
1. After you finish the phase, pause and wait for user review or feedback.
1. Auto-compact the context, then repeat with the next unfinished phase as directed by the user.

If provided, the agent you'll use is:
