#!/usr/bin/env python3
"""Compare a rendered page's markup + builder CSS against real-Divi ground truth (Task 14/23).

  fidelity.py <truth.html> <candidate.html> [--show N] [--json out.json]
  fidelity.py flatten <url> <out.html>     fetch a live page with its same-origin stylesheets inlined

Ported from research/python-renderer-spike/evaluate.py's comparison logic (stdlib only), so any
renderer (the Python renderer, or a future one) can be scored against the same measuring stick.

Markup: the balanced `.et-l` block of both files -> sequence of (tag, class list) for every
element; reports exact-sequence equality and a difflib ratio over that sequence.
CSS: (media, single selector, declaration) triples of builder rules (selectors containing a module
order class such as .et_pb_text_3) - same method as research/playground-prototype/compare.py.

Divi 5 pages (a Divi 5 front-end marker, divi_format._D5_HTML_MARKERS) keep their builder CSS under other
style ids (research/divi5/playground-prototype/compare_d5.py): `et-critical-inline-css`,
`et-core-unified[-deferred]-<id>[-cached-inline-styles[-N]]`, and et-cache `et-core-unified-*` files that
`flatten` inlines as `<style data-href=...>`. Those ids count only on Divi 5 pages, so Divi 4 numbers are
unchanged (a Divi 4 page can carry `et-critical-inline-css` too).

Determinism: only tags, class lists and builder CSS are compared, never attribute values or text.
What real Divi prints differently on every request therefore needs no normalization: the contact
form's `_wpnonce-et-pb-contact-form-submitted-N` value and its captcha digits (rand(1, 15), in the
question text and the data-first_digit/data-second_digit attributes), and the Email Optin's
checksum input (tests/test_fidelity.py pins this).
"""
import argparse
import difflib
import json
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Skill" / "divi-page-builder" / "scripts"))
from divi_format import _D5_HTML_MARKERS  # noqa: E402

_ORDER = re.compile(r"\.et_pb_[a-z_]+?_\d+(?![\d_])")


