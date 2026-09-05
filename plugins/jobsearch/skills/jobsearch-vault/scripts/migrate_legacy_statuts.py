#!/usr/bin/env python3
"""One-shot migration: normalize legacy `opportunite-js` statut values (#127).

The vault accumulated statut values that predate `JS_STATUTS_LEGACY_ALIASES`
in note_schemas.py (manual Obsidian edits, outside the skill pipeline). This
rewrites every note still carrying one of those legacy values to its
canonical replacement.

Usage:
    python migrate_legacy_statuts.py            # dry run, prints what would change
    python migrate_legacy_statuts.py --apply    # actually rewrite the notes

Safe to re-run: notes already on a canonical value are left untouched.
"""

import argparse
import sys

from note_schemas import JS_STATUTS_LEGACY_ALIASES
from obsidian_api import ObsidianAPI

FOLDER = "CRM-JobSearch/Opportunites"


def main():
    parser = argparse.ArgumentParser(description="Normalize legacy opportunite-js statut values")
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry run)")
    args = parser.parse_args()

    api = ObsidianAPI()

    try:
        entries = api.list_directory(FOLDER)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    md_files = [e for e in entries if isinstance(e, str) and e.endswith(".md")]
    changed = 0

    for filepath in md_files:
        path = f"{FOLDER}/{filepath}" if "/" not in filepath else filepath
        try:
            note = api.read_note(path)
        except Exception:
            continue

        fm = note.get("frontmatter", {}) or {}
        current = fm.get("statut")
        replacement = JS_STATUTS_LEGACY_ALIASES.get(current)
        if replacement is None:
            continue

        changed += 1
        print(f'{path}: "{current}" -> "{replacement}"')
        if args.apply:
            api.update_field(path, "statut", replacement)

    if not md_files:
        print(f"# no notes found in {FOLDER}", file=sys.stderr)
    elif changed == 0:
        print("# no legacy statut values found — nothing to migrate", file=sys.stderr)
    elif not args.apply:
        print(f"\n# dry run: {changed} note(s) would change. Re-run with --apply to write.", file=sys.stderr)
    else:
        print(f"\n# migrated {changed} note(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
