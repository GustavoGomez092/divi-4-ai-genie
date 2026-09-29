"""Divi 5 token fidelity end to end, against the local Divi 5 site (divi-5-test.local). Opt-in: PP_LIVE_TESTS=1 and
the site running (@live5_only).

research/tools/divi5/fidelity_setup.php seeds known design data (3 global colors, one derived; a number and a font
variable; a module preset on divi/button; a divi/font option-group preset on the heading title) and a source page
using them all plus a literal responsive h2 and a custom class. extract_tokens.py then runs over REST and must recover
every known value exactly. A page composed from those tokens only (exemplar section/row/column, a heading with the
recovered group preset, the button's recovered style bundle) must validate clean against them, go up with
`publish.py draft`, and render the same preset and module CSS as the source page.

The touched options are backed up (raw rows) before anything changes and restored byte-for-byte in tearDownClass;
the "D5TEST fidelity" pages and the throwaway Application Password are deleted. A backup left by an interrupted run is
restored first (setUpClass sweep).
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path

from _paths import SCRIPTS, SITE5_URL, TOOLS5, live5_only, wp5

sys.path.insert(0, str(SCRIPTS))
import divi5_blocks  # noqa: E402
from tokens5_from_html import _css, _decls, _walk_css, stylesheet_links, tokens5_from_html  # noqa: E402

SETUP = TOOLS5 / "fidelity_setup.php"
BACKUP = Path(tempfile.gettempdir()) / "divi-genie-d5-tokens-fidelity-backup.json"
APP_NAME = "d5-tokens-fidelity-test"
BUTTON_PRESET, FONT_PRESET = "d5fbtnpreset1", "d5ffontpreset1"
NAVY, CORAL, CORAL_LIGHT = "gcid-d5fnavy0001", "gcid-d5fcoral001", "gcid-d5fcorallt1"
RADIUS, FONT = "gvid-d5fradius01", "gvid-d5ffont0001"
TOKEN_CODES = {"W5_UNKNOWN_PRESET", "W5_UNKNOWN_VARIABLE", "W_OFF_PALETTE_COLOR", "W_OFF_BRAND_FONT",
               "W_OFF_SCALE_SPACING"}
# Divi's feature caches: deleted when the design data changes, rebuilt (or dropped) by any later request.
VOLATILE_OPTIONS = {"_et_builder_da_feature_cache", "_et_builder_gf_feature_cache"}
VAR_RE = re.compile(r"var\(--([\w-]+)(?:,[^()]*)?\)")


def _wp(*args):
    out = wp5(*args)
    if out.returncode != 0:
        raise RuntimeError(f"wp {' '.join(map(str, args[:3]))} failed: {out.stderr[-400:]}")
    return out.stdout.strip()


def _setup_php(*args):
    return json.loads(_wp("eval-file", SETUP, *args).splitlines()[-1])


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "divi-genie-test"}),
                                timeout=120) as resp:
        return resp.read().decode("utf-8", "replace")


def _page_css(url):
    """(html, css_by_url) of a public page with its same-origin et-cache stylesheets. Second hit: Divi builds the
    page's static CSS on the first view."""
    _get(url)
    html = _get(url)
    return html, {link: _get(link) for link in stylesheet_links(html, url)}


def _rules(html, css_by_url, needle):
    """[(media, selector, declarations)] of every style rule whose selector matches `needle` (a regex)."""
    pat = re.compile(needle)
    return [(m, " ".join(sel.split()), _decls(body)) for m, sel, body in _walk_css(_css(html, css_by_url))
            if pat.search(sel)]


def _root(html, css_by_url):
    root = {}
    for media, sel, body in _walk_css(_css(html, css_by_url)):
        if media is None and sel == ":root":
            root.update({k[2:]: v for k, v in _decls(body).items() if k.startswith("--")})
    return root


def _computed(decls, root):
    """Declarations with every var(--x) replaced by the page's :root value (recursively)."""
    def sub(value, depth=0):
        if depth > 5:
            return value
        new = VAR_RE.sub(lambda m: root.get(m.group(1), m.group(0)), value)
        return new if new == value else sub(new, depth + 1)
    return {k: sub(v) for k, v in decls.items()}


