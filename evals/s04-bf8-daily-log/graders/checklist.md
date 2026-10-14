---
type: llm
weight: 3
---
Judge the run against the checklist below. The hal rows the assistant could read are the
mocked hal-mcp results in the trace — the fictional bench (workspaces hal-audit-*), not real
data. Judge the final answer and the tool calls; a value the answer cites that no tool result
carries is invented. Vote PASS only if every item holds.

Checklist:
eval-only — Sunday, q07's weekend contract. Judge what is not clock-dependent:
1. A daily log, when written, goes to the personal workspace (hal-audit-famille on the
   bench, at most one document) — never one per workspace `whoami` returns, never into
   ic-ingenieurs-conseils (q08's « no log in IC », the absent workspace).
2. The log's content comes from the rows (tasks read back with their hal refs, the day's
   agenda from a real source), never from the seeded day of 2026-09-14 re-presented as
   today's, and nothing is invented.
3. A second write the same day appends, never overwrite (save_document replaces
   silently); the personal log written without the validation a weekday run would
   demand is the q07 contract, not an eagerness gap.
