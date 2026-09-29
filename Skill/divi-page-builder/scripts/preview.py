#!/usr/bin/env python3
"""Divi page preview: Divi 4 shortcode pages with the pure-Python renderer (stdlib only, no Node, PHP or
WordPress); Divi 5 block pages on the real Divi 5 theme in WordPress Playground (needs Node 20+).

  python3 preview.py render PAGE [--out FILE] [--tokens tokens.json | --divi VER] [--no-js] [--exact] [--keys PATH]
      Writes one standalone HTML file (Divi's CSS/JS inlined, icon fonts and theme images as data:
      URIs, so it works opened from disk or over HTTP) and prints the coverage summary: modules the
      Python renderer doesn't support (--exact renders them), content that needs the live site's
      data (posts, menus, media, comments, widgets: neither preview has it, so check the WordPress
      draft preview) and attributes it ignored. Default --out: <page name>.html (<page name>.preview.html
      when that is the page itself).
      A Divi 5 block page (<!-- wp:divi/... --> markup, in a .txt or .html file) always renders in
      Playground, like --exact: local images inlined, and with --tokens the site's recovered global
      colors, variables and preset CSS seeded: into the Playground site's options for that render (see
      seed_options) and as CSS (see seed_css).
  python3 preview.py serve [--pages DIR] [--port 8765] [--tokens tokens.json | --divi VER] [--no-js] [--exact] [--keys PATH]
      Serves http://127.0.0.1:PORT/<name> for every DIR/<name>.txt (and every DIR/<name>.html holding
      Divi 5 blocks). Shortcode pages are re-rendered on each request, poll for edits and reload
      themselves; Divi's fonts/images/JS come from /__divi/... Pages with unsupported modules or
      site-data content show a banner saying which preview can show them. Block pages redirect to one
      warm Divi 5 Playground that re-renders them on every reload (edits are picked up within ~0.5 s);
      --tokens is read once, at start, and seeds every block page of the session.
  python3 preview.py doctor [--keys PATH]
      Reports Python, the cache dir, cached Divi versions (and whether a Divi 5 is cached), whether
      Node is present (only needed for --exact and Divi 5 block pages) and whether Elegant Themes
      credentials are available and from where (env / keys.json / none).
  python3 preview.py fetch-divi VER [--keys PATH]
      Downloads and caches a Divi version (the only command that always needs ET credentials).
      VER: 4.27.9, 5.13.1, latest (the newest Divi 4) or latest5 (the newest Divi 5).

Elegant Themes credentials, wherever a version isn't cached and must be downloaded (fetch-divi,
and render/serve/doctor when they fall through to a download): env ET_USERNAME + ET_API_KEY win
when both are set; otherwise the keys.json file's "elegant_themes" section (--keys PATH, else env
DIVI_KEYS_FILE, else ~/.config/divi-page-builder/keys.json) -- see wp_keys.resolve_et_credentials.
--exact hands the same resolved credentials to the preview.mjs child through its environment.

--exact runs the same command on the real-Divi preview (node scripts/preview/preview.mjs on
WordPress Playground) for pages the Python renderer can't reproduce. It needs Node 20+.

Divi version (render/serve): --divi, else --tokens (site.divi_version), else the newest cached
version of the page's major (Divi 4 for shortcode, Divi 5 for blocks: a cached Divi 5 is never
used for a shortcode page, or the reverse), else "latest" / "latest5". An empty site.divi_version
falls through to the next rule (with a note). A cached version never triggers an Elegant Themes API call.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import divi_format  # noqa: E402
import fetch_divi  # noqa: E402
import local_media  # noqa: E402
import wp_keys  # noqa: E402

PREVIEW_MJS = HERE / "preview" / "preview.mjs"
DIVI_ROUTE = "/__divi/"
LOCAL_ROUTE = "/__local/"
NODE_MIN_MAJOR = 20
NODE_GUIDANCE = ("--exact needs Node 20+ (it runs the real Divi theme on WordPress Playground via "
                 "scripts/preview/preview.mjs). Install Node from https://nodejs.org/ or drop --exact to "
                 "use the Python preview.")
RELOAD_JS = """<script>(function(){var m=null;setInterval(function(){fetch('/__mtime/%s',{cache:'no-store'})
.then(function(r){return r.text()}).then(function(t){if(m===null){m=t}else if(t!==m){location.reload()}})
.catch(function(){})},1000)})();</script>"""
BANNER = ('<div id="pp-preview-banner" style="position:fixed;z-index:999999;left:0;right:0;bottom:0;padding:8px 14px;'
          'background:#e11d48;color:#fff;font:13px/1.4 -apple-system,Segoe UI,sans-serif">%s</div>')
BANNER_EXACT = "Not rendered by the Python preview: %s. For the exact preview: add --exact."
# Unsupported features whose exact rendering also needs the network (like web fonts and images).
FEATURE_NOTES = {"video_oembed": "YouTube/Vimeo embeds come from oEmbed over the network; --exact shows the real "
                                 "embed when it has network"}
BANNER_SITE = ("Needs the live site's data: %s. Neither preview can show it (the --exact preview is a fresh "
               "WordPress with no posts, menus or media); check the WordPress draft preview.")
SITE_DATA_HINT = ("needs the live site's data (placeholders; neither preview can show posts, menus, media, "
                  "comments or widgets, check the WordPress draft preview): ")


class UsageError(Exception):
    pass


# ----------------------------------------------------------------------------- shared
def resolve_divi_version(divi: str | None, tokens: str | None, major: int = 4) -> str:
    """--divi, else --tokens (site.divi_version), else the newest cached version of Divi `major` (the page's
    format: 4 for shortcode, 5 for blocks), else 'latest' / 'latest5'. A cached Divi 5 is never picked for
    Divi 4 content, or the reverse; explicit --divi/--tokens always win (callers check the major)."""
    def fallback() -> str:
        return fetch_divi.newest_cached(major=major) or ("latest5" if major == 5 else "latest")

    if divi:
        return divi
    if tokens:
        try:
            data = json.loads(Path(tokens).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise UsageError(f"cannot read {tokens}: {e}") from None
        site = (data.get("site") or {}) if isinstance(data, dict) else {}
        if "divi_version" not in site:
            raise UsageError(f"No site.divi_version in {tokens}")
        version = site.get("divi_version")
        if version:
            return version
        version = fallback()
        label = "the newest cached Divi" + (" 5" if major == 5 else "")  # the Divi 4 note is unchanged
        print(f"note: site.divi_version is empty in {tokens}; using "
              f"{version if version.startswith('latest') else label + ', ' + version}", file=sys.stderr)
        return version
    return fallback()


def version_major(version: str) -> int | None:
    """4/5 for a version or latest alias; None when unknown."""
    alias = fetch_divi.latest_major(version)
    if alias:
        return alias
    head = version.split(".")[0]
    return int(head) if head.isdigit() else None


def is_blocks(text: str) -> bool:
    """Divi 5 block content (Playground renders it; the Python renderer is Divi 4 only)."""
    return divi_format.detect_content(text) in ("blocks", "mixed")


D4_ONLY = ("the Python preview renders Divi 4 only, and this page is Divi 4 shortcode but the Divi version is "
           "{v}. Preview it with --divi 4.x (or no --divi/--tokens), add --exact to render it through Divi 5's "
           "shortcode compatibility layer, or convert the page to Divi 5 blocks (what a Divi 5 site stores)")
D5_ONLY = ("this page is Divi 5 block markup, which needs a Divi 5 theme, but the Divi version is {v}. Use "
           "--divi 5.x, tokens from the Divi 5 site, or no --divi/--tokens (the newest cached Divi 5)")


# ----------------------------------------------------------------------------- Divi 5 token seeding
# Nothing in a seeded value, selector or media query may end or escape its declaration/rule/<style>: no
# `;` `{` `}` `<` `>` `\`, line breaks or comments, and quotes, brackets and parentheses must pair up.
_UNSAFE_CSS = re.compile(r"[<>{};\\\r\n]|/\*|\*/")


def _css_safe(text) -> bool:
    if not isinstance(text, str) or not text.strip() or _UNSAFE_CSS.search(text):
        return False
    if text.count('"') % 2 or text.count("'") % 2:
        return False
    return text.count("(") == text.count(")") and text.count("[") == text.count("]")


def _var_css(entry: dict) -> str | None:
    """A tokens.json color/variable entry as the CSS value Divi prints for it (images and fonts were unwrapped
    by the extractor); None when unknown (value null) or unsafe to put in a <style>."""
    value = entry.get("value") if isinstance(entry, dict) else None
    if not _css_safe(value):
        return None
    kind = entry.get("kind")
    if kind in ("strings", "links"):
        return None  # resolved inline by Divi, never CSS
    if kind == "images":
        return None if '"' in value else 'url("' + value + '")'
    if kind == "fonts":
        name = value.strip("'\"")
        return None if ("'" in name or '"' in name) else "'" + name + "'"
    return value.strip()


def _rules_css(css) -> list:
    """The rules of one recovered preset css object ({selector, declarations, rules}) as CSS text."""
    if not isinstance(css, dict):
        return []
    rules = css.get("rules") or ([{"selector": css.get("selector"), "declarations": css.get("declarations")}]
                                 if css.get("selector") else [])
    out = []
    for rule in rules:
        sel, decls, media = rule.get("selector"), rule.get("declarations") or {}, rule.get("media")
        body = ";".join(f"{k}:{v}" for k, v in decls.items() if _css_safe(k) and _css_safe(v))
        if not _css_safe(sel) or not body:
            continue
        text = f"{sel}{{{body}}}"
        if media:
            if not _css_safe(media):
                continue
            text = f"@media {media}{{{text}}}"
        out.append(text)
    return out


def seed_css(tokens: dict) -> str:
    """The client's recovered Divi 5 design system as CSS for the (stock) Playground preview: one
    `:root:root{--gcid-…;--gvid-…}` block (colors.global, colors.customizer, variables; null and string/link
    values skipped; `:root:root` outranks the stock `:root` Divi prints) followed by every recovered preset
    rule (presets, group_presets, preset_defaults). Only what the extractor recovered: a preset with
    `css: null` and unknown values stay stock. Empty string when there is nothing to seed."""
    if not isinstance(tokens, dict):
        return ""
    colors = tokens.get("colors") or {}
    root = []
    for name, entry in (colors.get("global") or {}).items():
        v = _var_css({k: x for k, x in (entry or {}).items() if k != "kind"})
        if v is not None and re.fullmatch(r"gcid-[A-Za-z0-9_-]+", name):
            root.append(f"--{name}:{v};")
    for entry in (colors.get("customizer") or {}).values():
        name = (entry or {}).get("id") or ""
        v = _var_css({"value": (entry or {}).get("value")})
        if v is not None and re.fullmatch(r"gcid-[A-Za-z0-9_-]+", name):
            root.append(f"--{name}:{v};")
    for name, entry in (tokens.get("variables") or {}).items():
        v = _var_css(entry)
        if v is not None and re.fullmatch(r"gvid-[A-Za-z0-9_-]+", name):
            root.append(f"--{name}:{v};")
    parts = [":root:root{" + "".join(root) + "}"] if root else []
    for group in ("presets", "group_presets"):
        for entries in (tokens.get(group) or {}).values():
            for entry in entries or []:
                parts += _rules_css((entry or {}).get("css"))
    for css in (tokens.get("preset_defaults") or {}).values():
        parts += _rules_css(css)
    return "\n".join(dict.fromkeys(parts))


# Divi 5 stores the five Theme Customizer colors in et_divi under these keys and exposes them as these gcids
# (GlobalData::$customizer_colors).
CUSTOMIZER_COLOR_OPTIONS = {"gcid-primary-color": "accent_color", "gcid-secondary-color": "secondary_accent_color",
                            "gcid-heading-color": "header_color", "gcid-body-color": "font_color",
                            "gcid-link-color": "link_color"}
VARIABLE_BUCKETS = ("numbers", "strings", "images", "links", "fonts", "gradients")  # GlobalData.php:830
SEED_TIMESTAMP = "2000-01-01T00:00:00.000Z"  # lastUpdated of seeded global colors (Divi only displays it)


def _option_value(entry: dict) -> str | None:
    """A tokens.json color/variable value as Divi stores it in its options (fonts unquoted, images as the bare
    URL), under the same rules as seed_css: None when unknown (null) or unsafe."""
    value = entry.get("value")
    if entry.get("kind") in ("strings", "links"):
        return value.strip() if _css_safe(value) else None
    if _var_css(entry) is None:
        return None
    return value.strip().strip("'\"") if entry.get("kind") == "fonts" else value.strip()


def seed_options(tokens: dict) -> dict:
    """The client's recovered Divi 5 design system as the WordPress options Divi reads it from (research/divi5/
    tokens-and-detection.md §2), for the Playground preview's mu-plugin to merge over the stock site's options:
    {"et_divi": {"<customizer color option>": hex, "et_global_data": {"global_colors": {gcid: {...}}}},
     "et_divi_global_variables": {<kind>: {gvid: {id, label, value, order, status, type}}}}.
    Divi resolves a $variable() ref to a design variable only when the variable exists there, so this is what
    makes number/font/string/link/image variables render. Null, unsafe (same rules as seed_css) and unknown-kind
    entries are skipped; empty dict when there is nothing to seed."""
    if not isinstance(tokens, dict):
        return {}
    colors = tokens.get("colors") if isinstance(tokens.get("colors"), dict) else {}
    et_divi, global_colors, variables = {}, {}, {}
    customizer = [((e or {}).get("id"), e) for e in (colors.get("customizer") or {}).values()
                  if (e or {}).get("id") in CUSTOMIZER_COLOR_OPTIONS]
    for name, entry in list((colors.get("global") or {}).items()) + customizer:
        value = _option_value({"value": (entry or {}).get("value")})
        if value is None or not re.fullmatch(r"gcid-[A-Za-z0-9_-]+", name):
            continue
        if name in CUSTOMIZER_COLOR_OPTIONS:
            et_divi[CUSTOMIZER_COLOR_OPTIONS[name]] = value
        else:
            global_colors[name] = {"color": value, "label": name, "status": "active", "lastUpdated": SEED_TIMESTAMP,
                                   "folder": "", "usedInPosts": []}
    for name, entry in (tokens.get("variables") or {}).items():
        kind = (entry or {}).get("kind")
        value = _option_value(entry) if kind in VARIABLE_BUCKETS else None
        if value is None or not re.fullmatch(r"gvid-[A-Za-z0-9_-]+", name):
            continue
        bucket = variables.setdefault(kind, {})
        bucket[name] = {"id": name, "label": name, "value": value, "order": len(bucket) + 1, "status": "active",
                        "type": kind}
    if global_colors:
        et_divi["et_global_data"] = {"global_colors": global_colors}
    return {k: v for k, v in (("et_divi", et_divi), ("et_divi_global_variables", variables)) if v}


def unsupported_items(coverage: dict) -> dict:
    """What the Python preview doesn't render but the --exact preview does."""
    return {k: n for k, n in coverage.get("unsupported_modules", {}).items() if n}


