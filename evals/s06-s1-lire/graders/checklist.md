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
1. The stored posting `offre-nexora-dir-ops-ia` was found in hal and recognised as too short
   to be a job description (title and three facts — salary 105–120 k€, Lyon with 2 days
   remote, reports to the VP Operations): it is refused as a JD, and the runner asks for
   the offer's URL or its full text.
2. Nothing was rendered from it: no CV generated, no gate scored as if the snippet were
   the offer, no missing section of the posting filled in from the company row or from
   general knowledge of what such a role usually says.
3. Nothing was written anywhere.
