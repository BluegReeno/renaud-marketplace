---
name: offer-to-cv
description: >
  Turn one job offer into one judged CV and one logged application, inline in the
  caller's context. Takes `JOB_URL` alone — it resolves the job description itself
  through read-job-offer — or a pre-fetched `JD_TEXT`. Checks compensation against
  the floor in jobsearch/data/comp-thresholds.json (rejects only on an explicit
  figure below it), checks the JD against the qualitative disqualifiers in
  jobsearch/data/role-criteria.json (rejects only on a clear content match),
  generates the 1-page PDF CV via cv-generator, spawns the cv-judge agent itself
  (Tour 1, corrections, Tour 2) and logs the application via log-application with
  status "📝 À postuler". A CV is never logged without a judge score. With
  `MODE: gates-only` it runs the two gates and stops on a PASSE or ÉCARTÉ line,
  writing nothing. Two callers: morning-briefing invokes it over the morning's 🔥
  offers, one after the other; apply-to-offer invokes it on a pasted URL or text.
  It replaced the cv-log-worker agent on 2026-10-21: a sub-agent the runtime
  launched in the background had no Agent tool and skipped the judge, so the CV
  went out « ⚠️ CV non jugé » (renaud#176). Never auto-applies, never sends
  messages, never generates cover letters.
allowed-tools: "Bash WebFetch Skill(read-job-offer) Skill(cv-generator) Skill(log-application) Agent(cv-judge)"
---

# Offer To CV — Skill Instructions

You handle exactly **one** job offer, inline, in the context of whoever invoked you. Resolve the
offer, run the comp gate, run the qualitative role gate, generate the CV, have it judged twice,
log the application. Nothing else.

This is a **skill, not a sub-agent**, on purpose. On 2026-10-21 the previous design — a
`cv-log-worker` agent spawned by the caller — was launched asynchronously by the runtime; a
background sub-agent has no `Agent` tool at any depth, so it could not spawn the judge and logged
the CV unjudged. Running inline, you always have the caller's `Agent` tool, and the judge runs
every time (renaud#176 §2). The cost is accepted: `morning-briefing` processes its 🔥 offers one
after the other.

Two callers invoke you, and you behave identically for both:

- `morning-briefing` (Step 2c.4) — one of the morning's 🔥 offers, usually with `JD_TEXT` and
  `SENDER_EMAIL` already in hand.
- `apply-to-offer` — an offer Renaud pasted during the day: a `JOB_URL`, or the offer's text as
  `JD_TEXT` with no URL, and a `MODE`.

## Inputs

The caller passes these fields (one per line, `KEY: value` format).

**Required:**

- `DATE` — today's date in `YYYY-MM-DD` format (Europe/Paris)
- `JOB_URL` or `JD_TEXT`, at least one:
  - `JOB_URL` — LinkedIn job URL (`https://www.linkedin.com/jobs/view/<job_id>`) or a bare `job_id`
  - `JD_TEXT` — full job description text, when the caller already has it (fetched, or pasted by
    Renaud with no link)

**Optional** — each has a defined behaviour when absent, see Step 0:

- `MODE` — `full` (default) or `gates-only`. `gates-only` runs Step 0, A.5 and A.6 and stops
  there with a `PASSE` or `ÉCARTÉ` line: no CV, no judge, no log, nothing written (Step A.7)
- `JOB_TITLE` — job title, when the caller already has it
- `COMPANY` — company name, when the caller already has it
- `SENDER_EMAIL` — address that sent the digest. Absent ⇒ `source` is `manual` (Step A)
- `OUTPUT_DIR` — where the PDF goes. Absent ⇒ the Drive folder named in Step B. A replay or a
  test passes a scratch folder here, and then **Step C is skipped**: a CV rendered outside the
  Drive is not a candidature, and nothing is logged for it.

If `JOB_URL` is empty **and** `JD_TEXT` is empty, you cannot do anything useful: return the
`ÉCHEC` line immediately with reason `no JOB_URL and no JD_TEXT`.

## Step 0 — Resolve the offer, the thresholds and the qualitative criteria

### 0.1 — Read the comp thresholds and the role disqualifiers

Every figure you use in the comp gate, and every disqualifier you use in the qualitative role gate,
lives in one of two files under this `jobsearch` plugin. Never hardcode one, never carry one over
from a previous run. Resolve the plugin directory **once**, then read both files from it — never
run a second, independent resolution cascade for the second file.

The first tier is the plugin as loaded: `${CLAUDE_PLUGIN_ROOT}` is this plugin's root when the
skill is invoked from `jobsearch`, and `briefing`'s root when `morning-briefing` invokes it — in
that case `jobsearch` is its sibling under the same marketplace. Both candidates are tried. The
install-path tiers below only serve a session where that root is not set. Before 2026-10-14 the
cascade knew only the renaud-marketplace install paths, and a worker loaded from anywhere else
stopped on `THRESHOLDS_NOT_FOUND` (hal eval `s06-s2-gate-inconnu`).

**Without `Bash`** (an eval run, a session that did not grant it): skip the script and `Read` the two
files at `${CLAUDE_PLUGIN_ROOT}/data/comp-thresholds.json` and
`${CLAUDE_PLUGIN_ROOT}/data/role-criteria.json` (or `${CLAUDE_PLUGIN_ROOT}/../jobsearch/data/…`
when the root is `briefing`'s); if that root is unexpanded or the files are not there, `Glob`
`**/jobsearch/data/comp-thresholds.json` under `~/.claude/plugins` and under the marketplace
checkouts in `~/Projects`, in that order; nothing found → the `_NOT_FOUND` abort below, never a
remembered figure.

```bash
PLUGIN_FILES=$(python3 - <<'PYEOF'
import os, pathlib, sys, glob as _glob

def find_plugin_dir():
    home = pathlib.Path.home()

    def has_data(p):
        return (p / 'data' / 'comp-thresholds.json').exists()

    # Tier 0 — the plugin as loaded. Claude Code sets CLAUDE_PLUGIN_ROOT for a plugin's own
    # files; the literal below is for the case where it is substituted into this file instead of
    # the environment. The root is jobsearch's own, or briefing's when morning-briefing invokes
    # this skill — then jobsearch is its sibling.
    for root in (os.environ.get('CLAUDE_PLUGIN_ROOT', ''), "${CLAUDE_PLUGIN_ROOT}"):
        if not root or root.startswith('${'):
            continue
        root = pathlib.Path(root)
        for cand in (root, root.parent / 'jobsearch'):
            if has_data(cand):
                return cand

    env = os.environ.get('JOBSEARCH_PLUGIN_DIR', '')
    if env and pathlib.Path(env).exists():
        return pathlib.Path(env)

    for mkt in ['renaud-marketplace']:
        cache_root = home / '.claude' / 'plugins' / 'cache' / mkt / 'jobsearch'
        if cache_root.exists():
            cands = sorted(cache_root.glob('*'), key=lambda p: p.stat().st_mtime, reverse=True)
            if cands:
                return cands[0]

    sandbox = _glob.glob('/sessions/*/mnt/.remote-plugins/*/jobsearch')
    sandbox += _glob.glob(str(home / '.claude/plugins/synced/*/jobsearch'))
    sandbox = sorted(sandbox, key=os.path.getmtime, reverse=True)
    if sandbox:
        return pathlib.Path(sandbox[0])

    dev = home / 'Projects' / 'renaud-marketplace' / 'plugins' / 'jobsearch'
    if dev.exists():
        return dev

    return None

plugin_dir = find_plugin_dir()
files = {
    'THRESHOLDS': pathlib.Path('data') / 'comp-thresholds.json',
    'CRITERIA': pathlib.Path('data') / 'role-criteria.json',
}
for key, rel in files.items():
    path = (plugin_dir / rel) if plugin_dir else None
    print(f"{key}={path if path and path.exists() else key + '_NOT_FOUND'}")
PYEOF
)
THRESHOLDS=$(echo "$PLUGIN_FILES" | grep '^THRESHOLDS=' | cut -d= -f2-)
CRITERIA=$(echo "$PLUGIN_FILES" | grep '^CRITERIA=' | cut -d= -f2-)
[ "$THRESHOLDS" = "THRESHOLDS_NOT_FOUND" ] || cat "$THRESHOLDS"
[ "$CRITERIA" = "CRITERIA_NOT_FOUND" ] || cat "$CRITERIA"
```

Read `comp_floor_eur` and `target_comp_eur` from the first file's output, and `disqualifiers[]`
from the second's.

**If either file cannot be resolved, stop.** Do not fall back to a remembered figure or a
remembered list, and do not continue with the corresponding gate skipped: generate no CV, log no
candidature, and return one of:

```
❌ <company> — <role> : abandon, seuils de rémunération illisibles (THRESHOLDS_NOT_FOUND).
   Le plugin jobsearch n'a pas été résolu — ni ${CLAUDE_PLUGIN_ROOT}, ni JOBSEARCH_PLUGIN_DIR.
```

```
❌ <company> — <role> : abandon, critères qualitatifs illisibles (CRITERIA_NOT_FOUND).
   Le plugin jobsearch n'a pas été résolu — ni ${CLAUDE_PLUGIN_ROOT}, ni JOBSEARCH_PLUGIN_DIR.
```

If both are unreadable, report both reasons on the same line.

This used to say "skip the comp gate — a skipped gate is visible". It was not. On 2026-09-04 all
three workers hit `THRESHOLDS_NOT_FOUND` because the resolver ignored the `synced/` layout, and the
50–60 k€ Albatross offer was rejected only because a human ran `find` by hand. A run that trusted
the resolver would have produced a CV and logged an application 33 % under target, unprompted and
unmarked. An abandoned offer costs one re-run; a false application is sent to a recruiter. The same
reasoning applies to `role-criteria.json`: silently skipping the qualitative gate on a read failure
would produce exactly the Stakha case again — a CV and a logged candidature for an offer Renaud
would have screened out on sight (renaud#129).

### 0.2 — Resolve the job description

If `JD_TEXT` is non-empty, use it as-is and skip to Step A.

Otherwise, invoke `Skill(read-job-offer)` with `JOB_URL`. It returns a structured block; take:

- `jd_text` → `JD_TEXT`
- `title` → `JOB_TITLE` (only if `JOB_TITLE` was not supplied)
- `company` → `COMPANY` (only if `COMPANY` was not supplied)
- `freshness`, `applicant_count` → carry into Step D

If it returns `status: unavailable`, stop and return:

```
ÉCHEC | <JOB_TITLE or JOB_URL> — <COMPANY or "?"> | CV:skip LOG:skip | JD unreadable: <reason>
```

**Never build a CV from a digest snippet, a headline, or a company name.** A plausible CV written
from one line of text is worse than no CV — it is indistinguishable from a real one. If a caller
hands you a `JD_TEXT` shorter than 500 characters *and* a `JOB_URL`, re-resolve through
`read-job-offer` and prefer its result.

## Step A — Auto-detect source from SENDER_EMAIL

If `SENDER_EMAIL` is absent or empty, set `source` to `manual`, leave `source_detail` empty, and
skip to Step A.5. That is the `apply-to-offer` path: Renaud found the offer himself.

Otherwise map `SENDER_EMAIL` to `source` using this table:

| SENDER_EMAIL contains | `source` |
|-----------------------|----------|
| `messaging-digest-noreply@linkedin.com` | `linkedin-inmail` |
| any other `@linkedin.com` sender (`jobalerts-noreply@`, `jobs-noreply@`, `jobs-listings@`, …) | `linkedin-alert` |
| `welcometothejungle.com` | `wttj` |
| `collective.work` or `malt.com` | `freelance` |
| `taleez` / `myworkday` / `smartrecruiters` / `lever` / `greenhouse` | `direct-ats` |
| a named recruitment firm (cabinet) | `headhunter` |
| not matched | `other` |

Rows are evaluated **top to bottom, first match wins** — which is why the InMail digest sits
above the `@linkedin.com` catch-all. The catch-all replaced an enumeration of two exact
addresses that did not include `jobs-noreply@linkedin.com`: on 2026-09-04 that sender alone
produced 3 of the day's 13 digests, and the Anthropic and Stakha applications were logged
`other`, under-counting the LinkedIn channel (renaud#126). Match on the domain, not on a list
of local parts that LinkedIn changes without telling anyone.

Set `source_detail` to the sender name or domain extracted from `SENDER_EMAIL`
(e.g. `"LinkedIn Job Alerts"` or the cabinet name). Omit if not identifiable.

## Step A.5 — Comp gate (salary filter)

> **Constants — read in Step 0.1, never written here.**
> `target_comp_eur` (target package — display only) · `comp_floor_eur` (rejection floor).
> Reject only if an explicit compensation figure is found AND is below `comp_floor_eur`.
> Never block when compensation is unknown.

### A.5.1 — Extract compensation from JD_TEXT

Scan `JD_TEXT` for any of these patterns (case-insensitive):

- Ranges: `X–Y k€`, `X to Y €/an`, `X–Y K EUR`, `X-Y €`
- Caps / maximums: `up to X k€`, `jusqu'à X €`, `max X€`
- Annuals: `X € brut annuel`, `X €/year`, `X k€ annuels`
- OTE: `X k€ OTE`, `up to X€ OTE` — treat as the total package (it's variable)

**Extraction rule:** use the **upper bound** of any range, or the stated figure if single.
For OTE, use the stated figure directly (it's already a variable ceiling).
If multiple figures found, use the **highest** (avoid rejecting a negotiable offer).

Convert `k€` or `K€` or `K EUR` → × 1000.

Set `COMP_FOUND` = extracted figure in € (integer), or `null` if nothing found.

### A.5.2 — Fallback web search (only if COMP_FOUND is null)

**Skip this step** if `JD_TEXT` appears complete: length > 500 characters AND contains
at least one of `Responsibilities`, `Requirements`, `Missions`, `Profil`, `About the role`.

If `COMP_FOUND` is still null AND `JOB_URL` is non-empty:
- Call `WebFetch(JOB_URL)` and re-run extraction on the fetched content.
- Update `COMP_FOUND` if a figure is found. Otherwise leave `null`.

### A.5.3 — Decision

| Condition | Action |
|-----------|--------|
| `COMP_FOUND` is null | **Continue** → proceed to Step A.6 |
| `COMP_FOUND` ≥ `comp_floor_eur` | **Continue** → proceed to Step A.6 |
| `COMP_FOUND` < `comp_floor_eur` | **Reject** → return ÉCARTÉ line (skip Steps B and C) |

**If rejected**, return immediately (do not proceed to Steps B or C):
```
ÉCARTÉ | <JOB_TITLE> — <COMPANY> | rému <COMP_FOUND>€ < plancher <comp_floor_eur>€ (comp-thresholds.json) | écart <N>% sous la cible <target_comp_eur>€
```
Where `<N>%` = `round((target_comp_eur - COMP_FOUND) / target_comp_eur × 100)`. The floor is the
figure the offer was rejected on, so it is the one the line names first; the target is context.

## Step A.6 — Qualitative role gate (content filter)

> **Constants — read in Step 0.1, never written here.** `disqualifiers[]` from
> `jobsearch/data/role-criteria.json`, each an `{id, label, detect}` entry.
> This is a content judgment, not a keyword regex: read `detect` and decide whether `JD_TEXT`
> actually matches it. If Step 0.1 could not read the file, you already stopped there —
> this step never runs on a missing list.

### A.6.1 — Check every disqualifier

For each entry in `disqualifiers[]`, read `JD_TEXT` and judge whether it clearly matches `detect`.
A near-miss or an ambiguous case is not a match — reject only on a clear read, the same bar as the
comp gate's "explicit figure" rule. This is exactly the Stakha case (renaud#129): a Forward
Deployed Engineer posting whose required expertise was VPC / on-prem / air-gapped deployment, not
applied-AI delivery — `infra_heavy_fde` exists to catch that before a CV is written, not after.

### A.6.2 — Decision

| Condition | Action |
|-----------|--------|
| No disqualifier matches | **Continue** → proceed to Step A.7 |
| One or more disqualifiers match | **Reject** → return ÉCARTÉ line (skip Steps B and C) |

**If rejected**, return immediately (do not proceed to Steps B or C), naming the first matching
disqualifier and the concrete JD phrase that triggered it:

```
ÉCARTÉ | <JOB_TITLE> — <COMPANY> | critère qualitatif : <label> — <one-line reason from JD_TEXT>
```

## Step A.7 — Stop here in `MODE: gates-only`

Both gates passed. In `MODE: gates-only`, return this line and stop — Steps B to D do not run:

```
PASSE | <JOB_TITLE> — <COMPANY> | rému <COMP_FOUND>€ ≥ plancher <comp_floor_eur>€ — or — rému non indiquée, la porte de rémunération ne bloque pas | critères qualitatifs : aucun ne s'applique (<n> vérifiés, role-criteria.json)
```

Never estimate a salary the text does not state to fill the first field. In `MODE: full`, continue.

## Step B — Generate the CV

Invoke `Skill(cv-generator)` passing `JD_TEXT` as the pasted offer text.
Let `cv-generator` auto-detect profile (P1–P5) and company type (T1–T5), and the language from the
raw offer text.
Output dir: `OUTPUT_DIR` when the caller gave one, otherwise
`~/Library/CloudStorage/SynologyDrive-MyAssistant/jobsearch/`.

Note the detected profile (e.g. `P4`), the cell (e.g. `P4×T5 EN`) and the generated PDF path.

**The cell's About and competency blocks ship as validated.** Since renaud#176 the P4 cells of
`cv-master.json` carry the three-line About (bridge between the client's need and the product;
AI expertise plus the whole stack; entrepreneur plus international enterprise accounts) and the
three FDE competency blocks Renaud validated on the HappyRobot application. `cv-generator`'s
Step 3b personalises **bullets** to the offer; it does not rewrite that About or those blocks
unless the offer plainly calls for another framing, and it never takes a technology out of them.
A rendered CV that needs three generations before it is sendable is the defect this skill exists
to remove: the first render must already be the validated structure.

`cv-generator` adds, removes or replaces a bullet without touching the master: a `null` value in
`--bullet-overrides` or `--container-items` removes that line, a `+` index appends one, and
`--containers-override` replaces a cell's three competency blocks whole. Use those flags — never
copy `cv-master.json` to a scratch folder and run with `--data-dir` to get a change in.

If `cv-generator` fails → proceed to Step D with the failure reason. Do not abort.

## Step B.5 — Judge review, Tour 1

Skip this step entirely if Step B failed — there is no CV to judge. Proceed to Step D with the
failure noted; Step C does not run (nothing to log).

**If the `Agent` tool is unavailable in your context** — which only happens when the caller
itself runs as a background sub-agent — do not work around it and do not log: the PDF stays where
Step B wrote it, Step C is skipped, and Step D returns `ÉCHEC | … | CV:ok LOG:skip | juge
indisponible : outil Agent absent dans ce contexte`. A CV is never logged without a judge score,
and a caller that cannot spawn the judge is misconfigured, not a reason to lower the bar.

Otherwise, spawn the judge, **foreground** (you need its verdict before deciding what to
regenerate):

```
Agent(cv-judge, run_in_background: false, prompt="""
JD_TEXT: <the full job description text>
CV_PATH: <absolute path to the PDF generated in Step B>
JOB_TITLE: <JOB_TITLE>
COMPANY: <COMPANY>
PROFILE: <profile/cell detected in Step B, e.g. P4×T5 EN>
""")
```

Keep the judge's Tour 1 answer verbatim — Tour 2 carries it (Step B.6).

**Apply the corrections the judge marked as ready-to-paste** — only the ones that name what they
displace (a bullet swapped, a claim shortened, a sentence cut). Skip any suggestion that is a net
addition with nothing removed, and skip anything the judge routed to its « Notes d'entretien »
section instead of the CV body. Regenerate via `Skill(cv-generator)` with the accepted
corrections (`--bullet-overrides`, `--container-items`, `--about-override`,
`--containers-override`, `--title-override` — whichever fits). Note the new PDF path (unchanged
when cv-generator overwrites in place).

**Never take a technology, a product or a result out of the CV because the judge calls it
unproven.** The judge checks claims against `parcours` alone; a claim it could not find there is
reported as « non vérifié dans parcours », and the decision is yours: keep it when `parcours`
plainly supports it (a stack named for a product, a client, a figure), cut it only when it is
actually false. A judge that recommends removing OAuth, Node or « full-stack » is the under-selling
defect of renaud#176 §3 — do not apply such a recommendation; say in Step D that it was declined.

**Never accept a CV at cv-generator's tightest compression level.** cv-generator retries up to
three progressively tighter compact CSS levels before it warns of page overflow; the tightest
makes the font too small to read comfortably. If cv-generator's own report warns of overflow
after all three levels, or the regenerated PDF visibly reads as cramped when you check it, the
fix is to **cut** judge-flagged filler or the lowest-impact accepted addition — never to leave it
at the tightest level. Regenerate again after cutting if needed.

## Step B.6 — Judge review, Tour 2 (short)

Spawn the judge a second time, **foreground**, with Tour 1's verdict carried in the prompt —
the call returns Tour 2's answer before you take the next step:

```
Agent(cv-judge, run_in_background: false, prompt="""
TOUR: 2
JD_TEXT: <the full job description text>
CV_PATH: <path to the regenerated PDF>
JOB_TITLE: <JOB_TITLE>
COMPANY: <COMPANY>
TOUR_1_VERDICT: <Tour 1's answer, verbatim — score, the five problems, the rewrites>
Corrections applied: <list of Tour 1 corrections actually applied>
Corrections skipped: <list of Tour 1 corrections skipped, with why>
""")
```

Never resume the Tour 1 judge with `SendMessage` instead. Its reply comes back as a message on a
later turn, after your answer: on hal S06 run `20261013-000828` (s4-juge) the worker returned
its summary while Tour 2 was still running, and the score v1 → v2 never reached Renaud. Never
write Step D without Tour 2's score.

Tour 2 runs even when Tour 1 left nothing to correct: its score is the one the vault keeps.

Apply the same rule as Tour 1 — accepted corrections must be swaps, never additions, and never an
under-sell — and regenerate once more via `Skill(cv-generator)` if the judge's Tour 2 response
calls for it. This is the final CV; it proceeds to Step C.

**Never block logging on an imperfect Tour 2 verdict.** If the judge still reports something
broken that cannot be fixed without exceeding the page (e.g. the JD asks for two contradictory
things), proceed to Step C anyway — the constraint here is "never silent", not "never
imperfect". Carry the judge's final score and its top unresolved issue into Step D as a
degradation instead of withholding the CV.

## Step C — Log the application

Skipped when the caller passed an `OUTPUT_DIR` (a replay, a test): say so in Step D.

Invoke `Skill(log-application)` with:
- Offer text: `JD_TEXT`
- Company: `COMPANY`
- Role: `JOB_TITLE`
- Source: the `source` detected in Step A
- Source detail: the `source_detail` from Step A (omit if empty)
- URL: `JOB_URL` (omit if empty string)
- Statut: `📝 À postuler`
- CV path: `jobsearch/<cv_filename>` — the **final** PDF, after Steps B.5/B.6's corrections
- CV profile: the profile detected in Step B, e.g. `P4`
- CV judge: the judge's final score as `<v1>→<v2>/10`

All three CV fields are present or none is: a CV without a judge score never reaches
`log-application`.

If `log-application` fails → proceed to Step D with failure reason.

## Step D — Return one-line summary

**On success (B, B.5, B.6 and C succeeded):**
```
CV_préparé | <JOB_TITLE> — <COMPANY> | Profil : P<n> | CV : <cv_filename> | Source : <source> | Juge : <v1>→<v2>/10 | <freshness>, <applicant_count> candidats
```

Append the freshness and applicant-count fragment only when Step 0.2 actually returned them; omit
it silently otherwise — never print an empty or guessed value. The `Juge :` fragment is always
present on a `CV_préparé` line: a line without it is an `ÉCHEC` line.

**If any degradation occurred**, append it to the line after a `| ⚠️ ` marker — one fragment per
degradation, and never drop one:

- `⚠️ JD partielle` — the JD resolved but is under 500 characters
- `⚠️ ancre corrigée (parcours ≠ cv-master.json) : <quoi>` — the judge caught a factual conflict and
  it was fixed; say what, so Renaud sees it went through without having to re-check
- `⚠️ juge : <résumé du problème résiduel>` — Tour 2 still reported something unresolved that could
  not be fixed without exceeding the page
- `⚠️ recommandation écartée : <quoi>` — a judge suggestion declined as an under-sell (Step B.5)
- `⚠️ non loggé : OUTPUT_DIR fourni` — a replay; the PDF exists, no candidature was written

**On partial or total failure:**
```
ÉCHEC | <JOB_TITLE> — <COMPANY> | CV:<ok/fail> LOG:<ok/fail/skip> | <reason>
```

## Constraints (load-bearing)

- **No cover letter.** Never generate a cover letter under any circumstance.
- **No auto-apply.** Never submit an application, click any "Apply" button, or interact with job portals.
- **No recruiter reply.** Never compose or send any message to any person.
- **Status is `📝 À postuler`** — NOT `✉️ Candidature envoyée`. Renaud moves the card to « Candidature envoyée » when he actually submits.
- **One offer only.** You handle exactly the one offer the caller described. No iteration over other offers — the caller loops, not you.
- **Fail loud, not silent.** If any step fails, report it clearly in Step D — never return a silent success.
- **Unknown compensation = continue.** Never reject an offer solely because the salary is not mentioned.
- **Never invent a JD.** The CV is built from a job description that was actually read — via `JD_TEXT` from the caller or `Skill(read-job-offer)` in Step 0.2. A digest snippet, a title, or a company description is not a JD: return `ÉCHEC` rather than a CV built on one.
- **Never hardcode a compensation figure.** Every threshold comes from `jobsearch/data/comp-thresholds.json`, read at Step 0.1. If it is unreadable the skill aborts and says so out loud — it is never replaced by a remembered number.
- **Never hardcode a qualitative disqualifier.** Every entry comes from `jobsearch/data/role-criteria.json`, read at Step 0.1. If it is unreadable the skill aborts and says so out loud — the gate is never silently skipped, and a disqualifier is never restated inline here or in `morning-briefing`.
- **One definition site per figure, one per disqualifier.** If a threshold or a disqualifier needs to change, it changes in its file, not here and not in `morning-briefing`.
- **No CV is logged unjudged.** Steps B.5 and B.6 run for every successfully generated CV. No `Agent` tool means no log and an `ÉCHEC` line — never a « ⚠️ CV non jugé » candidature in the vault.
- **A judge rewrite without a named displacement is never applied.** The page is already full —
  applying a net-addition suggestion is exactly what pushes a CV to cv-generator's tightest,
  barely-legible compression level. Cut before you add.
- **A judge recommendation that under-sells is never applied.** The goal of the CV is the
  interview. A technology or a claim `parcours` supports stays on the page whatever a retex or a
  learning note once said.
- **`parcours` outranks `cv-master.json`.** When the judge flags a conflict between them,
  the correction follows `parcours`, and Step D says so — see `cv-generator/SKILL.md` §"Factual
  source of truth" for the three real cases this already caught.
