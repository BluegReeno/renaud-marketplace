#!/usr/bin/env python3
"""Batch validation: generate all 30 CVs (15 cells × FR+EN), assert 1-page A4.

Also asserts every PDF embeds only the bundled font families — WeasyPrint names them after the
CSS family: 'CV-Sans' (Roboto) and 'CV-Symbols' (DejaVu Sans, for the glyphs Roboto lacks). Any
other font name means a glyph fell back to a system font, i.e. the page would not render the
same on another machine — the defect the bundle exists to remove (renaud#176 §7). Runs on the
Mac and in CI on Linux; the Linux run is the one that proves the cloud sandbox fits the page.
"""
import subprocess
import sys
import pathlib
import tempfile
import os

BUNDLED_FAMILIES = ('CV-Sans', 'CV-Symbols')

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


def embedded_fonts(pdf_path):
    """Return the set of base font names used by the PDF's pages (subset prefixes stripped)."""
    import pikepdf
    names = set()
    with pikepdf.open(pdf_path) as pdf:
        for page in pdf.pages:
            fonts = page.Resources.get('/Font') or {}
            for _, font in fonts.items():
                base = str(font.get('/BaseFont', ''))
                names.add(base.lstrip('/').split('+', 1)[-1])
    return names


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
            if sys.platform == 'darwin':
                env['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib'  # WeasyPrint/Pango on macOS only

            result = subprocess.run(
                [
                    'python3', str(GENERATOR),
                    '--profile', profile,
                    '--company-type', ctype,
                    '--lang', lang,
                    '--output', fname,
                    '--output-dir', str(out_dir),
                    # Validation renders every cell, including on a machine with no
                    # contact.local.json. Since renaud#98 a missing file exits 1 by
                    # default, so this path has to ask for the placeholder explicitly.
                    '--allow-placeholder',
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
                continue

            fonts = embedded_fonts(out_path)
            foreign = sorted(f for f in fonts if not f.startswith(BUNDLED_FAMILIES))
            if foreign or not fonts:
                errors.append(f"FAIL {fname}: fonts {sorted(fonts)} — expected only {BUNDLED_FAMILIES} "
                              f"(a foreign name means a glyph fell back to a system font)")
                continue

            level = result.stdout.count('retrying with compact layout level')
            print(f"  OK  {fname}  (compact level {level}/3, fonts {sorted(fonts)})")

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
