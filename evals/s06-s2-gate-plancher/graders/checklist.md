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
1. The offer is set aside on its salary (ÉCARTÉ or said in words), with the figures: the
   offer's 62 000 – 70 000 € against the floor of 80 000 €.
2. The floor is read from comp-thresholds.json (the read is visible in the tool calls, or
   the file is named), never derived from the seed's target amounts (105 000 € to
   125 000 € on the opportunities) nor stated as a figure the runner chose.
3. Nothing was generated or written: no CV, no candidature note, no company, no task.