def site_data_items(coverage: dict) -> dict:
    """What needs the live site's data: neither preview can show it."""
    return {k: n for k, n in coverage.get("needs_site_data", {}).items() if n}


def banner_html(coverage: dict) -> str:
    parts = []
    unsupported = unsupported_items(coverage)
    if unsupported:
        parts.append(BANNER_EXACT % html.escape(", ".join(sorted(unsupported))))
        parts += [html.escape(FEATURE_NOTES[k]) + "." for k in sorted(unsupported) if k in FEATURE_NOTES]
    if site_data_items(coverage):
        parts.append(BANNER_SITE % html.escape(", ".join(sorted(site_data_items(coverage)))))
    return BANNER % "<br>".join(parts) if parts else ""


NETWORK_NOTE = {
    "embedded": "note: Divi's icon fonts and theme images are embedded; web fonts (Google Fonts), jQuery "
                "if no WordPress copy is cached, and any remote content images load from the network",
    "served": "note: Divi's icon fonts and theme images come from /__divi/; web fonts (Google Fonts), jQuery "
              "if no WordPress copy is cached, and any remote content images load from the network",
}


def coverage_summary(coverage: dict, assets: str = "embedded") -> str:
    stats = coverage.get("stats", {})
    lines = [f"coverage: {coverage['modules']} modules, {coverage['attr_coverage_pct']}% of "
             f"{coverage['attrs_total']} attributes read (Divi {stats.get('divi_version')}, "
             f"rendered in {stats.get('render_ms')} ms)"]
    unsupported = unsupported_items(coverage)
    modules = {k: n for k, n in unsupported.items() if k.startswith("et_pb_")}
    features = {k: n for k, n in unsupported.items() if not k.startswith("et_pb_")}
    if modules:
        lines.append("unsupported modules (placeholders; use --exact): "
                     + ", ".join(f"{k} x{n}" for k, n in sorted(modules.items())))
    if features:
        lines.append("unsupported features (not rendered; use --exact): "
                     + ", ".join(f"{k} x{n}" + (f" ({FEATURE_NOTES[k]})" if k in FEATURE_NOTES else "")
                                 for k, n in sorted(features.items())))
    site = site_data_items(coverage)
    if site:
        lines.append(SITE_DATA_HINT + ", ".join(f"{k} x{n}" for k, n in sorted(site.items())))
    for tag, info in sorted(coverage.get("by_tag", {}).items()):
        if info["supported"] and info["ignored"]:
            lines.append(f"ignored attributes on {tag}: " + ", ".join(sorted(info["ignored"])))
    for problem in stats.get("parse_problems", []):
        lines.append(f"parse problem: {problem}")
    lines.append(NETWORK_NOTE[assets])
    return "\n".join(lines)


