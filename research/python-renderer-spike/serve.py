#!/usr/bin/env python3
"""SPIKE: stdlib-only live preview server for Divi shortcode pages.

    python3 serve.py [--pages DIR] [--port 8765] [--divi-path DIR] [--no-js]

GET /              index of <name>.txt files in the pages dir
GET /<name>        renders <name>.txt on every request (edit -> reload)
GET /__divi/<path> serves static files (fonts, images, js) from the local Divi theme dir
GET /__mtime/<name> mtime of <name>.txt; the page polls it once a second and reloads on change
"""
from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import divi_render as dr  # noqa: E402

RELOAD_JS = """<script>(function(){var m=null;setInterval(function(){fetch('/__mtime/%s',{cache:'no-store'})
.then(function(r){return r.text()}).then(function(t){if(m===null){m=t}else if(t!==m){location.reload()}})
.catch(function(){})},1000)})();</script>"""


def make_handler(pages: Path, data: dr.DiviData, with_js: bool, jquery: str | None):
    class H(BaseHTTPRequestHandler):
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
                body = "<h1>Divi pages</h1><ul>" + "".join(f'<li><a href="/{html.escape(n)}">{html.escape(n)}</a></li>' for n in names) + "</ul>"
                return self.send(200, body.encode())
            if path.startswith("/__mtime/"):
                f = pages / (Path(path[len("/__mtime/"):]).name + ".txt")
                return self.send(200, str(f.stat().st_mtime_ns if f.exists() else 0).encode(), "text/plain")
            if path.startswith("/__divi/"):
                if not data.divi_path:
                    return self.send(404, b"no divi path")
                rel = os.path.normpath(path[len("/__divi/"):]).lstrip("/")
                f = (data.divi_path / rel).resolve()
                if not str(f).startswith(str(data.divi_path.resolve())) or not f.is_file() or f.suffix == ".php":
                    return self.send(404, b"not found")
                ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
                return self.send(200, f.read_bytes(), ctype, {"Cache-Control": "max-age=3600"})
            name = Path(path.strip("/")).name
            f = pages / f"{name}.txt"
            if not f.exists():
                return self.send(404, b"no such page")
            t0 = time.perf_counter()
            page, ctx, stats = dr.render_page(f.read_text(encoding="utf-8"), data, title=name, with_js=with_js,
                                              jquery=jquery, reload_js=RELOAD_JS % name)
            cov = dr.coverage_report(ctx)
            hdr = {"X-Render-Ms": f"{(time.perf_counter() - t0) * 1000:.1f}",
                   "X-Attr-Coverage": str(cov["attr_coverage_pct"]),
                   "X-Unsupported": json.dumps(cov["unsupported_modules"])[:500]}
            return self.send(200, page.encode("utf-8"), extra=hdr)
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default=str(Path(__file__).resolve().parent / "pages"))
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--divi-path", default=str(dr.DEFAULT_DIVI))
    ap.add_argument("--theme-css-url")
    ap.add_argument("--no-js", action="store_true")
    a = ap.parse_args()
    divi = Path(a.divi_path).expanduser()
    data = dr.DiviData(divi if divi.exists() else None, a.theme_css_url)
    data.asset_base = "/__divi/"
    jquery = dr.find_jquery(data.divi_path)
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(Path(a.pages), data, not a.no_js, jquery))
    print(f"Serving {a.pages} at http://127.0.0.1:{a.port}/", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
