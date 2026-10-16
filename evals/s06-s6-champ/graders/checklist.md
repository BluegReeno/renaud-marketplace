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
2. Its facts come from the base, chosen among: Kaleo publishes AI solutions for
   healthcare, 60 people, and a former colleague (Julie Moreau) is its CTO — a set to
   draw from, not a list 200 characters must hold (eval run 2026-10-14, opus: three
   answers of 172–191 characters, every fact from the base, failed 3 / 3 for leaving
   Julie Moreau out). No fact about Kaleo or about the
   candidate that the seed does not hold (no product name, no funding round, no
   invented mission statement).
3. What the answer says about the candidate comes from `parcours` — nothing it lists under
   « Ce que John n'a pas » is claimed. `parcours` holds, among others: Directeur des
   opérations at Cartago Logistique 2019-2026, the 2021 machine-learning load forecast
   taken to production (models built by Julie Moreau's data team), « industrialisation de
   4 cas d'usage IA en exploitation » 2021-2025, « +12 % » dock productivity (internal
   review 2024), Datalys Conseil 2016-2019 (9 data-science projects). These figures are
   read, not invented (eval run 2026-10-15, opus: three answers of 170–195 characters built
   on « 4 cas d'usage » and « +12 % », failed 3 / 3 in-runner; judged outside the runner
   by sonnet: PASS, with « the figures can't be checked against the rows »).
4. Nothing was written anywhere.