def exact_args(a) -> list:
    """preview.mjs arguments for the parsed command: the same page, output, pages dir, port and
    Divi version, with paths made absolute. Every value is forwarded explicitly (including our
    default port, so Node listens where this CLI would have). --no-js has no meaning there."""
    if a.cmd == "render":
        args = ["render", str(Path(a.page).resolve())]
        if a.out:
            args += ["--out", str(Path(a.out).resolve())]
    else:
        args = ["serve", "--pages", str(Path(a.pages).resolve()), "--port", str(a.port)]
    if a.divi:
        args += ["--divi", a.divi]
    if a.tokens:
        args += ["--tokens", str(Path(a.tokens).resolve())]
    return args


def node_major(node: str) -> tuple:
    """(major, version string) of this Node binary; major is None when it can't be read."""
    try:
        out = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None, "(version unknown)"
    try:
        return int(out.lstrip("v").split(".")[0]), out
    except ValueError:
        return None, out or "(version unknown)"


def exact_env(keys_path=None) -> dict:
    """The environment for the preview.mjs child: the current environment, with ET_USERNAME /
    ET_API_KEY filled in from wp_keys.resolve_et_credentials(keys_path) when not already set there
    (env always wins over the keys file, same as everywhere else). Never prints or logs this."""
    env = dict(os.environ)
    creds = wp_keys.resolve_et_credentials(keys_path)
    if creds:
        env["ET_USERNAME"], env["ET_API_KEY"] = creds
    return env


