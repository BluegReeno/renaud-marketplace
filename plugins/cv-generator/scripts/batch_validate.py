#!/usr/bin/env python3
"""Batch validation: generate all 30 CVs (15 cells × FR+EN), assert 1-page A4."""
import subprocess
import sys
import pathlib
import tempfile
import os

VALID_CELLS = [
    ('p1', 't1'), ('p1', 't2'), ('p1', 't3'), ('p1', 't4'), ('p1', 't5'),
    ('p2', 't1'), ('p2', 't3'), ('p2', 't4'), ('p2', 't5'),
    ('p3', 't1'), ('p3', 't5'),
    ('p4', 't1'), ('p4', 't5'),
    ('p5', 't3'), ('p5', 't5'),
]
LANGS = ['en', 'fr']
GENERATOR = pathlib.Path(__file__).parent / 'generate_cv.py'


def check_page_count(pdf_path):
    """Return page count using pikepdf."""
    import pikepdf
    with pikepdf.open(pdf_path) as pdf:
        return len(pdf.pages)


def main():
    out_dir = pathlib.Path(tempfile.mkdtemp(prefix='cv_batch_'))
    errors = []
    total = 0

    print(f"Output directory: {out_dir}")
    print(f"Generating {len(VALID_CELLS) * len(LANGS)} CVs...")

    for (profile, ctype) in VALID_CELLS:
        for lang in LANGS:
            total += 1
            fname = f"CV_Renaud_Laborbe_{profile.upper()}_{ctype.upper()}_{lang.upper()}.pdf"
            out_path = out_dir / fname

            env = os.environ.copy()
            env['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib'  # WeasyPrint/Pango on macOS

            result = subprocess.run(
                [
                    'python3', str(GENERATOR),
                    '--profile', profile,
                    '--company-type', ctype,
                    '--lang', lang,
                    '--output', fname,
                    '--output-dir', str(out_dir),
                ],
                capture_output=True, text=True, env=env
            )

            if result.returncode != 0:
                errors.append(f"FAIL generation {profile}x{ctype}/{lang}: {result.stderr[-300:]}")
                continue

            if not out_path.exists():
                errors.append(f"FAIL missing output {fname}")
                continue

            pages = check_page_count(out_path)
            if pages != 1:
                errors.append(f"FAIL {fname}: {pages} pages (expected 1)")
            else:
                print(f"  OK  {fname}")

    print(f"\n{'=' * 50}")
    print(f"Total: {total} CVs — {total - len(errors)} OK, {len(errors)} errors")

    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("All 30 CVs validated — 1 page each.")


if __name__ == '__main__':
    main()