def _et_l(html: str) -> str:
    """The first balanced `<div class="et-l et-l--post">...</div>` block, or "" if absent."""
    m = re.search(r'<div class="et-l et-l--post">', html)
    if not m:
        return ""
    depth = 0
    for t in re.finditer(r"<(/?)div\b[^>]*>", html[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return html[m.start(): m.start() + t.end()]
    return ""


class _Seq(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.items.append((tag, " ".join((a.get("class") or "").split())))


def _seq(html: str):
    p = _Seq()
    p.feed(html)
    return p.items


_BUILDER_STYLE = re.compile(
    r'<style id="et-builder-module-design-(?:deferred-)?(?:\d+-cached|python)-inline-styles">(.*?)</style>', re.S)


# Divi 5 (compare_d5.py): live (static CSS files on) <style id="et-critical-inline-css"> + the flattened
# et-core-unified[-deferred]-<id>.min.css; Playground first render et-core-unified[-deferred]-<id>-cached-inline-styles[-N].
_BUILDER_STYLE5 = re.compile(
    r'<style (?:id="(?:et-critical-inline-css|et-core-unified-(?:deferred-)?\d+(?:-cached-inline-styles(?:-\d+)?)?'
    r'|et-builder-module-design-[^"]*)"|data-href="[^"]*/et-core-unified-[^"]*")[^>]*>(.*?)</style>', re.S)


def is_divi5_page(html: str) -> bool:
    return bool(_D5_HTML_MARKERS.search(html))


def _builder_css(html: str) -> str:
    """All builder-authored CSS: real Divi prints it in the inline style, the *deferred* style
    (Playground, no critical CSS), or split between both; the Python renderer uses its own id.
    Divi 5 pages: the Divi 5 style ids as well (see the module docstring)."""
    pattern = _BUILDER_STYLE5 if is_divi5_page(html) else _BUILDER_STYLE
    return "\n".join(m.group(1) for m in pattern.finditer(html))


def _decls(css: str) -> set:
    """Set of 'media | selector { declaration }' strings for builder-authored (order-classed) rules."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = set()
    media = ""
    for tok in re.finditer(r"(@media[^{]*)\{|([^{}]+)\{([^{}]*)\}|\}", css):
        if tok.group(1):
            media = re.sub(r"\s+", " ", tok.group(1)).strip()
            continue
        if tok.group(0) == "}":
            media = ""
            continue
        sels, body = tok.group(2), tok.group(3)
        for sel in sels.split(","):
            sel = re.sub(r"\s+", " ", sel).strip()
            if not _ORDER.search(sel):
                continue
            # split on ';' outside parentheses (data: URIs contain ';')
            depth, cur, parts = 0, "", []
            for ch in body:
                depth += (ch == "(") - (ch == ")")
                if ch == ";" and depth == 0:
                    parts.append(cur)
                    cur = ""
                else:
                    cur += ch
            parts.append(cur)
            for d in parts:
                d = re.sub(r"\s*:\s*", ":", re.sub(r"\s+", " ", d).strip(), count=1)
                if d:
                    out.add(f"{media} | {sel} {{ {d} }}")
    return out


def compare(truth_html: str, candidate_html: str) -> dict:
    """Compares real-Divi `truth_html` against a candidate renderer's `candidate_html`.

    Returns a dict with:
      markup.truth_elements, markup.candidate_elements  - element counts in the .et-l block
      markup.tag_class_sequence_equal (bool)            - exact (tag, class-list) sequence match
      markup.tag_class_seq_ratio (float)                - difflib ratio over that sequence
      css.truth_decls, css.common, css.missing, css.extra
      css.ratio (float)                                 - Jaccard similarity of the declaration sets
      missing_examples, extra_examples                  - up to 10 example declarations each
    """
    a, b = _et_l(truth_html), _et_l(candidate_html)
    sa, sb = _seq(a), _seq(b)
    sm = difflib.SequenceMatcher(None, sa, sb, autojunk=False)

    da, db = _decls(_builder_css(truth_html)), _decls(_builder_css(candidate_html))
    common, union = da & db, da | db
    missing, extra = sorted(da - db), sorted(db - da)

    return {
        "markup": {
            "truth_elements": len(sa),
            "candidate_elements": len(sb),
            "tag_class_sequence_equal": sa == sb,
            "tag_class_seq_ratio": round(sm.ratio(), 4),
            "et_l_bytes": [len(a), len(b)],
            "et_l_identical": a == b,
        },
        "css": {
            "truth_decls": len(da),
            "candidate_decls": len(db),
            "common": len(common),
            "missing": len(missing),
            "extra": len(extra),
            "ratio": round(len(common) / len(union), 4) if union else 1.0,
        },
        "missing_examples": missing[:10],
        "extra_examples": extra[:10],
    }


def _fetch(url: str) -> str:
    return urllib.request.urlopen(url, timeout=60).read().decode("utf-8", "replace")


def flatten(url: str, fetch=_fetch) -> str:
    """The page at `url` with every same-origin <link rel=stylesheet> and <link rel=preload as=style> replaced
    by `<style data-href=URL>` holding that file (what a browser applies; a plain fetch misses the deferred
    et-cache CSS a Divi 5 page preloads). Other links stay as they are."""
    html = fetch(url)
    origin = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))

    def repl(m):
        tag = m.group(0)
        rel = re.search(r"rel=['\"](stylesheet|preload)['\"]", tag)
        href = re.search(r"href=['\"]([^'\"]+)['\"]", tag)
        if not rel or not href:
            return tag
        if rel.group(1) == "preload" and not re.search(r"as=['\"]style['\"]", tag):
            return tag
        h = href.group(1).replace("&#038;", "&").replace("&amp;", "&")
        if not h.startswith(origin + "/"):
            return tag
        return f'<style data-href="{h}">\n{fetch(h)}\n</style>'

    return re.sub(r"<link\b[^>]*>", repl, html)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "flatten":
        Path(sys.argv[3]).write_text(flatten(sys.argv[2]), encoding="utf-8")
        sys.exit(0)
    ap = argparse.ArgumentParser()
    ap.add_argument("truth")
    ap.add_argument("candidate")
    ap.add_argument("--json")
    args = ap.parse_args()
    result = compare(
        open(args.truth, encoding="utf-8", errors="replace").read(),
        open(args.candidate, encoding="utf-8", errors="replace").read(),
    )
    print(json.dumps(result, indent=1, ensure_ascii=False))
    if args.json:
        open(args.json, "w").write(json.dumps(result, indent=1, ensure_ascii=False))
