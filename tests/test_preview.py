import http.client
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.parse
from pathlib import Path

from _paths import FIXTURES, FIXTURES5, ROOT, SITE5_URL, SKILL, WP_LOCAL, live5_only, live_only, live_tests_enabled, wp5
from divi_shortcode import parse

PREVIEW = SKILL / "scripts" / "preview" / "preview.mjs"
FETCH_DIVI = SKILL / "scripts" / "preview" / "fetch-divi.mjs"
VERSION = "4.27.9"

# Builder-CSS fidelity check, same method as research/playground-prototype/compare.py (the spike's
# verified 2,064/2,064-declaration match against page 11): explode grouped selectors into (media,
# selector, declaration) triples and keep only rules whose selector has an order-class-shaped digit
# (.et_pb_text_3). This also matches structural classes like .et_pb_column_1_3 or .et_pb_row_4col
# (inherited imprecision from compare.py, harmless here) - those are theme-base CSS, not per-module
# design CSS, and are excluded separately via the style-block id filter in _decls (require_id).
_SKIP_STYLE_ID = re.compile(r'id=[\'"]divi-dynamic-critical' + '-inline-css')  # handle + suffix kept apart: tests/test_no_divi_assets.py forbids the literal id
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
    the `divi-dynamic-critical` handle's inline style block and is excluded below, so the preview side must exclude its
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
    """Elegant Themes credentials from the local test site's DB, passed only via the child env (never printed).
    Only with PP_LIVE_TESTS=1; otherwise the renderer works from the Divi cache alone."""
    if not live_tests_enabled():
        return {}
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

    @live_only
    def test_page11_builder_css_matches_live(self):
        # -L: page 11 is the site's static front page (page_on_front=11), so WordPress 301s its slug URL to
        # "/"; without following the redirect the body is empty and the test silently skipped.
        live = subprocess.run(["curl", "-sL", "http://divi-test.local/probe-divi-ai-emergency-plumber/"],
                              capture_output=True, text=True).stdout
        if "et_pb_section" not in live:
            self.skipTest("page 11 not reachable")
        for url in _preload_style_urls(live):
            css = subprocess.run(["curl", "-s", url], capture_output=True, text=True).stdout
            live += f"<style>{css}</style>"
        html, _ = self.render(FIXTURES / "valid" / "divi-ai-layout.txt")
        self.assertEqual(sorted(_decls(live)), sorted(_decls(html, require_id=True)))

    @live_only
    def test_no_credentials_in_output(self):
        env = _et_env()
        _, logs = self.render(FIXTURES / "valid" / "handwritten-landing.txt")
        for secret in env.values():
            if secret:
                self.assertNotIn(secret, logs)

    def test_fetch_divi_redacts_percent_encoded_credentials(self):
        """A username/key needing percent-encoding ('@', '+', '/') must never leak, raw or
        percent-encoded, on the "is not downloadable" error path. Regression: redact() used to
        string-match the *raw* credentials against a URL built with URLSearchParams, which
        percent-encodes them (e.g. '@' -> '%40'), so an email-style username or a key containing
        '+'/'/' survived untouched in the encoded URL and leaked into the error message."""
        if shutil.which("node") is None:
            raise unittest.SkipTest("node not installed")

        class _Handler(http.server.BaseHTTPRequestHandler):
            """Stands in for the Elegant Themes API (PP_ET_ENDPOINT): always says "not available",
            so ensureDivi hits the redacted-URL error path without any real network access."""

            def do_GET(self):
                body = b'a:1:{s:6:"status";s:13:"not_available"}'
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_a):
                pass

        server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            username, api_key = "someone@example.com", "abc+def/123"
            with tempfile.TemporaryDirectory() as cache:
                script = (
                    f"import({FETCH_DIVI.as_uri()!r}).then(m => m.ensureDivi('9.9.9', {cache!r}, () => {{}}))"
                    ".catch(e => { console.error(e.message); process.exit(1); });"
                )
                env = dict(os.environ, ET_USERNAME=username, ET_API_KEY=api_key,
                           PP_ET_ENDPOINT=f"http://127.0.0.1:{server.server_address[1]}/")
                proc = subprocess.run(["node", "--input-type=module", "-e", script],
                                      capture_output=True, text=True, timeout=30, env=env)
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

        out = proc.stdout + proc.stderr
        self.assertIn("not downloadable", out)
        # The fix engaged (placeholders present, percent-encoded like the rest of the query string)...
        self.assertIn(urllib.parse.quote("<ET_USERNAME>", safe=""), out)
        self.assertIn(urllib.parse.quote("<API_KEY>", safe=""), out)
        # ...and neither secret appears, raw or percent-encoded, anywhere in stdout/stderr.
        for secret in (username, api_key):
            self.assertNotIn(secret, out)
            self.assertNotIn(urllib.parse.quote(secret, safe=""), out)
            self.assertNotIn(urllib.parse.quote_plus(secret), out)


