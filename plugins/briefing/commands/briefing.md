---
description: Produce today's morning briefing (calendars + hal tasks + Obsidian jobsearch, read-only)
---

Run the `morning-briefing` skill from the `briefing` plugin: produce one read-only brief covering today's Google Calendars (the union declared by your hal workspaces), current-sprint hal tasks across every workspace you belong to (each labelled with its workspace name), and Obsidian jobsearch state (interviews, relances due, active candidatures). If any source is unreachable, render `⚠️ DOWN` for that section — never silent omission.
