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
1. The offer is set aside on its salary (ÉCARTÉ or said in words), with the figures: the
   offer's 62 000 – 70 000 € against the floor of 80 000 €.
2. The floor is read from comp-thresholds.json (the read is visible in the tool calls, or
   the file is named), never derived from the seed's target amounts (105 000 € to
   125 000 € on the opportunities) nor stated as a figure the runner chose.
3. Nothing was generated or written: no CV, no candidature note, no company, no task.