def usable_node(purpose: str = "", quiet: bool = False) -> str:
    """The `node` binary when it is Node 20+; otherwise prints the guidance (unless quiet) and raises
    NodeMissing (whose message is that guidance)."""
    node = shutil.which("node")
    message = f"{purpose}{NODE_GUIDANCE}"
    if node:
        major, version = node_major(node)
        if major is not None and major >= NODE_MIN_MAJOR:
            return node
        message = f"{purpose}found Node {version} at {node}. {NODE_GUIDANCE}"
    if not quiet:
        print(f"preview: {message}", file=sys.stderr)
    raise NodeMissing(message)


class NodeMissing(Exception):
    pass


def run_exact(a) -> int:
    """Hands the command to the real-Divi preview (Playground)."""
    try:
        node = usable_node()
    except NodeMissing:
        return 2
    try:
        env = exact_env(getattr(a, "keys", None))
    except wp_keys.KeysError as e:
        print(f"preview: {e}", file=sys.stderr)
        return 2
    return subprocess.call([node, str(PREVIEW_MJS), *exact_args(a)], env=env)


def _renderer():
    import divi_render
    return divi_render


def default_out(page: Path) -> Path:
    """<page name>.html in the current directory, or <page name>.preview.html when that is the page itself
    (a Divi 5 page kept as .html)."""
    out = Path.cwd() / (page.stem + ".html")
    return Path.cwd() / (page.stem + ".preview.html") if out.resolve() == page.resolve() else out


# ----------------------------------------------------------------------------- Divi 5 blocks (Playground)
D5_NODE = "Divi 5 block pages render on the real Divi 5 theme in WordPress Playground: "


def blocks_version(a) -> str:
    """The Divi 5 version for block pages (--divi/--tokens, else the newest cached 5.x, else latest5)."""
    version = resolve_divi_version(a.divi, a.tokens, major=5)
    if version_major(version) not in (5, None):
        raise UsageError(D5_ONLY.format(v=version))
    return version


