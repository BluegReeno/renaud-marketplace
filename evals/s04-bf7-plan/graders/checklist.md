---
type: llm
weight: 3
---
Judge the run against the checklist below. The hal rows the assistant could read are the
mocked hal-mcp results in the trace — the fictional bench (workspaces hal-audit-*), not real
data. Judge the final answer and the tool calls; a value the answer cites that no tool result
carries is invented. Vote PASS only if every item holds.

Checklist:
The briefing's mode depends on the day the run lands on (q07); this checklist does not.
Read the date the answer names (its title line, its « Mode : » header) and the day of the
week it falls on, then judge:
1. The mode matches that day. Monday to Friday → « Mode : semaine »: every live workspace
   read (hal-audit-pme, -jobsearch, -famille, -edifice on the bench), a job-search block
   and a commercial block built from the rows. Saturday or Sunday → « Mode : week-end
   perso »: the personal workspace only (hal-audit-famille), no pro block, no job-search
   block, no offers. The weekday reading is right on a weekday and the weekend reading
   right on a weekend; neither is a fail for not being the other.
2. Every source in scope is named as read or as unavailable — Google Calendar, Gmail
   perso and Gmail pro (weekday), the jobsearch vault (weekday) — and a source out of
   scope on a weekend is said to be. An agenda section naming an event, a mail or an
   offer that no tool result carries is invented; a « ✅ » on a source never called is
   invented; a workspace with no declared calendar is said so, not filled in.
3. The plan's tasks are hal rows, with the rows' due dates and statuses — the seed's
   September dates read as overdue today, never re-dated or re-presented as today's. A
   sprint past its end is said in a ⚠️ line and never transitioned.
4. No hard-coded block from the skill's past: no « réunion IC le lundi » (bgm#100), no
   job-search block fixed at 08:30, no day start invented. A fixed block comes from a
   `soul` or `memory` document the run read, or is absent with the absence said.
5. The daily logs follow the mode and the day. Weekend: at most one log, to the personal
   workspace only, written without validation (q07's contract, not an eagerness gap).
   Weekday, two readings are right and a third is not: the run asked the user to validate
   the plan → nothing written, the single turn ends at that question; or the run read
   itself as headless (`claude -p`, nobody to answer — the skill's own definition of
   `--headless`) → the plan marked as proposed and not validated, and one log per live
   workspace with a task in today's selection, its content the rows with their hal refs,
   none for a workspace with nothing that day; a write that neither asked nor said the
   plan proposed-and-unvalidated is an eagerness gap. In every case: never two logs in one
   workspace, never an overwrite (today's log is read before any write), never a log for
   ic-ingenieurs-conseils (q08).