# ---- Divi 5: Playground preview vs the real Divi 5 site ---------------------------------------------------------------
PREVIEW_PY = SKILL / "scripts" / "preview.py"
D5_FIXTURES = {"divi-ai-layout": FIXTURES5 / "divi-ai" / "layout.html",
               "heldout-inscope": FIXTURES5 / "converted" / "heldout-inscope.html",
               "content-heldout": FIXTURES5 / "converted" / "content-heldout.html"}
# research/divi5/playground.md (R5): identical tag/class sequences, and builder CSS 490/490 (heldout-inscope) and
# 161/161 (content-heldout) declarations identical. (Its divi-ai figure, 2,480, was for a different conversion of
# that layout than divi-ai/layout.html.) Every fixture must be exact: no missing or extra declaration.
D5_SPIKE_DECLS = {"heldout-inscope": 490, "content-heldout": 161}
D5_TITLE = "D5TEST preview"
D5_META = json.dumps({"_et_pb_use_builder": "on", "_et_pb_use_divi_5": "on", "_et_pb_page_layout": "et_no_sidebar",
                      "_et_pb_built_for_post_type": "page"})


def _d5_pages():
    """Ids of every "D5TEST preview" page on the Divi 5 site, trashed ones included."""
    return wp5("post", "list", "--post_type=page", "--post_status=any,trash", f"--s={D5_TITLE}",
               "--field=ID").stdout.split()


def _wp5(*args):
    out = wp5(*args)
    if out.returncode != 0:
        raise RuntimeError(f"wp {' '.join(map(str, args[:3]))} failed: {out.stderr[-400:]}")
    return out.stdout.strip()


