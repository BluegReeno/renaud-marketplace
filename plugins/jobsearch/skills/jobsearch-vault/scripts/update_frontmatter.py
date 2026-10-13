#!/usr/bin/env python3
"""Update a single frontmatter field on a job-search vault note (filesystem-only).

Usage:
    python update_frontmatter.py "CRM-JobSearch/Opportunites/Poste — Entreprise.md" statut "❌ Refus"
    python update_frontmatter.py "Taches/Relance — Anthropic — 2026-06-12.md" echeance "2026-06-26"
    python update_frontmatter.py "Taches/Task.md" etiquettes --json-value '["jobsearch"]'
"""

import argparse
import json
import sys

from note_schemas import coerce_update, validate_update
from obsidian_api import ObsidianAPI


def main():
    parser = argparse.ArgumentParser(description="Update a frontmatter field")
    parser.add_argument("path", help="Vault-relative path to the note")
    parser.add_argument("field", help="Frontmatter field name to update")
    parser.add_argument("value", nargs="?", help="New value (string)")
    parser.add_argument("--json-value", help="New value as JSON (for arrays, numbers, booleans)")
    args = parser.parse_args()

    if not args.value and not args.json_value:
        parser.error("Provide a value or --json-value")

    if args.json_value:
        try:
            value = json.loads(args.json_value)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON value: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        value = args.value

    api = ObsidianAPI()

    try:
        note = api.read_note(args.path)
    except Exception as e:
        print(f"Error: cannot read {args.path}: {e}", file=sys.stderr)
        sys.exit(1)
    note_type = (note.get("frontmatter", {}) or {}).get("type")
    if note_type:
        value = coerce_update(note_type, args.field, value)
        vr = validate_update(note_type, args.field, value)
        for w in vr.warnings:
            print(f"Warning: {w}", file=sys.stderr)
        if not vr.ok:
            for e in vr.errors:
                print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        api.update_field(args.path, args.field, value)
        # Read back to confirm
        note = api.read_note(args.path)
        fm = note.get("frontmatter", {}) or {}
        actual = fm.get(args.field)
        print(json.dumps({
            "path": args.path,
            "field": args.field,
            "value": actual,
        }, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
