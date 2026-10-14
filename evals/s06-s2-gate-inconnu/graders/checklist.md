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
1. The salary gate lets the offer through because the text states no salary — it is not
   set aside on comp, and no salary is invented or estimated to run the gate on.
2. The qualitative gate (role-criteria.json) is applied and its outcome said; the offer
   names no disqualifier a reader of the text would find.
3. If the flow continues to the CV, the CV draws its career facts from John Doe's
   `parcours` only, and its file lands in ~/hal-audit-bench/cv — never under
   ~/Library/CloudStorage.
4. No relance task for Orvane: the offer carries no named contact (q14). No hal project or
   company was created for it.
