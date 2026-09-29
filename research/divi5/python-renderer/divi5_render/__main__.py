"""Internal entry point (the harness and tests; preview.py integration is Task 21-R5e):

    python3 -m divi5_render PAGE.html -o OUT.html [--divi 5.13.1] [--tokens tokens.json] [--coverage cov.json]

(run with research/divi5/python-renderer and Skill/divi-page-builder/scripts on PYTHONPATH).
"""
import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "divi5_render"  # noqa: A001

from divi5_render import render_page  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="divi5_render")
    ap.add_argument("page")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--divi")
    ap.add_argument("--tokens")
    ap.add_argument("--coverage")
    ap.add_argument("--no-embed", action="store_true", help="leave the static CSS's fonts/images as relative URLs")
    a = ap.parse_args(argv)
    tokens = json.loads(Path(a.tokens).read_text(encoding="utf-8")) if a.tokens else None
    r = render_page(Path(a.page).read_text(encoding="utf-8"), divi_version=a.divi, tokens=tokens,
                    embed_assets=not a.no_embed, title=Path(a.page).stem)
    Path(a.out).write_text(r.html, encoding="utf-8")
    if a.coverage:
        Path(a.coverage).write_text(json.dumps(r.coverage, indent=1), encoding="utf-8")
    print(json.dumps({k: r.coverage[k] for k in ("modules", "unsupported_modules", "attrs_total", "attrs_ignored")}),
          f"ignored={len(r.coverage['ignored'])}", f"render_ms={r.coverage['stats']['render_ms']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