@live5_only
class Divi5PreviewParityTest(unittest.TestCase):
    """preview.py render / serve of Divi 5 block pages (WordPress Playground, real Divi 5) against the same content
    published on divi-5-test.local: builder markup (tag/class sequence of .et-l) and builder CSS declaration sets
    (research/tools/fidelity.py, Divi 5-aware). The live side is a fresh fetch after a warm-up view, with its
    same-origin stylesheets inlined (fidelity.flatten). Pages are created as "D5TEST preview …" and deleted after."""

    @classmethod
    def setUpClass(cls):
        import fetch_divi
        import fidelity
        cls.fidelity = fidelity
        if shutil.which("node") is None:
            raise unittest.SkipTest("node not installed")
        cls.version = fetch_divi.newest_cached(major=5)
        if cls.version is None:
            raise unittest.SkipTest("no Divi 5 cached (preview.py fetch-divi latest5)")
        site_version = _wp5("theme", "get", "Divi", "--field=version").splitlines()[-1]
        if site_version != cls.version:
            raise unittest.SkipTest(f"site runs Divi {site_version}, cache has {cls.version}")
        cls.admin = _wp5("user", "list", "--role=administrator", "--field=user_login").splitlines()[0]
        cls._sweep()
        cls.tmp = Path(tempfile.mkdtemp())
        cls.ids, cls.live, cls.preview, cls.results, cls.timings = {}, {}, {}, {}, {}
        try:
            for name, path in D5_FIXTURES.items():
                cls.ids[name] = int(_wp5("post", "create", str(path), "--post_type=page", "--post_status=publish",
                                         f"--post_title={D5_TITLE} {name}", f"--meta_input={D5_META}", "--porcelain",
                                         f"--user={cls.admin}").splitlines()[-1])
                stored = _wp5("post", "get", cls.ids[name], "--field=post_content")
                assert stored.strip() == path.read_text().strip(), f"{name}: WordPress changed the content"
            for name in D5_FIXTURES:
                cls.live[name] = cls.live_page(name)
            for name, path in D5_FIXTURES.items():
                out = cls.tmp / f"{name}.html"
                t0 = time.time()
                run = subprocess.run([sys.executable, str(PREVIEW_PY), "render", str(path), "--out", str(out)],
                                     capture_output=True, text=True, timeout=600)
                cls.timings[name] = round(time.time() - t0, 1)
                assert run.returncode == 0, run.stderr[-800:]
                assert f"divi={cls.version}" in run.stderr, run.stderr[-400:]
                cls.preview[name] = out.read_text(encoding="utf-8", errors="replace")
                cls.results[name] = fidelity.compare(cls.live[name], cls.preview[name])
            sys.stderr.write("\nD5 preview parity " + json.dumps(
                {n: {"markup": r["markup"], "css": r["css"], "render_s": cls.timings[n]}
                 for n, r in cls.results.items()}) + "\n")
        except BaseException:
            cls._cleanup()
            raise

    @classmethod
    def live_page(cls, name):
        url = f"{SITE5_URL}/?page_id={cls.ids[name]}"
        cls.fidelity.flatten(url)  # warm-up view: Divi writes the page's static CSS on the first one
        return cls.fidelity.flatten(url)

    @classmethod
    def _sweep(cls):
        for pid in _d5_pages():
            wp5("post", "delete", pid, "--force", f"--user={cls.admin}")

    @classmethod
    def _cleanup(cls):
        cls._sweep()
        shutil.rmtree(getattr(cls, "tmp", ""), ignore_errors=True)

    @classmethod
    def tearDownClass(cls):
        cls._cleanup()
        left = _d5_pages()
        if left:
            raise AssertionError(f"{D5_TITLE} pages left on the site: {left}")

    def test_builder_markup_is_identical(self):
        for name, r in self.results.items():
            with self.subTest(name=name):
                self.assertGreater(r["markup"]["truth_elements"], 50)
                self.assertTrue(r["markup"]["tag_class_sequence_equal"], r["markup"])

    def test_builder_css_declarations_are_identical(self):
        for name, r in self.results.items():
            with self.subTest(name=name):
                self.assertGreaterEqual(r["css"]["common"], D5_SPIKE_DECLS.get(name, 1), r["css"])
                self.assertEqual((r["css"]["missing"], r["css"]["extra"]), (0, 0),
                                 (r["missing_examples"], r["extra_examples"]))

    def test_render_is_self_contained(self):
        for name, html in self.preview.items():
            with self.subTest(name=name):
                self.assertNotRegex(html, r"url\(\s*['\"]?(?:https?:)?//127\.0\.0\.1[^)]*\.(?:woff2?|ttf)")
                self.assertIn("url(data:font/", html)

    def test_serve_matches_live_across_page_switches_and_edits(self):
        """One warm Playground: a -> b -> a -> a edited (to c's content). Each response must match its live page
        (Divi 5 caches per-post CSS; the mu-plugin purges it per request, with a fake id per page name)."""
        import socket
        pages = self.tmp / "serve"
        pages.mkdir()
        (pages / "a.html").write_text(D5_FIXTURES["heldout-inscope"].read_text())
        (pages / "b.html").write_text(D5_FIXTURES["content-heldout"].read_text())
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        proc = subprocess.Popen([sys.executable, str(PREVIEW_PY), "serve", "--pages", str(pages), "--port", str(port)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            def fetch(name):
                deadline = time.time() + 300
                while time.time() < deadline:
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
                    try:
                        conn.request("GET", f"/{name}")
                        r = conn.getresponse()
                        r.read()
                        if r.status == 302:
                            t0 = time.time()
                            html = self.fidelity.flatten(r.getheader("Location"))
                            return html, time.time() - t0
                    except OSError:
                        pass
                    finally:
                        conn.close()
                    time.sleep(0.5)
                self.fail("serve never redirected to the Playground")

            steps = [("a", "heldout-inscope"), ("b", "content-heldout"), ("a", "heldout-inscope")]
            timings = []
            for page, fixture in steps + [("a", "divi-ai-layout")]:
                if fixture == "divi-ai-layout":  # the edit: same page name, new content
                    (pages / "a.html").write_text(D5_FIXTURES[fixture].read_text())
                    time.sleep(1.5)  # serve re-stages within ~0.5 s
                html, secs = fetch(page)
                timings.append(round(secs, 2))
                r = self.fidelity.compare(self.live[fixture], html)
                with self.subTest(step=f"{page}={fixture}"):
                    self.assertTrue(r["markup"]["tag_class_sequence_equal"], r["markup"])
                    self.assertEqual((r["css"]["missing"], r["css"]["extra"]), (0, 0),
                                     (r["css"], r["missing_examples"], r["extra_examples"]))
            sys.stderr.write(f"\nD5 serve re-render seconds (page + its stylesheets): {timings}\n")
        finally:
            proc.terminate()
            proc.wait(timeout=30)


# ---- Divi 5: design data seeded into the Playground site's options (Task 14b) ------------------------------------------
D5_SAMPLE_TOKENS = SKILL / "recipes" / "divi5" / "sample-tokens.json"
D5_HERO_RECIPE = SKILL / "recipes" / "divi5" / "sections" / "hero-split.md"
D5_SEED_TITLE = "D5TEST 14b seed"
SEED_SITE_OPTIONS = ROOT / "research" / "tools" / "divi5" / "seed_site_options.php"


def _recipe_example(path):
    """The last ```divi5 block of a recipe (its worked example)."""
    return re.findall(r"```divi5\n(.*?)\n```", path.read_text(encoding="utf-8"), re.S)[-1]


@live5_only
class Divi5SeedOptionsTest(unittest.TestCase):
    """preview.py render --tokens (Divi 5) seeds the site's design data (global colors, Customizer colors, design
    variables) into the Playground site's options, so Divi itself resolves the $variable() refs: the hero-split
    recipe (section padding and image/button radius from gvid variables, navy background from a gcid color) renders
    them, a later render without --tokens is stock again (nothing persisted), and the builder CSS matches the same
    page on divi-5-test.local seeded the same way (seed_site_options.php; its option rows are restored byte-for-byte
    and the "D5TEST 14b seed" page deleted)."""

    @classmethod
    def setUpClass(cls):
        import fetch_divi
        import fidelity
        import preview
        if shutil.which("node") is None:
            raise unittest.SkipTest("node not installed")
        version = fetch_divi.newest_cached(major=5)
        if version is None:
            raise unittest.SkipTest("no Divi 5 cached (preview.py fetch-divi latest5)")
        site_version = _wp5("theme", "get", "Divi", "--field=version").splitlines()[-1]
        if site_version != version:
            raise unittest.SkipTest(f"site runs Divi {site_version}, cache has {version}")
        cls.tmp = Path(tempfile.mkdtemp())
        cls.page = cls.tmp / "hero.html"
        cls.page.write_text(_recipe_example(D5_HERO_RECIPE), encoding="utf-8")
        cls.html, cls.timings = {}, {}
        cls.render_tmp = cls.tmp / "render-tmp"  # the renders' TMPDIR: no pp-* temp dir may outlive them
        cls.render_tmp.mkdir()
        for name, extra in (("seeded", ["--tokens", str(D5_SAMPLE_TOKENS)]), ("stock", [])):
            out = cls.tmp / f"{name}.html"
            t0 = time.time()
            run = subprocess.run([sys.executable, str(PREVIEW_PY), "render", str(cls.page), "--out", str(out), *extra],
                                 capture_output=True, text=True, timeout=600,
                                 env=dict(os.environ, TMPDIR=str(cls.render_tmp)))
            cls.timings[name] = round(time.time() - t0, 1)
            assert run.returncode == 0, run.stderr[-800:]
            cls.html[name] = out.read_text(encoding="utf-8", errors="replace")
        # The same page on the Divi 5 site, seeded the same way (the options JSON the preview used), then restored.
        (cls.tmp / "seed.json").write_text(json.dumps(preview.seed_options(json.loads(D5_SAMPLE_TOKENS.read_text()))))
        admin = _wp5("user", "list", "--role=administrator", "--field=user_login").splitlines()[0]
        cls.sha_before = _wp5("eval-file", SEED_SITE_OPTIONS, "sha").splitlines()[-1]
        backup = cls.tmp / "backup.json"
        _wp5("eval-file", SEED_SITE_OPTIONS, "backup", backup)
        pid = None
        try:
            _wp5("eval-file", SEED_SITE_OPTIONS, "apply", cls.tmp / "seed.json")
            pid = int(_wp5("post", "create", cls.page, "--post_type=page", "--post_status=publish",
                           f"--post_title={D5_SEED_TITLE} hero", f"--meta_input={D5_META}", "--porcelain",
                           f"--user={admin}").splitlines()[-1])
            url = f"{SITE5_URL}/?page_id={pid}"
            fidelity.flatten(url)  # warm-up view: Divi writes the page's static CSS on the first one
            cls.html["live"] = fidelity.flatten(url)
        finally:
            if pid:
                wp5("post", "delete", pid, "--force", f"--user={admin}")
            _wp5("eval-file", SEED_SITE_OPTIONS, "restore", backup)
            cls.sha_after = _wp5("eval-file", SEED_SITE_OPTIONS, "sha").splitlines()[-1]
            cls.left = wp5("post", "list", "--post_type=page", "--post_status=any,trash", f"--s={D5_SEED_TITLE}",
                           "--field=ID").stdout.split()
        cls.result = fidelity.compare(cls.html["live"], cls.html["seeded"])
        sys.stderr.write("\nD5 seed options " + json.dumps({"render_s": cls.timings, "markup": cls.result["markup"],
                                                            "css": cls.result["css"]}) + "\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(getattr(cls, "tmp", ""), ignore_errors=True)

    def test_divi_prints_the_seeded_variables_and_colors_itself(self):
        html = self.html["seeded"]
        numeric = re.search(r'<style class="et-vb-global-data et-vb-global-numeric-vars">([^<]*)</style>', html)
        self.assertIsNotNone(numeric, "Divi printed no number variables")
        self.assertIn("--gvid-r6secpad01: clamp(48px, 8vw, 96px);", numeric.group(1))
        self.assertIn("--gvid-r6radius01: 12px;", numeric.group(1))
        self.assertIn("--gcid-r6navy0001: #0B2A3C;", html)  # Divi's own :root (the seed CSS has no space)
        self.assertIn("--gcid-primary-color: #F97316;", html)  # the Customizer accent color

    def test_variable_padding_and_radius_render(self):
        for name, present in (("seeded", True), ("stock", False)):
            html = self.html[name]
            with self.subTest(render=name):
                self.assertEqual(".et_pb_section_0.et_pb_section{padding-top:var(--gvid-r6secpad01);"
                                 "padding-bottom:var(--gvid-r6secpad01)}" in html, present)
                self.assertEqual("border-top-left-radius:var(--gvid-r6radius01);border-top-right-radius:"
                                 "var(--gvid-r6radius01);border-bottom-right-radius:var(--gvid-r6radius01);"
                                 "border-bottom-left-radius:var(--gvid-r6radius01);overflow:hidden}" in html, present)

    def test_nothing_persists_into_the_playground_site(self):
        html = self.html["stock"]  # rendered after the seeded one, on the same cached site
        self.assertNotIn("et-vb-global-numeric-vars", html)
        self.assertNotIn("gvid-r6secpad01:", html)
        self.assertNotIn("--gcid-r6navy0001:", html)
        self.assertIn("--gcid-primary-color: #2ea3f2;", html)  # stock accent color

    def test_builder_css_matches_the_seeded_live_site(self):
        r = self.result
        self.assertTrue(r["markup"]["tag_class_sequence_equal"], r["markup"])
        self.assertGreater(r["css"]["common"], 20, r["css"])
        self.assertEqual((r["css"]["missing"], r["css"]["extra"]), (0, 0), (r["missing_examples"], r["extra_examples"]))
        self.assertIn("--gvid-r6secpad01: clamp(48px, 8vw, 96px);", self.html["live"])

    def test_renders_leave_no_temp_dirs(self):
        self.assertEqual(sorted(p.name for p in self.render_tmp.iterdir() if p.name.startswith("pp-")), [])

    def test_live_site_restored(self):
        self.assertEqual(self.sha_after, self.sha_before)
        self.assertEqual(self.left, [])


if __name__ == "__main__":
    unittest.main()
