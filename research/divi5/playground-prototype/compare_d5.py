#!/usr/bin/env python3
"""R5 fidelity check for Divi 5 pages: live LocalWP page vs Playground preview.

  compare_d5.py flatten <url> <out.html>          fetch a live page and inline its local stylesheets
                                                  (<link rel=stylesheet|preload as=style> under the
                                                  same origin) as <style data-href=...> blocks
  compare_d5.py compare <truth.html> <cand.html>  markup + builder-CSS comparison (JSON)

Reuses research/tools/fidelity.py (balanced .et-l block, (tag, class) sequence, and the
(media, selector, declaration) triple method for order-classed builder rules). The one D5
difference: builder CSS is not confined to `et-builder-module-design-*` style ids (D5 emits
`et-critical-inline-css`, `et-core-unified[-deferred]-<id>[-cached-inline-styles]`, ...), so the
builder CSS set is taken from EVERY <style> block, still filtered to order-classed selectors.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "research" / "tools"))
import fidelity  # noqa: E402


def flatten(url: str, out: str) -> None:
    html = urllib.request.urlopen(url).read().decode("utf-8", "replace")
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
        if not h.startswith(origin):
            return tag
        css = urllib.request.urlopen(h).read().decode("utf-8", "replace")
        return f'<style data-href="{h}">\n{css}\n</style>'

    Path(out).write_text(re.sub(r"<link\b[^>]*>", repl, html), encoding="utf-8")


# Builder-authored CSS blocks, by origin:
#   live D5 (static CSS files on):  <style id="et-critical-inline-css"> + et-core-unified-deferred-<id>.min.css
#                                   (flattened to <style data-href=...>) [+ et-core-unified-<id>.min.css]
#   Playground D5, first/forced-inline load: et-core-unified[-deferred]-<id>-cached-inline-styles[-N]
#   Divi 4: et-builder-module-design-*
_BUILDER = re.compile(
    r'<style (?:id="(?:et-critical-inline-css|et-core-unified-(?:deferred-)?\d+(?:-cached-inline-styles(?:-\d+)?)?'
    r'|et-builder-module-design-[^"]*)"|data-href="[^"]*/et-core-unified-[^"]*")[^>]*>(.*?)</style>', re.S)


def all_css(html: str) -> str:
    return "\n".join(_BUILDER.findall(html))


def compare(truth: str, cand: str) -> dict:
    a, b = fidelity._et_l(truth), fidelity._et_l(cand)
    sa, sb = fidelity._seq(a), fidelity._seq(b)
    import difflib
    sm = difflib.SequenceMatcher(None, sa, sb, autojunk=False)
    da, db = fidelity._decls(all_css(truth)), fidelity._decls(all_css(cand))
    common, union = da & db, da | db
    first = next((i for i, (x, y) in enumerate(zip(sa, sb)) if x != y), None)
    return {
        "markup": {"truth_elements": len(sa), "candidate_elements": len(sb),
                   "tag_class_sequence_equal": sa == sb, "tag_class_seq_ratio": round(sm.ratio(), 4),
                   "et_l_bytes": [len(a), len(b)], "et_l_identical": a == b,
                   "first_diff": None if first is None else [sa[first], sb[first]]},
        "css": {"truth_decls": len(da), "candidate_decls": len(db), "common": len(common),
                "missing": len(da - db), "extra": len(db - da),
                "ratio": round(len(common) / len(union), 4) if union else 1.0},
        "missing_examples": sorted(da - db)[:8],
        "extra_examples": sorted(db - da)[:8],
    }


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "flatten":
        flatten(sys.argv[2], sys.argv[3])
    elif cmd == "compare":
        rd = lambda p: Path(p).read_text(encoding="utf-8", errors="replace")
        print(json.dumps(compare(rd(sys.argv[2]), rd(sys.argv[3])), indent=1, ensure_ascii=False))
