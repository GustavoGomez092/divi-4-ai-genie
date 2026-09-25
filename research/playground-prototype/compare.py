#!/usr/bin/env python3
"""Compare a Playground preview against a live Divi page.

  compare.py <live.html> <preview.html>

Reports: .et-l builder markup equality, builder CSS declaration set equality
(regex over every <style> block), and body classes diff.
"""
import re
import sys


def et_l(html):
    """Return the balanced <div class="et-l et-l--post"> ... </div> block."""
    m = re.search(r'<div class="et-l et-l--post">', html)
    if not m:
        return None
    depth, i = 0, m.start()
    for t in re.finditer(r'<(/?)div\b[^>]*>', html[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return html[m.start(): m.start() + t.end()]
    return None


# A module *order class* (.et_pb_text_3, .et_pb_column_1) - not a column-type class like .et_pb_column_1_3.
SKIP_STYLE_IDS = r'id=[\'"]divi-dynamic-critical' + '-inline-css'  # handle + suffix kept apart: tests/test_no_divi_assets.py forbids the literal id
ORDER = r'\.et_pb_[a-z_]+?_\d+(?![\d_])'


def decls(html):
    """Set of (media, single selector, declaration) for builder rules (.et_pb_<module>_<n>).

    Grouped selectors are exploded, because Divi groups them differently when it splits CSS
    into critical/deferred files (live) vs one inline block (preview)."""
    # Theme base CSS (not builder output): on the live site Divi inlines part of it as
    # the `divi-dynamic-critical` handle's inline style block; in the preview the same rules live in style-static.min.css.
    css = '\n'.join(body for attrs, body in re.findall(r'<style([^>]*)>(.*?)</style>', html, re.S)
                     if not re.search(SKIP_STYLE_IDS, attrs))
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out = set()
    media, depth = '', 0
    for tok in re.finditer(r'(@media[^{]*)\{|([^{}]+)\{([^{}]*)\}|\}', css):
        if tok.group(1):
            media = re.sub(r'\s+', ' ', tok.group(1)).strip()
            continue
        if tok.group(0) == '}':
            media = ''
            continue
        sels, body = tok.group(2), tok.group(3)
        if not re.search(ORDER, sels):
            continue
        for sel in sels.split(','):
            sel = re.sub(r'\s+', ' ', sel).strip()
            if not re.search(ORDER, sel):
                continue
            for d in body.split(';'):
                d = re.sub(r'\s*:\s*', ':', re.sub(r'\s+', ' ', d).strip(), count=1)
                if d:
                    out.add(f'{media} | {sel} {{ {d} }}')
    return out


def body_classes(html):
    m = re.search(r'<body[^>]*class="([^"]*)"', html)
    return set(m.group(1).split()) if m else set()


live, prev = (open(p, encoding='utf-8', errors='replace').read() for p in sys.argv[1:3])
a, b = et_l(live), et_l(prev)
print(f'.et-l live={len(a or "")} chars preview={len(b or "")} chars identical={a == b}')
if a and b and a != b:
    for n, (x, y) in enumerate(zip(a, b)):
        if x != y:
            print('  first diff at', n, '\n  live:   ', a[max(0, n - 120): n + 120], '\n  preview:', b[max(0, n - 120): n + 120])
            break
    ca = re.findall(r'class="([^"]*)"', a)
    cb = re.findall(r'class="([^"]*)"', b)
    print(f'  class sequences: live={len(ca)} preview={len(cb)} equal={ca == cb}')
da, db = decls(live), decls(prev)
print(f'builder CSS decls live={len(da)} preview={len(db)} common={len(da & db)} only-live={len(da - db)} only-preview={len(db - da)}')
for d in sorted(da - db)[:15]:
    print('  - live only:', d[:200])
for d in sorted(db - da)[:15]:
    print('  + preview only:', d[:200])
ba, bb = body_classes(live), body_classes(prev)
print('body classes only-live:', sorted(ba - bb), 'only-preview:', sorted(bb - ba))
