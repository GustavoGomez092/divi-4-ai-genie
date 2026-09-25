import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SKILL, WP_LOCAL
from divi_shortcode import parse

PREVIEW = SKILL / "scripts" / "preview" / "preview.mjs"
VERSION = "4.27.9"

# Builder-CSS fidelity check, same method as research/playground-prototype/compare.py (the spike's
# verified 2,064/2,064-declaration match against page 11): explode grouped selectors into (media,
# selector, declaration) triples and keep only rules whose selector has a module *order class*
# (.et_pb_text_3, not the structural .et_pb_column_1_3 or .et_pb_row_4col).
_SKIP_STYLE_ID = re.compile(r'id=[\'"]divi-dynamic-critical-inline-css')
_ORDER = re.compile(r'\.et_pb_[a-z_]+?_\d+(?![\d_])')


def _preload_style_urls(html):
    """<link rel=preload as=style> stylesheets a browser swaps in via onload once idle. A plain curl of
    the live page never fetches them, so the deferred/dynamic module-design CSS they hold (everything
    below the fold) is missing unless fetched and appended separately, as the spike's comparison did."""
    return re.findall(r'<link\b[^>]*rel=[\'"]preload[\'"][^>]*as=[\'"]style[\'"][^>]*href=[\'"]([^\'"]+)[\'"]', html)


def _decls(html, require_id=False):
    """Set of 'media | selector { declaration }' strings for builder-authored rules.

    require_id=True additionally drops anonymous <style> blocks. `render --out` (via &inline=1) turns
    every local <link rel=stylesheet> into an id-less <style> tag so the file is self-contained; those
    blocks hold Divi's theme-base CSS (row/column layout, shared across every module type, identical to
    the live theme by construction). The live page's equivalent chunk is inlined under
    id="divi-dynamic-critical-inline-css" and is excluded below, so the preview side must exclude its
    id-less counterpart the same way to compare only per-module design CSS on both sides.
    """
    out = set()
    for attrs, body in re.findall(r'<style([^>]*)>(.*?)</style>', html, re.S):
        if _SKIP_STYLE_ID.search(attrs):
            continue
        if require_id and not re.search(r'\bid=', attrs):
            continue
        css = re.sub(r'/\*.*?\*/', '', body, flags=re.S)
        media = ''
        for tok in re.finditer(r'(@media[^{]*)\{|([^{}]+)\{([^{}]*)\}|\}', css):
            if tok.group(1):
                media = re.sub(r'\s+', ' ', tok.group(1)).strip()
                continue
            if tok.group(0) == '}':
                media = ''
                continue
            sels, decl_body = tok.group(2), tok.group(3)
            if not _ORDER.search(sels):
                continue
            for sel in sels.split(','):
                sel = re.sub(r'\s+', ' ', sel).strip()
                if not _ORDER.search(sel):
                    continue
                for d in decl_body.split(';'):
                    d = re.sub(r'\s*:\s*', ':', re.sub(r'\s+', ' ', d).strip(), count=1)
                    if d:
                        out.add(f'{media} | {sel} {{ {d} }}')
    return out


def _et_env():
    """Elegant Themes credentials from the local test site's DB, passed only via the child env (never printed)."""
    out = subprocess.run([str(WP_LOCAL), "option", "get", "et_automatic_updates_options", "--format=json"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return {}
    import json
    data = json.loads(out.stdout[out.stdout.index("{"):])
    return {"ET_USERNAME": data.get("username", ""), "ET_API_KEY": data.get("api_key", "")}


def node(*args, timeout=600):
    if shutil.which("node") is None:
        raise unittest.SkipTest("node not installed")
    env = dict(os.environ, **_et_env())
    return subprocess.run(["node", str(PREVIEW), *args], capture_output=True, text=True, timeout=timeout, env=env)


class PreviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        warm = node("fetch-divi", VERSION)
        if warm.returncode != 0:
            raise unittest.SkipTest(f"Divi {VERSION} not cached and not fetchable: {warm.stderr[-300:]}")

    def render(self, path, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.html"
            proc = node("render", str(path), "--out", str(out), "--divi", VERSION, *extra)
            self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
            return out.read_text(), proc.stdout + proc.stderr

    def test_doctor(self):
        proc = node("doctor")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn(VERSION, proc.stdout)

    def test_fixtures_render_every_section(self):
        for name in ("handwritten-landing.txt", "brand-kit.txt", "unicode.txt"):
            path = FIXTURES / "valid" / name
            html, _ = self.render(path)
            self.assertIn('class="et-l', html, name)
            sections = len(parse(path.read_text()).sections())
            self.assertEqual(len(re.findall(r'class="[^"]*\bet_pb_section\b', html)), sections, name)

    def test_tokens_select_divi_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "o.html"
            proc = node("render", str(FIXTURES / "valid" / "handwritten-landing.txt"), "--out", str(out),
                        "--tokens", str(FIXTURES / "tokens-min.json"))
            self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
            self.assertIn(VERSION, proc.stdout + proc.stderr)

    def test_page11_builder_css_matches_live(self):
        live = subprocess.run(["curl", "-s", "http://divi-test.local/probe-divi-ai-emergency-plumber/"],
                              capture_output=True, text=True).stdout
        if "et_pb_section" not in live:
            self.skipTest("page 11 not reachable")
        for url in _preload_style_urls(live):
            css = subprocess.run(["curl", "-s", url], capture_output=True, text=True).stdout
            live += f"<style>{css}</style>"
        html, _ = self.render(FIXTURES / "valid" / "divi-ai-layout.txt")
        self.assertEqual(sorted(_decls(live)), sorted(_decls(html, require_id=True)))

    def test_no_credentials_in_output(self):
        env = _et_env()
        _, logs = self.render(FIXTURES / "valid" / "handwritten-landing.txt")
        for secret in env.values():
            if secret:
                self.assertNotIn(secret, logs)


if __name__ == "__main__":
    unittest.main()
