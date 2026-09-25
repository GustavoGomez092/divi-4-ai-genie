#!/usr/bin/env python3
"""Evaluate the Python renderer against real-Divi output (markup + builder CSS).

  evaluate.py <truth.html> <python.html> [--show N] [--json out.json]

Markup: the balanced `.et-l` block of both files -> sequence of (tag, class list) for every
element; reports exact-sequence equality, difflib ratio, elements with identical class lists.
CSS: (media, single selector, declaration) triples of builder rules (selectors containing a
module order class such as .et_pb_text_3), same method as playground-prototype/compare.py.
"""
import argparse
import difflib
import json
import re
from html.parser import HTMLParser


def et_l(html):
    m = re.search(r'<div class="et-l et-l--post">', html)
    if not m:
        return ""
    depth = 0
    for t in re.finditer(r'<(/?)div\b[^>]*>', html[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return html[m.start(): m.start() + t.end()]
    return ""


class Seq(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.items.append((tag, " ".join((a.get("class") or "").split())))

    def handle_data(self, d):
        if d.strip():
            self.text.append(" ".join(d.split()))


def seq(html):
    p = Seq()
    p.feed(html)
    return p.items, p.text


ORDER = r'\.et_pb_[a-z_]+?_\d+(?![\d_])'


def builder_css(html):
    for sid in ("et-builder-module-design-990000001-cached-inline-styles", "et-builder-module-design-python-inline-styles"):
        m = re.search(r'<style id="%s">(.*?)</style>' % sid, html, re.S)
        if m:
            return m.group(1)
    return ""


def decls(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out = set()
    media = ''
    for tok in re.finditer(r'(@media[^{]*)\{|([^{}]+)\{([^{}]*)\}|\}', css):
        if tok.group(1):
            media = re.sub(r'\s+', ' ', tok.group(1)).strip()
            continue
        if tok.group(0) == '}':
            media = ''
            continue
        sels, body = tok.group(2), tok.group(3)
        for sel in sels.split(','):
            sel = re.sub(r'\s+', ' ', sel).strip()
            if not re.search(ORDER, sel):
                continue
            # split on ; outside parentheses (data: URIs contain ;)
            depth, cur, parts = 0, '', []
            for ch in body:
                depth += (ch == '(') - (ch == ')')
                if ch == ';' and depth == 0:
                    parts.append(cur)
                    cur = ''
                else:
                    cur += ch
            parts.append(cur)
            for d in parts:
                d = re.sub(r'\s*:\s*', ':', re.sub(r'\s+', ' ', d).strip(), count=1)
                if d:
                    out.add(f'{media} | {sel} {{ {d} }}')
    return out


def evaluate(truth_html, py_html, show=0):
    a, b = et_l(truth_html), et_l(py_html)
    sa, ta = seq(a)
    sb, tb = seq(b)
    sm = difflib.SequenceMatcher(None, sa, sb, autojunk=False)
    matched = sum(bl.size for bl in sm.get_matching_blocks())
    tags_only = difflib.SequenceMatcher(None, [x[0] for x in sa], [x[0] for x in sb], autojunk=False)
    # per-position identical class lists after alignment of tag sequence
    same_cls = 0
    for op, i1, i2, j1, j2 in tags_only.get_opcodes():
        if op == 'equal':
            same_cls += sum(1 for k in range(i2 - i1) if sa[i1 + k][1] == sb[j1 + k][1])
    # whitespace-insensitive class compare (Divi emits double spaces inside class attrs)
    text_ratio = difflib.SequenceMatcher(None, ta, tb, autojunk=False).ratio()
    da, db = decls(builder_css(truth_html)), decls(builder_css(py_html))
    res = {
        "markup": {
            "truth_elements": len(sa), "python_elements": len(sb),
            "byte_identical": a == b,
            "whitespace_normalized_identical": re.sub(r'\s+', ' ', a) == re.sub(r'\s+', ' ', b),
            "tag_class_sequence_equal": sa == sb,
            "tag_class_seq_ratio": round(sm.ratio(), 4),
            "tag_class_matched_elements": matched,
            "tag_seq_ratio": round(tags_only.ratio(), 4),
            "elements_with_identical_class_list": same_cls,
            "text_node_ratio": round(text_ratio, 4),
        },
        "css": {
            "truth_decls": len(da), "python_decls": len(db), "common": len(da & db),
            "missing": len(da - db), "extra_or_wrong": len(db - da),
            "recall_pct": round(100 * len(da & db) / len(da), 1) if da else 100.0,
            "precision_pct": round(100 * len(da & db) / len(db), 1) if db else 100.0,
        },
    }
    if show:
        res["css"]["missing_sample"] = sorted(da - db)[:show]
        res["css"]["extra_sample"] = sorted(db - da)[:show]
        diffs = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != 'equal':
                diffs.append({"op": op, "truth": sa[i1:i2][:4], "python": sb[j1:j2][:4]})
        res["markup"]["diff_sample"] = diffs[:show]
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("truth")
    ap.add_argument("python")
    ap.add_argument("--show", type=int, default=0)
    ap.add_argument("--json")
    a = ap.parse_args()
    r = evaluate(open(a.truth, encoding="utf-8", errors="replace").read(),
                 open(a.python, encoding="utf-8", errors="replace").read(), a.show)
    print(json.dumps(r, indent=1, ensure_ascii=False))
    if a.json:
        open(a.json, "w").write(json.dumps(r, indent=1, ensure_ascii=False))
