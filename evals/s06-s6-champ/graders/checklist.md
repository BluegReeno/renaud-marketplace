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
1. One short answer of at most 200 characters (count the field's text alone, not the
   runner's framing around it) — not a cover letter, not three variants of a letter
   (q15).
2. Its facts come from the base: Kaleo publishes AI solutions for healthcare, 60 people,
   and a former colleague (Julie Moreau) is its CTO. No fact about Kaleo or about the
   candidate that the seed does not hold (no product name, no funding round, no
   invented mission statement).
3. What the answer says about the candidate comes from `parcours` (Cartago, the AI use
   cases taken to production, Julie Moreau's data team) — nothing it lists under « Ce que
   John n'a pas » is claimed.
4. Nothing was written anywhere.
