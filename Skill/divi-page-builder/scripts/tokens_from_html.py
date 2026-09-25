"""Read site-wide Divi styling from a public page's HTML: Customizer CSS, global colors, fonts, Divi version.

Selectors below are the exact ones recorded in research/tools/notes/customizer-css.md (Task 12
Step 1, captured against Divi 4.27.9). Two things that discovery found necessary, beyond picking
the right selector:

- CSS comments must be stripped before splitting rules into selectors/declarations: one of Divi's
  <style> blocks opens with a `/*# sourceURL=... */` comment immediately followed by its first
  real selector on the next line, and a comment-unaware splitter glues the two together so the
  selector never matches.
- Matching must take the *last* rule for a given selector+property, not the first: Divi's own
  base/reset CSS declares plain-selector rules (e.g. `body{font-size:14px;color:#666}`) earlier in
  the document than the Customizer's override rules for the same selector, and since both use
  equal-specificity selectors the browser (and this parser) must apply the one that appears later.
- At-rule blocks (`@media`, `@supports`, `@font-face`, ...) must be stripped before rules are split
  out, not just fed to the same flat rule/selector splitter: a breakpoint override inside `@media`
  uses the same plain selectors as the desktop rule (e.g. `body{color:...}`), and since RULE_RE has
  no notion of nesting, a rule inside a media block would otherwise be picked up as if it were a
  top-level rule -- and, depending on source order relative to the real desktop rule, "last wins"
  could then pick the *breakpoint* value instead of the desktop Customizer value.
"""
from __future__ import annotations

import re
from urllib.parse import parse_qs, unquote, urlparse  # noqa: F401  (urlparse kept for API parity)

COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
DECL_RE = re.compile(r"([\w-]+)\s*:\s*([^;]+)")


def _strip_at_rules(css: str) -> str:
    """Drop every top-level at-rule (`@media{...}`, `@supports{...}`, `@font-face{...}`,
    `@import ...;`, ...), block or statement, so only plain top-level rules remain for `_rules()`
    to split. A small brace-depth scan, not a regex: `@media` blocks nest further rules inside
    them, which a flat `{...}`-matching regex can't tell apart from a top-level rule."""
    out = []
    i, n = 0, len(css)
    while i < n:
        if css[i] == "@":
            j = i
            while j < n and css[j] not in ";{":
                j += 1
            if j >= n:
                break  # unterminated at-rule (malformed CSS): drop the remainder
            if css[j] == ";":
                i = j + 1  # statement at-rule (e.g. @import/@charset): drop through the ';'
                continue
            depth = 1
            k = j + 1
            while k < n and depth > 0:
                if css[k] == "{":
                    depth += 1
                elif css[k] == "}":
                    depth -= 1
                k += 1
            i = k  # block at-rule: drop the whole nested block
            continue
        out.append(css[i])
        i += 1
    return "".join(out)


def _rules(css: str):
    for m in RULE_RE.finditer(css):
        selectors = [s.strip() for s in m.group(1).split(",")]
        decls = {k.strip().lower(): v.strip().replace("!important", "").strip() for k, v in DECL_RE.findall(m.group(2))}
        yield selectors, decls


def _last(css: str, selector: str, prop: str) -> str:
    """Value of `prop` in the last rule (source order) whose selector list contains `selector`
    exactly. "Last" matches the CSS cascade for the equal-specificity, single-selector rules this
    parser targets -- see the module docstring."""
    result = ""
    for selectors, decls in _rules(css):
        if selector in selectors and prop in decls:
            result = decls[prop]
    return result


def tokens_from_html(html: str) -> dict:
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    css = COMMENT_RE.sub("", css)
    css = _strip_at_rules(css)
    fonts = []
    for href in re.findall(r"fonts\.googleapis\.com/css2?\?([^\"']+)", html):
        for fam in parse_qs(unquote(href.replace("&#038;", "&"))).get("family", []):
            for part in fam.split("|"):
                name = part.split(":")[0].replace("+", " ").strip()
                if name and name not in fonts:
                    fonts.append(name)
    version = ""
    m = re.search(r'content="Divi v\.([\d.]+)"', html) or \
        re.search(r"themes/Divi/[^\"']*\?ver=([\d.]+)", html)
    if m:
        version = m.group(1)
    global_colors = {k: v.strip() for k, v in re.findall(r"--(gcid-[\w-]+)\s*:\s*([^;}]+)", css)}
    customizer = {
        "body_text": _last(css, "body", "color"),
        "heading": _last(css, "h1", "color"),
        "link": _last(css, "a", "color"),
        "accent": _last(css, ".et_pb_counter_amount", "background-color") or _last(css, "#top-menu li.current-menu-item>a", "color"),
        "body_font": _last(css, "body", "font-family").split(",")[0].strip("'\" "),
        "heading_font": _last(css, "h1", "font-family").split(",")[0].strip("'\" "),
        "body_size": _last(css, "body", "font-size"),
        "content_width": _last(css, ".et_pb_fullwidth_section .et_pb_title_container", "max-width"),
    }
    return {"divi_version": version, "global_colors": global_colors, "fonts": fonts,
            "customizer": {k: v for k, v in customizer.items() if v}}
