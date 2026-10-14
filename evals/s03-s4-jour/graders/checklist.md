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
eval-only — the day is not the seed's Monday 2026-09-14. Judge only what is
clock-independent:
1. No family calendar is reachable on the bench: the absence is named, and no event is
   invented. The seed's judo of Monday 2026-09-14 is never presented as today's. A judo
   slot cited from the club's row (« Léo, mardi et vendredi 17h30 ») is correct when
   today is a Tuesday or a Friday, and when it is said to come from that note.
2. The tasks cited are hal-audit-famille's, with their due dates as the rows carry them;
   « Envoyer le certificat de scolarité de Léo au club de judo » (high, due 2026-09-15) is
   said overdue, not « tomorrow ». A personal task of another workspace (« Cadeau
   d'anniversaire de Sofia », hal-audit-jobsearch) is never presented as a family row.
3. Nothing is closed or moved; a daily log, if one is written, lands in hal-audit-famille
   only, once.
