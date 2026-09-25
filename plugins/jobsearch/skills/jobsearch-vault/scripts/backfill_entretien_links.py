#!/usr/bin/env python3
"""One-shot backfill: link every `opportunite-js` to its `entretien` notes (#119).

An `entretien` note declares its opportunité only in frontmatter
(`opportunite`, and `opportunite_secondaire` for notes shared by two
candidatures), so nothing on the opportunité led back to its preps and CRs.
`interview-prep` and `log-cr` now write that back-link themselves, into the
opportunité's `## Entretiens` section; this rebuilds the section for every
note written before they did.

Each line is the exact format those two skills write, so a later skill run on
the same entretien is deduplicated by `upsert_section` instead of repeated:

    - <YYYY-MM-DD> — <Prep|CR|categorie> — [[<entretien note name>]]

Usage:
    python backfill_entretien_links.py            # dry run, prints what would be added
    python backfill_entretien_links.py --apply    # actually write the sections

Safe to re-run: a line already in the section is skipped.
"""

import argparse
import re
import sys
import unicodedata

from obsidian_api import ObsidianAPI

ENTRETIENS = "CRM-JobSearch/Entretiens"
OPPORTUNITES = "CRM-JobSearch/Opportunites"
HEADING = "Entretiens"
LINK_FIELDS = ("opportunite", "opportunite_secondaire")

# categorie → short label. Anything else (legacy or hand-written values) is
# kept verbatim, so the line still says what kind of note it is.
LABELS = {"Préparation": "Prep", "Compte-rendu": "CR"}
# Same-day order: the prep is written before the meeting, the CR after it.
SAME_DAY_RANK = {"Prep": 0, "CR": 2}

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
FILENAME_DATE = re.compile(r"(\d{2})-(\d{2})-(\d{4})$")
UNDATED = "sans date"


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def link_target(value) -> str | None:
    """Return the note name a `"[[Name]]"` / `"[[folder/Name|alias]]"` value points to."""
    if not isinstance(value, str):
        return None
    m = WIKILINK.search(value)
    if not m:
        return None
    return nfc(m.group(1).strip().rsplit("/", 1)[-1])


def entretien_date(fm: dict, name: str) -> str:
    """`date` frontmatter (ISO, datetime tolerated), else the filename's DD-MM-YYYY suffix."""
    value = fm.get("date")
    if isinstance(value, str) and re.match(r"\d{4}-\d{2}-\d{2}", value):
        return value[:10]
    m = FILENAME_DATE.search(name)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return UNDATED


def entretien_label(categorie) -> str:
    return LABELS.get(categorie, categorie) if isinstance(categorie, str) and categorie else "Note"


def entretien_line(date: str, label: str, name: str) -> str:
    return f"- {date} — {label} — [[{name}]]"


def collect(api: ObsidianAPI) -> tuple[dict, list]:
    """Map each opportunité note name to its sorted (sort key, line) list; list unresolved links."""
    opportunites = {nfc(f[:-3]): f for f in api.list_directory(OPPORTUNITES)}
    by_opp: dict[str, list] = {}
    unresolved = []

    for filename in api.list_directory(ENTRETIENS):
        name = nfc(filename[:-3])
        fm = api.read_note(f"{ENTRETIENS}/{filename}").get("frontmatter", {}) or {}
        date = entretien_date(fm, name)
        label = entretien_label(fm.get("categorie"))
        line = entretien_line(date, label, name)
        key = (date == UNDATED, date, SAME_DAY_RANK.get(label, 1), name)
        for field in LINK_FIELDS:
            target = link_target(fm.get(field))
            if target is None:
                continue
            if target not in opportunites:
                unresolved.append((name, field, target))
                continue
            by_opp.setdefault(opportunites[target], []).append((key, line))

    for entries in by_opp.values():
        # Chronological; undated notes last; same day: prep, other notes, CR.
        entries.sort(key=lambda e: e[0])
    return by_opp, unresolved


def main():
    parser = argparse.ArgumentParser(description="Backfill ## Entretiens on opportunite-js notes")
    parser.add_argument("--apply", action="store_true", help="Write changes (default: dry run)")
    args = parser.parse_args()

    try:
        api = ObsidianAPI()
        by_opp, unresolved = collect(api)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    notes_changed = lines_added = 0
    for filename in sorted(by_opp):
        path = f"{OPPORTUNITES}/{filename}"
        # Dry-run the dedup on an in-memory copy, so the report lists only what is new.
        _, body = api._split_frontmatter(api.read_raw(path))
        new_lines = []
        for _, line in by_opp[filename]:
            updated = api._upsert_section_body(body, HEADING, line, None)
            if updated != body:
                new_lines.append(line)
                body = updated
        if not new_lines:
            continue

        notes_changed += 1
        lines_added += len(new_lines)
        print(f"{path}:")
        for line in new_lines:
            print(f"  {line}")
            if args.apply:
                api.upsert_section(path, HEADING, line)

    for name, field, target in unresolved:
        print(f'# unresolved: "{name}" {field} → [[{target}]] (no such note in {OPPORTUNITES})',
              file=sys.stderr)

    if notes_changed == 0:
        print("# every opportunité already links its entretiens — nothing to backfill",
              file=sys.stderr)
    elif not args.apply:
        print(f"\n# dry run: {lines_added} line(s) on {notes_changed} note(s) would be added. "
              f"Re-run with --apply to write.", file=sys.stderr)
    else:
        print(f"\n# added {lines_added} line(s) on {notes_changed} note(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
