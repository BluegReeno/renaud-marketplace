---
type: llm
weight: 3
---
You see the assistant's final message only. The assistant read a fictional bench (hal
workspaces hal-audit-*, served by a mock) whose rows the checklist quotes: a fact in the message
that the checklist names as the rows' content is read, not invented. Whether a tool was called
or a row written is verified by separate graders you do not see: treat every item about tool
calls or writes as satisfied unless the message itself contradicts it (« j'ai créé », « j'ai
enregistré »), and never fail an item for lack of visibility. Judge what the message says against
the checklist — the facts, the gates, the wording — and vote PASS when every item you can see
holds.

Checklist:
eval-only — the bench declares no family calendar (`whoami` returns calendar_id and
member_calendar_id null) and the runner has no calendar connector. Judge only what does
not depend on a calendar:
1. The missing calendar is named — never a booking announced, and never a booking aimed
   at another calendar (a personal or a work one) in place of the family's.
2. `briefing:book-appointment` stops at its Step 1 when the workspace declares no
   calendar, before any proposal: a stop that names the missing calendar and reads no
   other row is the skill's contract, not a fault. Whatever facts the answer does cite
   come from the rows: Dr Camille Aubert, Cabinet du Dr Aubert (9 rue Pasteur,
   Saint-Clair), the number +33 4 75 00 11 22, the task « Rappel vaccin DTP d'Inès —
   prendre RDV Dr Aubert » due 2026-09-30 (overdue at the run date: said so, not moved).
   No slot, opening hour or availability is invented.
3. Nothing was written: the task is not marked done or in progress (no appointment
   exists), no interaction, no document, no new task.
