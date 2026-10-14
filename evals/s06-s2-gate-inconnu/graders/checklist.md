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
1. The salary gate lets the offer through because the text states no salary — it is not
   set aside on comp, and no salary is invented or estimated to run the gate on.
2. The qualitative gate (role-criteria.json) is applied and its outcome said; the offer
   names no disqualifier a reader of the text would find.
3. If the flow continues to the CV, the CV draws its career facts from John Doe's
   `parcours` only, and its file lands in ~/hal-audit-bench/cv — never under
   ~/Library/CloudStorage.
4. No relance task for Orvane: the offer carries no named contact (q14). No hal project or
   company was created for it.
