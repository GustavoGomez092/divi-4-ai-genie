#!/usr/bin/env python3
"""Compare a rendered page's markup + builder CSS against real-Divi ground truth (Task 14/23).

  fidelity.py <truth.html> <candidate.html> [--show N] [--json out.json]

Ported from research/python-renderer-spike/evaluate.py's comparison logic (stdlib only), so any
renderer (the Python renderer, or a future one) can be scored against the same measuring stick.

Markup: the balanced `.et-l` block of both files -> sequence of (tag, class list) for every
element; reports exact-sequence equality and a difflib ratio over that sequence.
CSS: (media, single selector, declaration) triples of builder rules (selectors containing a module
order class such as .et_pb_text_3) - same method as research/playground-prototype/compare.py.
"""
import argparse
import difflib
import json
import re
from html.parser import HTMLParser

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


def _builder_css(html: str) -> str:
    """All builder-authored CSS: real Divi prints it in the inline style, the *deferred* style
    (Playground, no critical CSS), or split between both; the Python renderer uses its own id."""
    return "\n".join(m.group(1) for m in _BUILDER_STYLE.finditer(html))


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
        },
        "css": {
            "truth_decls": len(da),
            "common": len(common),
            "missing": len(missing),
            "extra": len(extra),
            "ratio": round(len(common) / len(union), 4) if union else 1.0,
        },
        "missing_examples": missing[:10],
        "extra_examples": extra[:10],
    }


if __name__ == "__main__":
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
