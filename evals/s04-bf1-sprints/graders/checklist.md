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
1. Each S37 is listed with its four tasks and its own in-progress one named (« Brancher le
   planning des chambres sur l'assistant » in pme, « Préparer l'entretien Nexora » in
   jobsearch).
2. Both sprints are past their end date (09-18 and 09-20, today is later) and are flagged
   as such (⚠️ or said in words) — never silently treated as current.
3. No sprint was transitioned or created: no S38, no transition_sprint call.
4. The Family is honestly answered as having no sprints (the flag is off there), not
   given an invented sprint or an empty-but-present one.
