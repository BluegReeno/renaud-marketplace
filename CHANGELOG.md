# Changelog

Each plugin tracks its own version. Entries are grouped per plugin, newest
version first. The current version of every plugin must appear here — CI
(`scripts/check_version_sync.sh`) fails if a plugin's `plugin.json` version has
no matching entry below.

Heading format (parsed by the sync check): `## <plugin> <version>`.

## jobsearch 0.8.3

- CV generation (`cv-generator`), cover letters (`cover-letter`), application
  logging (`log-application`), interview prep (`interview-prep`), CR logging
  (`log-cr`), and job-search vault I/O (`jobsearch-vault`).

## briefing 0.8.0

- Daily morning briefing (`morning-briefing`), on-demand mail triage
  (`mail-triage`), weekly sprint review (`sprint-review`) and sprint planner
  (`sprint-planner`).

## improve 0.1.2

- Skill improvement capture (`improve`) — turn an observation into a GitHub
  issue in ≤30s from Cowork.

## myspy 0.1.0

- Personal weekly self-reflection check-in (`myspy`) — structured CBT/SFBT
  session backed by a private OKF knowledge base.
