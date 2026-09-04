#!/usr/bin/env python3
"""Verify a generated CV exposes one clickable link per contact entry.

A contact line rendered as a bare <span> looks identical on screen and is dead in
the PDF: a recruiter has to retype the URL. This checks the PDF itself — the /URI
annotations WeasyPrint emits — rather than the HTML that produced it.

Usage: uv run --with pypdf python3 check_pdf_links.py <cv.pdf> [--expect email linkedin github]
Exit 0 = every expected link is present. Exit 1 = at least one is missing.
"""
import sys

from pypdf import PdfReader

DEFAULT_EXPECTED = {
    "email": "mailto:",
    "linkedin": "linkedin.com",
    "github": "github.com",
}


def uris(path):
    reader = PdfReader(path)
    found = set()
    for page in reader.pages:
        for annot in page.get("/Annots") or []:
            action = annot.get_object().get("/A")
            if action and action.get("/URI"):
                found.add(str(action["/URI"]))
    return len(reader.pages), found


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    pdf_path = sys.argv[1]
    wanted = sys.argv[3:] if len(sys.argv) > 3 and sys.argv[2] == "--expect" else list(DEFAULT_EXPECTED)

    pages, found = uris(pdf_path)
    print(f"pages: {pages}")
    for uri in sorted(found):
        print(f"  link  {uri}")

    missing = [name for name in wanted
               if not any(DEFAULT_EXPECTED.get(name, name) in uri for uri in found)]
    if missing:
        print(f"\nFAIL: no /URI annotation for: {', '.join(missing)}")
        return 1
    if pages != 1:
        print(f"\nFAIL: CV must be 1 page, got {pages}")
        return 1
    print("\nOK: 1 page, every expected contact link is clickable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
