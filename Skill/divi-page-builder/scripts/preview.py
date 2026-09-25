#!/usr/bin/env python3
"""Divi 4 page preview with the pure-Python renderer (stdlib only, no Node, PHP or WordPress).

  python3 preview.py render PAGE [--out FILE] [--tokens tokens.json | --divi VER] [--no-js] [--exact]
      Writes one standalone HTML file (Divi's CSS/JS inlined, icon fonts and theme images as data:
      URIs, so it works opened from disk or over HTTP) and prints the coverage summary: modules the
      Python renderer doesn't support and attributes it ignored. Default --out: <page name>.html.
  python3 preview.py serve [--pages DIR] [--port 8765] [--tokens tokens.json | --divi VER] [--no-js] [--exact]
      Serves http://127.0.0.1:PORT/<name> for every DIR/<name>.txt, re-rendered on each request.
      The page polls for edits and reloads itself. Divi's fonts/images/JS come from /__divi/...
      Pages with unsupported modules show a banner.
  python3 preview.py doctor
      Reports Python, the cache dir, cached Divi versions and whether Node is present (only
      needed for --exact).
  python3 preview.py fetch-divi VER
      Downloads and caches a Divi version (needs ET_USERNAME / ET_API_KEY; the only command that does).

--exact runs the same command on the real-Divi preview (node scripts/preview/preview.mjs on
WordPress Playground) for pages the Python renderer can't reproduce. It needs Node 18+.

Divi version (render/serve): --divi, else --tokens (site.divi_version), else the newest cached
version, else "latest". A cached version never triggers an Elegant Themes API call.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import fetch_divi  # noqa: E402

PREVIEW_MJS = HERE / "preview" / "preview.mjs"
DIVI_ROUTE = "/__divi/"
NODE_GUIDANCE = ("--exact needs Node.js 18+ (it runs the real Divi theme on WordPress Playground via "
                 "scripts/preview/preview.mjs). Install Node from https://nodejs.org/ or drop --exact to "
                 "use the Python preview.")
RELOAD_JS = """<script>(function(){var m=null;setInterval(function(){fetch('/__mtime/%s',{cache:'no-store'})
.then(function(r){return r.text()}).then(function(t){if(m===null){m=t}else if(t!==m){location.reload()}})
.catch(function(){})},1000)})();</script>"""
BANNER = ('<div id="pp-preview-banner" style="position:fixed;z-index:999999;left:0;right:0;bottom:0;padding:8px 14px;'
          'background:#e11d48;color:#fff;font:13px/1.4 -apple-system,Segoe UI,sans-serif">'
          'Not rendered by the Python preview: %s. For the exact preview: add --exact.</div>')


class UsageError(Exception):
    pass


# ----------------------------------------------------------------------------- shared
def resolve_divi_version(divi: str | None, tokens: str | None) -> str:
    """--divi, else --tokens (site.divi_version), else the newest cached version, else 'latest'."""
    if divi:
        return divi
    if tokens:
        try:
            data = json.loads(Path(tokens).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise UsageError(f"cannot read {tokens}: {e}") from None
        version = (data.get("site") or {}).get("divi_version") if isinstance(data, dict) else None
        if not version:
            raise UsageError(f"No site.divi_version in {tokens}")
        return version
    return fetch_divi.newest_cached() or "latest"


def unsupported_items(coverage: dict) -> dict:
    return {k: n for k, n in coverage.get("unsupported_modules", {}).items() if n}


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
                     + ", ".join(f"{k} x{n}" for k, n in sorted(features.items())))
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


def run_exact(a) -> int:
    """Hands the command to the real-Divi preview (Playground)."""
    node = shutil.which("node")
    if not node:
        print(f"preview: {NODE_GUIDANCE}", file=sys.stderr)
        return 2
    return subprocess.call([node, str(PREVIEW_MJS), *exact_args(a)])


def _renderer():
    import divi_render
    return divi_render


# ----------------------------------------------------------------------------- render
def cmd_render(a) -> int:
    page = Path(a.page)
    if not page.is_file():
        raise UsageError(f"no such page: {page}")
    version = resolve_divi_version(a.divi, a.tokens)
    dr = _renderer()
    result = dr.render_page(page.read_text(encoding="utf-8"), divi_version=version, title=page.stem,
                            with_js=not a.no_js, embed_assets=True)
    out = Path(a.out) if a.out else Path.cwd() / (page.stem + ".html")
    out.write_text(result.html, encoding="utf-8")
    print(f"wrote {out} ({len(result.html) / 1024:.0f} KB)")
    print(coverage_summary(result.coverage))
    return 0


# ----------------------------------------------------------------------------- serve
def make_handler(pages: Path, version: str, with_js: bool):
    dr = _renderer()
    from divi_render.assets import mime_type, resolve_asset
    theme = dr.theme_for(version, DIVI_ROUTE, False)

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

        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            if path == "/":
                names = sorted(p.stem for p in pages.glob("*.txt"))
                items = "".join(f'<li><a href="/{html.escape(n)}">{html.escape(n)}</a></li>' for n in names)
                return self.send(200, f"<h1>Divi pages in {html.escape(str(pages))}</h1><ul>{items}</ul>".encode())
            if path.startswith("/__mtime/"):
                f = pages / (Path(path[len("/__mtime/"):]).name + ".txt")
                return self.send(200, str(f.stat().st_mtime_ns if f.is_file() else 0).encode(), "text/plain")
            if path.startswith(DIVI_ROUTE):
                f = resolve_asset(theme.path, path[len(DIVI_ROUTE):]) if theme.path else None
                if f is None:
                    return self.send(404, b"not found", "text/plain")
                return self.send(200, f.read_bytes(), mime_type(f), {"Cache-Control": "max-age=3600"})
            name = path.strip("/")
            f = pages / f"{name}.txt"
            if not name or "/" in name or not f.is_file():
                return self.send(404, b"no such page", "text/plain")
            t0 = time.perf_counter()
            try:
                result = dr.render_page(f.read_text(encoding="utf-8"), divi_version=version, title=name,
                                        with_js=with_js, asset_base=DIVI_ROUTE)
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
            if unsupported:
                banner = BANNER % html.escape(", ".join(sorted(unsupported)))
                page = page.replace("</body>", banner + "\n</body>", 1)
            page = page.replace("</body>", (RELOAD_JS % name) + "\n</body>", 1)
            headers = {"X-Render-Ms": f"{(time.perf_counter() - t0) * 1000:.1f}",
                       "X-Attr-Coverage": str(result.coverage["attr_coverage_pct"]),
                       "X-Unsupported": json.dumps(unsupported)[:500]}
            return self.send(200, page.encode("utf-8"), extra=headers)
    return Handler


def cmd_serve(a) -> int:
    pages = Path(a.pages).resolve()
    if not pages.is_dir():
        raise UsageError(f"no such pages dir: {pages}")
    version = resolve_divi_version(a.divi, a.tokens)
    handler = make_handler(pages, version, not a.no_js)
    server = ThreadingHTTPServer(("127.0.0.1", a.port), handler)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    names = sorted(p.stem for p in pages.glob("*.txt"))
    for n in names:
        print(f"{base}/{n}", flush=True)
    if not names:
        print(f"(no *.txt in {pages}; add one and open {base}/<name>)", flush=True)
    print("Serving (Python preview); Ctrl-C to stop.", file=sys.stderr, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


# ----------------------------------------------------------------------------- doctor / fetch
def cmd_doctor(a) -> int:
    from divi_render.assets import find_jquery
    cached = fetch_divi.list_cached()
    node = shutil.which("node")
    node_version = ""
    if node:
        try:
            node_version = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            node_version = "(version unknown)"
    jq = find_jquery()
    lines = [
        f"python: {platform.python_version()} ({sys.executable})",
        f"cache dir: {fetch_divi.cache_root()}",
        f"cached Divi versions: {', '.join(cached) if cached else '(none: python3 preview.py fetch-divi VER)'}",
        f"jQuery: {jq if jq else 'CDN (no cached WordPress copy)'}",
        f"node: {node + ' ' + node_version if node else 'not found'} (only needed for --exact)",
    ]
    print("\n".join(lines))
    return 0


def cmd_fetch_divi(a) -> int:
    return fetch_divi.main([a.version])


# ----------------------------------------------------------------------------- main
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="preview.py", description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd")

    def version_flags(p):
        g = p.add_mutually_exclusive_group()
        g.add_argument("--divi", help="Divi version (default: --tokens, else newest cached, else latest)")
        g.add_argument("--tokens", help="tokens.json whose site.divi_version picks the Divi version")
        p.add_argument("--no-js", action="store_true", help="leave out Divi's front-end JS")
        p.add_argument("--exact", action="store_true", help="use the real-Divi Playground preview (needs Node)")

    r = sub.add_parser("render", help="render one page to a standalone HTML file")
    r.add_argument("page")
    r.add_argument("--out")
    version_flags(r)
    s = sub.add_parser("serve", help="live preview server")
    s.add_argument("--pages", default=".")
    s.add_argument("--port", type=int, default=8765)
    version_flags(s)
    sub.add_parser("doctor", help="report what the preview can use")
    f = sub.add_parser("fetch-divi", help="download and cache a Divi version")
    f.add_argument("version")
    return ap


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    ap = build_parser()
    if not argv:
        ap.print_help(sys.stderr)
        return 2
    a = ap.parse_args(argv)
    if getattr(a, "exact", False):
        return run_exact(a)
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
