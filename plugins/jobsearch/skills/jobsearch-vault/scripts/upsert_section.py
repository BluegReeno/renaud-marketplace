#!/usr/bin/env python3
"""Idempotently add one bullet line to a note's body section (stdlib-only).

Creates the `## heading` (and `### subheading`, if given) when missing.
Dedup is exact-string only: a line identical (after stripping) to one
already under the same heading/subheading is skipped, never duplicated.
A contradicting entry — different date, different quote — is a different
line and is appended alongside the existing one, never replacing it.

Usage:
    python upsert_section.py "CRM-JobSearch/Opportunites/Poste — Entreprise.md" \\
        --heading "🏢 BANT (agrégé)" --subheading "B — Comp/Budget" \\
        --line "- 2026-09-15 — Deon van der Vyver (CTO) : « fourchette 70-85k » → [[CR Cognyx — Deon van der Vyver — 15-09-2026]]"
"""

import argparse
import json
import sys

from obsidian_api import ObsidianAPI


def main():
    parser = argparse.ArgumentParser(description="Upsert a bullet line into a note's body section")
    parser.add_argument("path", help="Vault-relative path to the note")
    parser.add_argument("--heading", required=True, help="## heading text (without the '##')")
    parser.add_argument("--subheading", help="### subheading text (without the '###'), optional")
    parser.add_argument("--line", required=True, help="Full bullet line to add, e.g. '- 2026-09-15 — ...'")
    args = parser.parse_args()

    api = ObsidianAPI()

    try:
        api.upsert_section(args.path, args.heading, args.line, subheading=args.subheading)
        print(json.dumps({
            "path": args.path,
            "heading": args.heading,
            "subheading": args.subheading,
        }, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
