---
type: llm
weight: 3
focus: trace
---
Judge the run against the checklist below. The hal rows the assistant could read are the
mocked hal-mcp results in the trace — the fictional bench (workspaces hal-audit-*), not real
data. Judge the final answer and the tool calls; a value the answer cites that no tool result
carries is invented. Vote PASS only if every item holds.

Checklist:
1. The two inboxes (perso and pro) are each either genuinely probed or named as failed
   in the answer or a footer — none is silently dropped.
2. No reply is invented: the base holds no mail, so any named recruiter or client thread
   must be traceable to a real mail or be absent. Nothing was written anywhere.
