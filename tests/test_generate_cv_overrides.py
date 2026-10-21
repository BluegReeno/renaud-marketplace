"""Offline tests of generate_cv.py's override grammar and font bundling (renaud#176 §7).

No WeasyPrint: these drive generate_cv_html(), which writes the HTML the PDF is rendered from,
and read that HTML. They pin:

- the shared key grammar of --bullet-overrides and --container-items — a text replaces, null
  removes, a key starting with "+" appends, indices refer to the stored list, bad keys warn;
- --containers-override replacing a cell's three competency blocks whole;
- the bundled font substituted as an absolute file URL, and a missing face stopping the script;
- the education separator validated on the HappyRobot CV.

Until this change, adding or removing a bullet meant copying cv-master.json to a scratch folder
and patching the generator — the correction died with the session.

Run: python3 tests/test_generate_cv_overrides.py
"""
import contextlib
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = REPO / "plugins" / "jobsearch"
SCRIPT = PLUGIN / "scripts" / "generate_cv.py"

spec = importlib.util.spec_from_file_location("generate_cv", SCRIPT)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

CONTACT = {"phone": "+33 (0)0 00 00 00 00", "email": "test@example.com", "location": "Paris", "location_url": None}


def render(**overrides):
    """Render one cell to HTML and return (html, stdout)."""
    cv_data = gen.load_cv_data()
    out = io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "cv.html"
        with contextlib.redirect_stdout(out):
            gen.generate_cv_html(output_html_path=path, cv_data=cv_data, contact=CONTACT,
                                 **{"profile": "p4", "company_type": "t5", "lang": "en", **overrides})
        return path.read_text(encoding="utf-8"), out.getvalue()


class TestApplyLineEdits(unittest.TestCase):
    def test_replace_remove_append_against_the_original_indices(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = gen.apply_line_edits(["a", "b", "c"], {"0": None, "2": "C", "+": "d", "+2": "e"}, "t")
        self.assertEqual(result, ["b", "C", "d", "e"])
        self.assertEqual(out.getvalue(), "")

    def test_bad_keys_warn_and_are_skipped(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = gen.apply_line_edits(["a", "b"], {"5": "x", "zz": "y", "+": None}, "--test")
        self.assertEqual(result, ["a", "b"])
        warnings = out.getvalue().splitlines()
        self.assertEqual(len(warnings), 3)
        self.assertTrue(all(w.startswith("WARNING: --test key") for w in warnings), warnings)


class TestBulletOverrides(unittest.TestCase):
    def test_null_removes_and_plus_appends_a_bullet(self):
        base, _ = render()
        html, log = render(bullet_overrides={"blue_green.p4.en.0": None, "artelia.p4.en.+": "APPENDED BULLET"})
        bg_first = json.loads((PLUGIN / "data" / "cv-master.json").read_text(encoding="utf-8"))
        first = bg_first["experiences"]["blue_green"]["bullets"]["p4"]["t5"]["en"][0]
        self.assertIn(first, base)
        self.assertNotIn(first, html)
        self.assertIn("<li>APPENDED BULLET</li>", html)
        self.assertEqual(log, "")

    def test_a_key_for_another_cell_warns_instead_of_vanishing(self):
        _, log = render(bullet_overrides={"blue_green.p1.en.0": "x", "nobody.p4.en.0": "y", "bad": "z"})
        self.assertEqual(log.count("WARNING: --bullet-overrides key"), 3, log)


class TestContainerOverrides(unittest.TestCase):
    def test_items_replace_remove_append(self):
        html, log = render(container_items={"0.0": "REPLACED ITEM", "0.1": None, "2.+": "ADDED ITEM"})
        self.assertIn("<li>REPLACED ITEM</li>", html)
        self.assertIn("<li>ADDED ITEM</li>", html)
        self.assertNotIn("Python (FastAPI, Pydantic AI)", html)
        self.assertEqual(log, "")

    def test_containers_override_replaces_the_three_blocks(self):
        blocks = [{"title": f"BLOCK {i}", "items": [f"item {i}a", f"item {i}b"]} for i in range(3)]
        html, _ = render(containers_override=blocks)
        for i in range(3):
            self.assertIn(f"BLOCK {i}", html)
            self.assertIn(f"<li>item {i}a</li>", html)
        self.assertNotIn("Agent Platform &amp; Stack", html)
        self.assertNotIn("Agent Platform & Stack", html)

    def test_about_override_replaces_the_three_lines(self):
        html, _ = render(about_override=["L1", "L2", "L3"])
        for line in ("L1", "L2", "L3"):
            self.assertIn(f"<span>{line}</span>", html)
        self.assertNotIn("Forward Deployed Engineer who turns", html)


class TestFontAndEducation(unittest.TestCase):
    def test_bundled_font_is_an_absolute_file_url(self):
        html, _ = render()
        self.assertNotIn("{{FONT_DIR}}", html)
        font_dir = (PLUGIN / "assets" / "fonts").resolve().as_uri()
        for face in gen.FONT_FILES:
            self.assertIn(f"url('{font_dir}/{face}')", html)
            self.assertTrue((PLUGIN / "assets" / "fonts" / face).exists(), face)
        self.assertIn("font-family: 'CV Sans', 'CV Symbols', sans-serif;", html)

    def test_licences_ship_with_the_fonts(self):
        fonts = PLUGIN / "assets" / "fonts"
        self.assertIn("Apache License", (fonts / "LICENSE.txt").read_text(encoding="utf-8"))
        self.assertIn("Bitstream", (fonts / "LICENSE_DEJAVU.txt").read_text(encoding="utf-8"))

    def test_a_missing_face_stops_the_script(self):
        original = gen.FONT_FILES
        gen.FONT_FILES = original + ("Roboto-Missing.otf",)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as ctx:
                    gen.get_font_dir()
            self.assertEqual(ctx.exception.code, 1)
        finally:
            gen.FONT_FILES = original

    def test_education_uses_the_dash_separator(self):
        html, _ = render()
        self.assertIn('<span class="degree">DEA (Master\'s) in Oceanography, Climatology &amp; Environment</span> '
                      '<span class="school">— Université', html.replace("&amp;", "&").replace("& Environment</span>", "&amp; Environment</span>"))
        self.assertNotIn("Environment:</span>", html)


if __name__ == "__main__":
    unittest.main()
