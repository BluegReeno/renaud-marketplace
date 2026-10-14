---
type: llm
weight: 3
---
Judge the run against the checklist below. The hal rows the assistant could read are the
mocked hal-mcp results in the trace — the fictional bench (workspaces hal-audit-*), not real
data. Judge the final answer and the tool calls; a value the answer cites that no tool result
carries is invented. Vote PASS only if every item holds.

Checklist:
1. The stored posting `offre-nexora-dir-ops-ia` was found in hal and recognised as too short
   to be a job description (title and three facts — salary 105–120 k€, Lyon with 2 days
   remote, reports to the VP Operations): it is refused as a JD, and the runner asks for
   the offer's URL or its full text.
2. Nothing was rendered from it: no CV generated, no gate scored as if the snippet were
   the offer, no missing section of the posting filled in from the company row or from
   general knowledge of what such a role usually says.
3. Nothing was written anywhere.
