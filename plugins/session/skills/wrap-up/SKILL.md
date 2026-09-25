---
name: wrap-up
description: >
  End a Claude Code session cleanly, in one pass. Checks what is not yet safe
  (uncommitted files, unpushed commits, unmerged branch, stale STATUS.md,
  leftover worktrees), then closes one of two ways: work finished → tidy up and
  say "OK to close"; work unfinished → write a handoff the next session picks up
  by itself. Use when Renaud says "wrap-up", "je peux fermer la session ?",
  "tout est à jour ?", "tout est sur main ?", "fais un handoff", "mon quota est
  à 99 %", "ton contexte est plein", "je reprendrai dans une nouvelle session",
  or before any /clear meant to continue the same work fresh.
allowed-tools: "Read AskUserQuestion Bash(git status *) Bash(git log *) Bash(git branch *) Bash(git rev-parse *) Bash(git symbolic-ref *) Bash(git worktree list *) Bash(git fetch *) Bash(ls *)"
---

# wrap-up — close a session, finished or not

One skill for every session end. It replaces the per-repo `/handoff` command:
a handoff is simply the wrap-up of a session whose work is not done.

## Where the handoff lives

```bash
HANDOFF_DIR="$(git rev-parse --path-format=absolute --git-common-dir)/claude-handoffs"
HANDOFF="$HANDOFF_DIR/$(git branch --show-current | sed 's|/|--|g').md"
```

Inside the repository's shared `.git` directory, one file per branch:

- **never tracked** — no `.gitignore` entry, never lands in a commit or a PR;
- **shared by every worktree** of the repo — a session opened in a fresh
  worktree still sees it;
- **survives worktree removal** — the branch's work is on the remote, the
  handoff is next to the git history.

The `SessionStart` hook (`~/.claude/hooks/session_start_context.py`) injects the
current branch's handoff in full, and lists the other branches' handoffs by
title. That is the whole resume mechanism — nothing to paste.

Outside a git repository there is nowhere shared to put it: say so, and write
`HANDOFF.md` in the working directory only if Renaud agrees.

## Step 1 — Inventory (read-only, one pass)

```bash
git status --short
git branch --show-current
git rev-parse --abbrev-ref @{u}                      # upstream, if any
git log --oneline @{u}..HEAD                          # unpushed (with upstream)
git log --oneline "$(git symbolic-ref refs/remotes/origin/HEAD)..HEAD"   # ahead of default branch
git branch -r --contains HEAD                         # is HEAD already on the remote?
git worktree list
ls "$HANDOFF_DIR" 2>/dev/null
```

Then, for the tracking files:

- `.claude/STATUS.md` — does it reflect what this session finished? Check it
  against the conversation, not against its own date. A task done here and
  still unchecked is a finding.
- `CONTEXT.md` in the working directory, if present — same test.
- `BLUEGREEN_MAP.md` — only if this session added, renamed or removed a skill,
  plugin, MCP tool or connector (rule in `~/Projects/CLAUDE.md`).

For each other worktree in `git worktree list`: is its branch merged into
`origin/HEAD` (`git branch -r --merged origin/HEAD` after `git fetch`)? A merged
one is removable. Never propose removing the worktree this session runs in.

## Step 2 — Finished or not?

Decide from the conversation: is the goal Renaud set for this session done?
If it is genuinely unclear, ask once — one question, not a checklist.

## Step 3a — Finished

1. Show the list of actions, then wait for one "oui":
   - commit remaining changes (atomic message, repo conventions);
   - check the finished tasks in `STATUS.md` / `CONTEXT.md`;
   - push the branch, or merge into main if Renaud said so this session;
   - delete `$HANDOFF` if one exists for this branch — it is consumed;
   - remove merged worktrees and their local branches.
2. Do them. Any failure stops the list and is reported as is.
3. Verdict, in one block:

   ```
   ✅ OK pour fermer.
   Sur le remote : <branch> @ <sha>  ·  PR : <url or "aucune">
   Rien en local.
   ```

## Step 3b — Not finished → handoff

1. Commit the work in progress (`wip: <what>` if it does not build) and push
   the branch — a handoff that points at commits only this machine has is not a
   handoff. Ask before pushing, like any push.
2. Move the open items to `## In Progress` of `STATUS.md` (one line each, no
   dated entry — `STATUS.md` says what is true now).
3. Write `$HANDOFF` (overwrite if it exists — one handoff per branch, always the
   latest):

   ```markdown
   # Handoff: <task, one line>

   **Date:** <YYYY-MM-DD>  ·  **Repo:** <name>  ·  **Branch:** <branch> @ <short sha>
   **Worktree:** <absolute path, or "removed">

   ## Goal
   <1–2 sentences>

   ## Done
   - [x] <item> — <file or commit>

   ## Next
   - [ ] <item, specific enough to act on: file, function, command>

   ## Decisions (and why)
   - **<decision>** — <why; alternative rejected>

   ## Dead ends — don't retry
   - <approach> — <why it failed>

   ## First action
   <the exact first step for the next session>
   ```

   Under 80 lines. Paths, not file contents. Every item restated in words, never
   a bare "#4" or "option B".
4. Verdict:

   ```
   ⏸ Handoff écrit : <path>
   Branche poussée : <branch> @ <sha>
   Pour reprendre : /clear ici, ou nouvelle session dans <repo> → « reprends »
   ```

## Resuming (what the next session does)

When a handoff was injected at session start, or Renaud says "reprends" /
"continue le handoff":

1. Read it. Check it against the repo before trusting it: `git fetch`, the
   branch exists on the remote at the stated sha or later.
2. Get onto the branch: if `git worktree list` shows it checked out elsewhere,
   work in that path; otherwise `git switch <branch>` here.
3. Say in two lines where things stand and what the first action is, then do it.
4. Leave the handoff in place until the work is finished — the next wrap-up
   (Step 3a) deletes it.

## Rules

- Nothing is pushed, merged or deleted without Renaud's "oui" on the listed
  actions. The inventory itself never asks.
- Never delete a branch that is not merged, nor a worktree with uncommitted
  changes — report it instead.
- Report what is, not what should be: "3 commits non poussés", not "tout est
  bon" before checking.