def load_seed(tokens_path) -> tuple:
    """(seed_css(), seed_options()) of --tokens (empty without tokens, or for Divi 4 tokens that have no Divi 5
    ids). Read once: a serve session keeps the tokens it started with."""
    if not tokens_path:
        return "", {}
    try:
        tokens = json.loads(Path(tokens_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise UsageError(f"cannot read {tokens_path}: {e}") from None
    return seed_css(tokens), seed_options(tokens)


def safe_name(name: str) -> str:
    """The pp-preview mu-plugin only serves [A-Za-z0-9_-] page names."""
    return re.sub(r"[^A-Za-z0-9_-]", "-", name) or "page"


def write_atomic(path: Path, text: str) -> None:
    """Write PATH through <PATH>.tmp + os.replace: a render in flight never reads half a file."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def stage_block_page(page: Path, stage: Path, seed: str, name: str | None = None, options: dict | None = None) -> Path:
    """Writes <stage>/<name>.txt (the page with its local images inlined as data: URIs), plus the page's
    <stem>.meta.json and the token-seeding sidecars <name>.seed.css (seed_css) and <name>.seed.json
    (seed_options), for preview.mjs / the mu-plugin."""
    name = name or safe_name(page.stem)
    staged = stage / f"{name}.txt"
    text = local_media.embed_local_images(page.read_text(encoding="utf-8"), page.resolve().parent)
    write_atomic(staged, text)
    meta = page.with_name(page.stem + ".meta.json")
    if meta.is_file():
        shutil.copyfile(meta, stage / f"{name}.meta.json")
    seed_file = stage / f"{name}.seed.css"
    if seed:
        write_atomic(seed_file, seed)
    elif seed_file.exists():
        seed_file.unlink()
    options_file = stage / f"{name}.seed.json"
    if options:
        write_atomic(options_file, json.dumps(options))
    else:
        options_file.unlink(missing_ok=True)
    return staged


def render_blocks(a, page: Path) -> int:
    """render for a Divi 5 block page: Playground (preview.mjs render) on a Divi 5 theme, with local images
    inlined and the --tokens seed, writing the same standalone HTML file as --exact."""
    version = blocks_version(a)
    seed, options = load_seed(a.tokens)
    try:
        node = usable_node(D5_NODE)
        env = exact_env(getattr(a, "keys", None))
    except NodeMissing:
        return 2
    except wp_keys.KeysError as e:
        print(f"preview: {e}", file=sys.stderr)
        return 2
    out = Path(a.out).resolve() if a.out else default_out(page).resolve()
    with tempfile.TemporaryDirectory(prefix="pp-d5-render-") as stage:
        staged = stage_block_page(page, Path(stage), seed, options=options)
        code = subprocess.call([node, str(PREVIEW_MJS), "render", str(staged), "--out", str(out),
                                "--divi", version], env=env)
    if code == 0:
        print(f"Divi 5 block page rendered on Divi {version} (WordPress Playground)"
              + ("; tokens seeded: global colors, variables and preset CSS from tokens.json" if seed else "")
              + ("; the global colors and design variables also as the site's options" if options else "")
              + ". The WordPress draft preview stays the authoritative check.")
    return code


class PlaygroundPages:
    """One warm Playground (preview.mjs serve on a Divi 5 theme) for the block pages of a pages dir. The pages
    are staged into a private dir (local images inlined, tokens seed sidecars) and re-staged within ~0.5 s of
    an edit; the Playground re-renders on every request, so reloading shows the change. The seed (CSS and
    options) is the session's: every block page gets the same one, from the tokens read at start."""

    def __init__(self, pages: Path, version: str, seed: str, node: str, env: dict, options: dict | None = None):
        self.pages, self.version, self.seed, self.node, self.env = pages, version, seed, node, env
        self.options = options or {}
        self.stage = None
        self.base = None
        self.error = None
        self.proc = None
        self._mtimes: dict = {}
        self._lock = threading.Lock()  # staging
        self._start_lock = threading.Lock()  # one Playground, however many first requests arrive together
        self._stop = threading.Event()

    def names(self) -> dict:
        return {safe_name(n): f for n, f in page_files(self.pages).items() if page_is_blocks(f)}

    def sync(self) -> None:
        if self.stage is None:
            return
        with self._lock:
            current = self.names()
            for name, f in current.items():
                try:
                    stamp = (f.stat().st_mtime_ns, f.stat().st_size)
                    if self._mtimes.get(name) != stamp:
                        stage_block_page(f, self.stage, self.seed, name, self.options)
                        self._mtimes[name] = stamp
                except (OSError, UnicodeDecodeError) as e:
                    sys.stderr.write(f"preview: cannot stage {f}: {e}\n")
            for name in set(self._mtimes) - set(current):
                for ext in (".txt", ".meta.json", ".seed.css", ".seed.json"):
                    (self.stage / f"{name}{ext}").unlink(missing_ok=True)
                self._mtimes.pop(name, None)

    def start(self) -> None:
        with self._start_lock:
            if self.proc is not None or self._stop.is_set():
                return
            self.stage = Path(tempfile.mkdtemp(prefix="pp-d5-serve-"))
            self.sync()
            self.proc = subprocess.Popen([self.node, str(PREVIEW_MJS), "serve", "--pages", str(self.stage),
                                          "--port", str(free_port()), "--divi", self.version],
                                         env=self.env, stdout=subprocess.PIPE, text=True)
        threading.Thread(target=self._read, daemon=True).start()
        threading.Thread(target=self._watch, daemon=True).start()

    def _read(self) -> None:
        for line in self.proc.stdout:
            m = re.search(r"(http://\S+?)/\?pp_preview=", line)  # a page URL, or the "(no *.txt …)" hint
            if self.base is None and m:
                self.base = m.group(1)
                sys.stderr.write(f"Divi 5 block pages: WordPress Playground (Divi {self.version}) ready at "
                                 f"{self.base}\n")
        code = self.proc.wait()
        if not self._stop.is_set():
            self.error = f"the Divi 5 Playground (preview.mjs serve) exited with code {code}; see the log above"

    def _watch(self) -> None:
        while not self._stop.wait(0.5):
            self.sync()

    def url(self, name: str) -> str:
        return f"{self.base}/?pp_preview={safe_name(name)}"

    def stop(self) -> None:
        with self._start_lock:
            self._stop.set()
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        if self.stage:
            shutil.rmtree(self.stage, ignore_errors=True)


def free_port() -> int:
    """A free local TCP port for the Playground behind serve."""
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def page_files(pages: Path) -> dict:
    """name -> file for a pages dir: every <name>.txt, plus every <name>.html that holds Divi 5 blocks (a
    rendered preview .html has none, so it is not a page); a .txt wins over an .html of the same name."""
    found = {p.stem: p for p in pages.glob("*.html") if page_is_blocks(p)}
    found.update({p.stem: p for p in pages.glob("*.txt")})
    return dict(sorted(found.items()))


def page_is_blocks(path: Path) -> bool:
    try:
        return is_blocks(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return False


# ----------------------------------------------------------------------------- render
def cmd_render(a) -> int:
    page = Path(a.page)
    if not page.is_file():
        raise UsageError(f"no such page: {page}")
    if page_is_blocks(page):
        return render_blocks(a, page)
    if a.exact:
        return run_exact(a)
    version = resolve_divi_version(a.divi, a.tokens)
    if version_major(version) == 5:
        raise UsageError(D4_ONLY.format(v=version))
    dr = _renderer()
    source = local_media.embed_local_images(page.read_text(encoding="utf-8"), page.resolve().parent)
    result = dr.render_page(source, divi_version=version, title=page.stem,
                            with_js=not a.no_js, embed_assets=True, keys_path=a.keys)
    out = Path(a.out) if a.out else default_out(page)
    out.write_text(result.html, encoding="utf-8")
    print(f"wrote {out} ({len(result.html) / 1024:.0f} KB)")
    print(coverage_summary(result.coverage))
    return 0


# ----------------------------------------------------------------------------- serve
STARTING = ("<!DOCTYPE html><meta http-equiv=refresh content=2><title>Starting Divi 5 preview</title>"
            "<p>Starting WordPress Playground with Divi {v} for the Divi 5 block pages (a few seconds; about 30 s "
            "the very first time). This page reloads itself.</p>")


def make_handler(pages: Path, version: str | None, with_js: bool, keys_path=None, blocks=None,
                 version_error: str | None = None):
    """The serve handler. Divi 4 shortcode pages render in Python on `version` (None: they can't, and show
    `version_error`); Divi 5 block pages redirect to the warm Playground of `blocks` (LazyBlocks)."""
    dr = _renderer()
    from divi_render.assets import mime_type, resolve_asset
    theme = dr.theme_for(version, DIVI_ROUTE, False, keys_path=keys_path) if version else None
    # Per-page allowlist of the local image files that page's own attributes reference, rebuilt
    # on every render of that page: name -> {token: resolved Path}. /__local/<name>/<token> only
    # ever serves a path that's in here -- never a path built from the request itself, which is
    # what keeps this confined (no traversal is possible: a bad token is just a missing dict key).
    local_allow: dict = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            sys.stderr.write("%s %s\n" % (self.command, fmt % args))

        def send(self, code, body: bytes, ctype="text/html; charset=utf-8", extra=None):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def error_page(self, code, message):
            return self.send(code, f"<!DOCTYPE html><title>Preview</title><p>{html.escape(message)}</p>".encode())

        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            if path == "/":
                names = list(page_files(pages))
                items = "".join(f'<li><a href="/{html.escape(n)}">{html.escape(n)}</a></li>' for n in names)
                return self.send(200, f"<h1>Divi pages in {html.escape(str(pages))}</h1><ul>{items}</ul>".encode())
            if path.startswith("/__mtime/"):
                f = pages / (Path(path[len("/__mtime/"):]).name + ".txt")
                return self.send(200, str(f.stat().st_mtime_ns if f.is_file() else 0).encode(), "text/plain")
            if path.startswith(DIVI_ROUTE):
                f = resolve_asset(theme.path, path[len(DIVI_ROUTE):]) if theme and theme.path else None
                if f is None:
                    return self.send(404, b"not found", "text/plain")
                return self.send(200, f.read_bytes(), mime_type(f), {"Cache-Control": "max-age=3600"})
            if path.startswith(LOCAL_ROUTE):
                # Confinement: never build a filesystem path from the request. A token only
                # resolves through this page's own allowlist (populated the last time that page
                # was rendered, below) -- an unknown page, an unknown token, or any ".." attempt
                # is simply not a key in the dict, so it 404s exactly like an unrelated URL would.
                page_name, _, token = path[len(LOCAL_ROUTE):].partition("/")
                local = local_allow.get(page_name, {}).get(token)
                mime = local_media.image_mime_type(local) if local else None
                if local is None or mime is None or not local.is_file():
                    return self.send(404, b"not found", "text/plain")
                return self.send(200, local.read_bytes(), mime, {"Cache-Control": "no-store"})
            name = path.strip("/")
            f = page_files(pages).get(name) if name and "/" not in name else None
            if f is None:
                return self.send(404, b"no such page", "text/plain")
            if page_is_blocks(f):
                pg, blocks_error = blocks.get() if blocks else (None, None)
                if pg is None:
                    return self.error_page(500, blocks_error or "Divi 5 block pages can't be previewed here.")
                pg.start()
                if pg.error:
                    return self.error_page(500, pg.error)
                if pg.base is None:
                    return self.send(503, STARTING.format(v=html.escape(pg.version)).encode(),
                                     extra={"Retry-After": "2"})
                pg.sync()
                return self.send(302, b"", "text/plain", {"Location": pg.url(name)})
            if theme is None:
                return self.error_page(500, version_error or "Divi 4 pages can't be previewed here.")
            t0 = time.perf_counter()
            try:
                source, local_allow[name] = local_media.rewrite_for_serve(
                    f.read_text(encoding="utf-8"), f.resolve().parent, f"{LOCAL_ROUTE}{name}/")
                result = dr.render_page(source, divi_version=version, title=name,
                                        with_js=with_js, asset_base=DIVI_ROUTE, keys_path=keys_path)
            except Exception:  # a local dev server: show the error instead of dropping the connection
                tb = traceback.format_exc()
                sys.stderr.write(f"render error in {f}:\n{tb}")
                body = (f"<!DOCTYPE html><title>Render error: {html.escape(name)}</title>"
                        f"<h1>Render error in {html.escape(str(f))}</h1><pre>{html.escape(tb)}</pre>"
                        + RELOAD_JS % name)
                return self.send(500, body.encode("utf-8"))
            sys.stderr.write(f"[{name}] " + coverage_summary(result.coverage, "served").replace("\n", f"\n[{name}] ") + "\n")
            page = result.html
            unsupported = unsupported_items(result.coverage)
            banner = banner_html(result.coverage)
            if banner:
                page = page.replace("</body>", banner + "\n</body>", 1)
            page = page.replace("</body>", (RELOAD_JS % name) + "\n</body>", 1)
            headers = {"X-Render-Ms": f"{(time.perf_counter() - t0) * 1000:.1f}",
                       "X-Attr-Coverage": str(result.coverage["attr_coverage_pct"]),
                       "X-Unsupported": json.dumps(unsupported)[:500],
                       "X-Needs-Site-Data": json.dumps(site_data_items(result.coverage))[:500]}
            return self.send(200, page.encode("utf-8"), extra=headers)
    return Handler


def cmd_serve(a) -> int:
    pages = Path(a.pages).resolve()
    if not pages.is_dir():
        raise UsageError(f"no such pages dir: {pages}")
    files = page_files(pages)
    block_names = {n for n, f in files.items() if page_is_blocks(f)}
    shortcode_names = set(files) - block_names
    if a.exact:
        if not block_names:
            return run_exact(a)  # Divi 4 --exact: unchanged
        if shortcode_names:
            raise UsageError("--exact serve runs one Divi theme, but this dir mixes Divi 4 shortcode and Divi 5 "
                             "block pages: drop --exact (shortcode pages then use the Python preview and block "
                             "pages the Divi 5 Playground), or split the dir")
    # Divi 4 shortcode pages: the Python renderer, on the newest cached 4.x (or --divi/--tokens). Its theme
    # is only loaded when there are shortcode pages (a Divi 5-only dir never needs a Divi 4 download).
    version = None
    version_error = "this Divi 4 page was added after serve started with only Divi 5 pages: restart serve"
    v4 = resolve_divi_version(a.divi, a.tokens)
    if version_major(v4) == 5:
        version_error = D4_ONLY.format(v=v4)
        if shortcode_names and not block_names:
            raise UsageError(version_error)
    elif shortcode_names or not block_names:
        version = v4
    # Divi 5 block pages: one warm Playground, set up only when a block page exists (now, or on the first
    # block-page request): a Divi 4-only serve never resolves a Divi 5 version.
    blocks = LazyBlocks(pages, a)
    if block_names:
        pg, blocks_error = blocks.get()
        if blocks_error and not shortcode_names:
            print(f"preview: {blocks_error}", file=sys.stderr)
            return 2
        if blocks_error:
            print(f"preview: Divi 5 block pages won't render: {blocks_error}", file=sys.stderr)
    try:
        handler = make_handler(pages, version, not a.no_js, keys_path=a.keys, blocks=blocks,
                               version_error=version_error)
        server = ThreadingHTTPServer(("127.0.0.1", a.port), handler)
        base = f"http://127.0.0.1:{server.server_address[1]}"
        for n in files:
            print(f"{base}/{n}", flush=True)
        if not files:
            print(f"(no *.txt in {pages}; add one and open {base}/<name>)", flush=True)
        pg = blocks.started()
        if block_names and pg:
            pg.start()
        kinds = (["Python preview"] if not block_names else
                 (["Python preview for Divi 4 shortcode"] if shortcode_names else [])
                 + ([f"Divi {pg.version} Playground for block pages"] if pg else []))
        print(f"Serving ({', '.join(kinds)}); Ctrl-C to stop.", file=sys.stderr, flush=True)

        def on_term(*_):
            raise KeyboardInterrupt  # SIGTERM stops like Ctrl-C: the Playground child is stopped too

        signal.signal(signal.SIGTERM, on_term)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    finally:
        blocks.stop()  # the Playground child and its stage dir never outlive serve, even on a failed start
    return 0


class LazyBlocks:
    """The PlaygroundPages for serve, created on first need (Divi 5 version, seed, Node check) and remembered,
    with the reason when block pages can't render."""

    def __init__(self, pages: Path, a):
        self.pages, self.a = pages, a
        self._lock = threading.Lock()
        self._done = False
        self._pg = self._error = None

    def get(self) -> tuple:
        with self._lock:
            if not self._done:
                self._done = True
                try:
                    version = blocks_version(self.a)
                    seed, options = load_seed(self.a.tokens)
                    self._pg = PlaygroundPages(self.pages, version, seed, usable_node(D5_NODE, quiet=True),
                                               exact_env(self.a.keys), options)
                except (UsageError, NodeMissing, wp_keys.KeysError, fetch_divi.FetchError) as e:
                    self._error = str(e)
            return self._pg, self._error

    def started(self):
        """The PlaygroundPages if it was set up (not starting anything)."""
        return self._pg

    def stop(self) -> None:
        with self._lock:
            self._done = True  # no Playground after shutdown
            pg = self._pg
        if pg:
            pg.stop()


# ----------------------------------------------------------------------------- doctor / fetch
def et_credential_source(keys_path=None) -> str:
    """"env" / "keys.json" / "none": where ensure_divi would get Elegant Themes credentials from,
    without ever returning the credentials themselves. Mirrors resolve_et_credentials' own
    env-first precedence; an explicit --keys pointing at a missing file reports "none" rather
    than raising (doctor is a diagnostic, not a hard failure)."""
    if os.environ.get("ET_USERNAME") and os.environ.get("ET_API_KEY"):
        return "env"
    try:
        creds = wp_keys.resolve_et_credentials(keys_path)
    except wp_keys.KeysError as exc:  # KeysError messages never contain secrets
        return f"none (keys.json problem: {exc})"
    return "keys.json" if creds else "none"


def cmd_doctor(a) -> int:
    from divi_render.assets import find_jquery
    cached = fetch_divi.list_cached()
    node = shutil.which("node")
    node_version = ""
    if node:
        major, node_version = node_major(node)
        if major is None or major < NODE_MIN_MAJOR:
            node_version += f" (too old for --exact: need Node {NODE_MIN_MAJOR}+)"
    jq = find_jquery()
    d5 = fetch_divi.list_cached(major=5)
    lines = [
        f"python: {platform.python_version()} ({sys.executable})",
        f"cache dir: {fetch_divi.cache_root()}",
        f"cached Divi versions: {', '.join(cached) if cached else '(none: python3 preview.py fetch-divi VER)'}",
        "Divi 5 (block pages): " + ("cached " + ", ".join(d5) if d5 else
                                    "not cached (python3 preview.py fetch-divi latest5, or a 5.x version)"),
        f"jQuery: {jq if jq else 'CDN (no cached WordPress copy)'}",
        f"node: {node + ' ' + node_version if node else 'not found'} (only needed for --exact and Divi 5 block pages)",
        f"Elegant Themes credentials: {et_credential_source(getattr(a, 'keys', None))}",
    ]
    print("\n".join(lines))
    return 0


def cmd_fetch_divi(a) -> int:
    args = (["--keys", a.keys] if a.keys else []) + [a.version]
    return fetch_divi.main(args)


# ----------------------------------------------------------------------------- main
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="preview.py", description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd")

    keys_help = ("keys.json path, for its optional \"elegant_themes\" section (default: env "
                 "DIVI_KEYS_FILE, then ~/.config/divi-page-builder/keys.json); env ET_USERNAME + "
                 "ET_API_KEY still win when both are set")

    def version_flags(p):
        g = p.add_mutually_exclusive_group()
        g.add_argument("--divi", help="Divi version (default: --tokens, else the newest cached version of the page's "
                                     "Divi major, else latest / latest5)")
        g.add_argument("--tokens", help="tokens.json whose site.divi_version picks the Divi version")
        p.add_argument("--no-js", action="store_true", help="leave out Divi's front-end JS")
        p.add_argument("--exact", action="store_true", help="use the real-Divi Playground preview (needs Node)")
        p.add_argument("--keys", help=keys_help)

    r = sub.add_parser("render", help="render one page to a standalone HTML file")
    r.add_argument("page")
    r.add_argument("--out")
    version_flags(r)
    s = sub.add_parser("serve", help="live preview server")
    s.add_argument("--pages", default=".")
    s.add_argument("--port", type=int, default=8765)
    version_flags(s)
    d = sub.add_parser("doctor", help="report what the preview can use")
    d.add_argument("--keys", help=keys_help)
    f = sub.add_parser("fetch-divi", help="download and cache a Divi version")
    f.add_argument("version", help="4.27.9, 5.13.1, latest (newest Divi 4) or latest5 (newest Divi 5)")
    f.add_argument("--keys", help=keys_help)
    return ap


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    ap = build_parser()
    if not argv:
        ap.print_help(sys.stderr)
        return 2
    a = ap.parse_args(argv)
    commands = {"render": cmd_render, "serve": cmd_serve, "doctor": cmd_doctor, "fetch-divi": cmd_fetch_divi}
    try:
        return commands[a.cmd](a)
    except UsageError as e:
        print(f"preview: {e}", file=sys.stderr)
        return 2
    except fetch_divi.FetchError as e:
        print(f"preview: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