@live5_only
class Divi5TokensFidelityTest(unittest.TestCase):
    @classmethod
    def _sweep(cls):
        """Undo an interrupted earlier run: its backup, its pages, its Application Password."""
        if BACKUP.exists():
            _setup_php("restore", BACKUP)
            BACKUP.unlink()
        for pid in wp5("post", "list", "--post_type=page", "--post_status=any", "--s=D5TEST fidelity",
                       "--field=ID").stdout.split():
            wp5("post", "delete", pid, "--force")
        for uuid in wp5("user", "application-password", "list", cls.admin, f"--name={APP_NAME}",
                        "--field=uuid").stdout.split():
            wp5("user", "application-password", "delete", cls.admin, uuid)

    @classmethod
    def setUpClass(cls):
        cls.admin = _wp("user", "list", "--role=administrator", "--field=user_login").splitlines()[0]
        cls._sweep()
        cls.before = _setup_php("snapshot")
        cls.tmp = Path(tempfile.mkdtemp())
        try:
            cls.password = _wp("user", "application-password", "create", cls.admin, APP_NAME, "--porcelain")
            cls.keys = cls.tmp / "keys.json"  # never the user's own keys.json
            cls.keys.write_text(json.dumps({"keys": []}))
            src = _setup_php("setup", BACKUP)
            cls.src_id, cls.src_url = src["page_id"], src["url"]
            cls.tokens_path = cls.tmp / "tokens.json"
            run = cls.script("extract_tokens.py", "--site", SITE5_URL, "--user", cls.admin, "--page", cls.src_id,
                             "--out", cls.tokens_path)
            if run.returncode != 0:
                raise RuntimeError(f"extract_tokens.py failed: {run.stderr[-600:]}")
            cls.extract_stderr = run.stderr
            cls.tokens = json.loads(cls.tokens_path.read_text())
        except BaseException:
            cls._restore()
            raise

    @classmethod
    def _restore(cls):
        problems = []
        if BACKUP.exists():
            try:
                cls.restored = _setup_php("restore", BACKUP)
                BACKUP.unlink()
            except Exception as exc:  # keep the backup for the next run's sweep
                problems.append(f"restore failed, backup kept at {BACKUP}: {exc}")
        for uuid in wp5("user", "application-password", "list", cls.admin, f"--name={APP_NAME}",
                        "--field=uuid").stdout.split():
            wp5("user", "application-password", "delete", cls.admin, uuid)
        shutil.rmtree(cls.tmp, ignore_errors=True)
        return problems

    @classmethod
    def tearDownClass(cls):
        problems = cls._restore()
        after = _setup_php("snapshot")
        if after["touched"] != cls.before["touched"]:
            problems.append(f"touched options differ after restore: {cls.before['touched']} -> {after['touched']}")
        changed = sorted(k for k in set(after["all"]) | set(cls.before["all"])
                         if k not in VOLATILE_OPTIONS and after["all"].get(k) != cls.before["all"].get(k))
        if changed:
            problems.append(f"options changed by the run: {changed}")
        left = wp5("post", "list", "--post_type=page", "--post_status=any", "--s=D5TEST fidelity",
                   "--field=ID").stdout.split()
        if left:
            problems.append(f"D5TEST fidelity pages left: {left}")
        if problems:
            raise AssertionError("; ".join(problems))

    @classmethod
    def script(cls, name, *args):
        env = dict(os.environ, WP_APP_PASSWORD=cls.password, DIVI_KEYS_FILE=str(cls.keys))
        run = subprocess.run([sys.executable, str(SCRIPTS / name), *map(str, args)], capture_output=True, text=True,
                             env=env, timeout=300, cwd=cls.tmp)
        if cls.password in run.stdout + run.stderr:
            raise AssertionError(f"{name} printed the Application Password")
        return run

    # ---- the extracted tokens reproduce the seeded values -------------------------------------------------------

    def test_site_and_source_page(self):
        s = self.tokens["site"]
        self.assertEqual((s["divi_major"], s["divi_version"], s["content_format"]), (5, "5.13.1", "blocks"))
        self.assertEqual(s["source_pages"], [{"id": self.src_id, "url": self.src_url, "format": "blocks"}])
        self.assertNotIn("warning", self.extract_stderr)

    def test_global_colors_resolved(self):
        g = self.tokens["colors"]["global"]
        self.assertEqual(g[NAVY]["value"], "#102A43")
        self.assertEqual(g[NAVY]["uses"], 1)  # the text color; the font preset's use is not in content
        self.assertEqual(g[CORAL]["value"], "#E4572E")
        self.assertEqual(g[CORAL]["uses"], 0)  # reached only through the button preset
        self.assertEqual((g[CORAL_LIGHT]["value"], g[CORAL_LIGHT]["base"]), ("#f3b29f", CORAL))  # HSL l + 25
        self.assertEqual(g[CORAL_LIGHT]["roles"], ["module.decoration.background.color"])

    def test_variables(self):
        v = self.tokens["variables"]
        self.assertEqual((v[RADIUS]["value"], v[RADIUS]["kind"]), ("10px", "numbers"))
        self.assertEqual((v[FONT]["value"], v[FONT]["kind"]), ("Montserrat", "fonts"))
        self.assertIn("Montserrat", self.tokens["typography"]["loaded_fonts"])

    def test_module_preset_css(self):
        (btn,) = self.tokens["presets"]["divi/button"]
        self.assertEqual((btn["id"], btn["uses"]), (BUTTON_PRESET, 1))
        radius = f"var(--{RADIUS})"
        self.assertEqual(btn["css"]["declarations"], {
            "background-color": f"var(--{CORAL})", "color": "#ffffff",
            "border-top-left-radius": radius, "border-top-right-radius": radius,
            "border-bottom-right-radius": radius, "border-bottom-left-radius": radius})
        self.assertIn({"selector": f"body #page-container .et_pb_section .preset--module--divi-button--{BUTTON_PRESET}"
                                   ":after", "declarations": {"font-size": "1.6em"}}, btn["css"]["rules"])

    def test_group_preset_css(self):
        (font,) = self.tokens["group_presets"]["divi/font"]
        self.assertEqual((font["id"], font["uses"], font["module"], font["group_id"]),
                         (FONT_PRESET, 1, "divi/heading", "designTitleText"))
        self.assertEqual(font["css"]["declarations"], {"font-family": f"var(--{FONT})", "font-weight": "700",
                                                       "color": f"var(--{NAVY})", "font-size": "48px"})

    def test_typography_scale_with_tablet_and_phone(self):
        h2 = self.tokens["typography"]["scale"]["h2"]
        self.assertEqual((h2["size"], h2["size_tablet"], h2["size_phone"], h2["weight"], h2["uses"]),
                         ("40px", "32px", "26px", "600", 1))
        self.assertNotIn("h1", self.tokens["typography"]["scale"])  # the preset heading has no inline font

    def test_custom_class_and_section_spacing(self):
        (bundle,) = self.tokens["module_styles"]["divi/button"]
        self.assertEqual((bundle["html_attributes"], bundle["module_preset"]), ({"class": "d5f-cta"}, [BUTTON_PRESET]))
        pad = self.tokens["spacing"]["section_padding"]
        self.assertEqual(pad, [[{"top": "72px", "right": "", "bottom": "72px", "left": ""}, 1]])

    # ---- a page composed from the tokens renders like the source ------------------------------------------------

    def compose(self):
        """A section/row/column from the source's exemplar, a heading with the recovered group preset and the
        button's recovered style bundle: every id and value comes from tokens.json."""
        t = self.tokens
        ver = t["site"]["divi_version"]
        section = t["section_exemplars"][0]
        row = section["children"][0]
        column = row["children"][0]
        (font,) = t["group_presets"]["divi/font"]
        (bundle,) = t["module_styles"]["divi/button"]
        heading = divi5_blocks.new_block("heading", {
            "builderVersion": ver, "title": {"innerContent": {"desktop": {"value": "Composed from tokens"}}},
            "groupPreset": {font["group_id"]: {"presetId": [font["id"]], "groupName": "divi/font"}}})
        button_attrs = dict(copy.deepcopy(bundle["attrs"]), builderVersion=ver, modulePreset=bundle["module_preset"])
        button = divi5_blocks.new_block("button", button_attrs)
        divi5_blocks.set_attr(button, "module.advanced.htmlAttributes", dict(bundle["html_attributes"]))
        divi5_blocks.set_attr(button, "button.innerContent", {"text": "Go", "linkUrl": "#go"})

        def outer(ex, kids):
            return divi5_blocks.new_block(ex["name"], dict(copy.deepcopy(ex["attrs"]), builderVersion=ver), kids)
        page = outer(section, [outer(row, [outer(column, [heading, button])])])
        return divi5_blocks.serialize(divi5_blocks.wrap_placeholder([page]))

    def test_composed_page_reproduces_the_preset_styling(self):
        page = self.tmp / "composed.html"
        page.write_text(self.compose(), encoding="utf-8")

        # validate against the extracted tokens: no errors, no unknown ids, nothing off-token
        run = self.script("validate.py", page, "--tokens", self.tokens_path, "--json")
        report = json.loads(run.stdout)
        self.assertEqual(report["errors"], 0, run.stdout)
        self.assertFalse({f["code"] for f in report["findings"]} & TOKEN_CODES, run.stdout)

        # push it with publish.py draft, then make it public to read its rendered CSS
        run = self.script("publish.py", "draft", page, "--title", "D5TEST fidelity copy", "--tokens",
                          self.tokens_path, "--site", SITE5_URL, "--user", self.admin)
        self.assertEqual(run.returncode, 0, run.stderr)
        copy_id = json.loads(run.stdout)["id"]
        run = self.script("publish.py", "publish", "--page-id", copy_id, "--yes", "--site", SITE5_URL,
                          "--user", self.admin)
        self.assertEqual(run.returncode, 0, run.stderr)
        copy_url = json.loads(run.stdout)["link"]

        src_html, src_css = _page_css(self.src_url)
        new_html, new_css = _page_css(copy_url)

        # the markup carries the same preset class and custom class
        self.assertRegex(new_html, rf'<a class="[^"]*\bet_pb_button_0\b[^"]*\bd5f-cta\b[^"]*'
                                   rf'\bpreset--module--divi-button--{BUTTON_PRESET}\b')

        # the preset-- rules, and the module's own printed CSS, are identical on both pages
        for needle in (rf"preset--module--divi-button--{BUTTON_PRESET}\b", r"\.et_pb_button_0(?![\w-])",
                       rf"preset--group--divi-heading--divi-font--\w+--{FONT_PRESET}\b"):
            with self.subTest(rules=needle):
                src_rules = _rules(src_html, src_css, needle)
                self.assertTrue(src_rules)
                self.assertEqual(_rules(new_html, new_css, needle), src_rules)

        # and so are the computed declarations of the preset rule, var() references resolved per page
        src_p = tokens5_from_html(src_html, src_css)["presets_css"][BUTTON_PRESET]
        new_p = tokens5_from_html(new_html, new_css)["presets_css"][BUTTON_PRESET]
        computed = _computed(new_p["declarations"], _root(new_html, new_css))
        self.assertEqual(computed, _computed(src_p["declarations"], _root(src_html, src_css)))
        self.assertEqual(computed, {"background-color": "#E4572E", "color": "#ffffff",
                                    **{f"border-{c}-radius": "10px"
                                       for c in ("top-left", "top-right", "bottom-right", "bottom-left")}})
        font = tokens5_from_html(new_html, new_css)["presets_css"][FONT_PRESET]
        self.assertEqual(_computed(font["declarations"], _root(new_html, new_css)),
                         {"font-family": "'Montserrat'", "font-weight": "700", "color": "#102A43",
                          "font-size": "48px"})


if __name__ == "__main__":
    unittest.main()
