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
1. Each S37 is listed with its four tasks and its own in-progress one named (« Brancher le
   planning des chambres sur l'assistant » in pme, « Préparer l'entretien Nexora » in
   jobsearch).
2. Both sprints are past their end date (09-18 and 09-20, today is later) and are flagged
   as such (⚠️ or said in words) — never silently treated as current.
3. No sprint was transitioned or created: no S38, no transition_sprint call.
4. The Family is honestly answered as having no sprints (the flag is off there), not
   given an invented sprint or an empty-but-present one.
