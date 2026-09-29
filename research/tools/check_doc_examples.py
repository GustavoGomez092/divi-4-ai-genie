#!/usr/bin/env python3
"""Validate every Divi example fenced in the skill's Markdown. Usage: check_doc_examples.py <skill_dir>

Divi 4: every ```divi block (shortcode). Divi 5: every ```divi5 block, plus ```html blocks under
reference/divi5/ and recipes/divi5/ whose content is Divi 5 block markup (other ```html blocks there are
plain HTML illustrations and are skipped). A ```divi5 block that is not block markup fails.

A block fails on any validation error, on W5_UNTYPED_COLUMN (an example column must carry its type), and on
the heading-outline warnings: W_HEADING_SKIP in any block, W_NO_H1 only in whole-page recipes (recipes/pages/, recipes/divi5/pages/). Every other block
(section recipes, edit recipes, module reference snippets) is a fragment of a page and is validated with
fragment=True (validate.py --fragment), which skips the page-level W_NO_H1 (and, for Divi 5,
W5_NO_PLACEHOLDER).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Skill" / "divi-page-builder" / "scripts"))
from divi_format import detect_content  # noqa: E402
from divi_schema import load_schema  # noqa: E402
from validate import validate_source  # noqa: E402

BLOCK_RE = re.compile(r"^```divi\n(.*?)^```", re.S | re.M)
# An opening ```divi fence on its own line. Compared against BLOCK_RE's match count below so a
# closing ``` glued to the last content line (no newline before it) can't silently vanish: BLOCK_RE
# would then either fail to match that block at all, or (with more than one block in the file)
# swallow a later block's fence as its own closer. Either way the counts stop agreeing.
OPEN_FENCE_RE = re.compile(r"^```divi[ \t]*$", re.M)
BLOCK5_RE = re.compile(r"^```divi5\n(.*?)^```", re.S | re.M)
OPEN_FENCE5_RE = re.compile(r"^```divi5[ \t]*$", re.M)
HTML_RE = re.compile(r"^```html\n(.*?)^```", re.S | re.M)
FAILING_WARNINGS = {"W_HEADING_SKIP", "W_NO_H1", "W5_UNTYPED_COLUMN"}  # an untyped column: widths unchecked
DIVI5_DIRS = (("reference", "divi5"), ("recipes", "divi5"))


def is_whole_page(rel: Path) -> bool:
    return rel.parts[:2] == ("recipes", "pages") or rel.parts[:3] == ("recipes", "divi5", "pages")


def is_divi5_doc(rel: Path) -> bool:
    return rel.parts[:2] in DIVI5_DIRS


def _examples(rel: Path, text: str):
    """(kind, source) for every example block in one file, in order: kind is "divi" or "divi5"."""
    found = [(m.start(), "divi", m.group(1)) for m in BLOCK_RE.finditer(text)]
    found += [(m.start(), "divi5", m.group(1)) for m in BLOCK5_RE.finditer(text)]
    if is_divi5_doc(rel):
        found += [(m.start(), "divi5", m.group(1)) for m in HTML_RE.finditer(text)
                  if detect_content(m.group(1)) == "blocks"]
    return [(kind, src) for _pos, kind, src in sorted(found, key=lambda t: t[0])]


def _fence_mismatch(text: str):
    """(fence, opened, parsed) for the first fence kind whose opening count differs from its parsed blocks."""
    for fence, open_re, block_re in (("divi", OPEN_FENCE_RE, BLOCK_RE), ("divi5", OPEN_FENCE5_RE, BLOCK5_RE)):
        opens, blocks = len(open_re.findall(text)), len(block_re.findall(text))
        if opens != blocks:
            return fence, opens, blocks
    return None


def check(skill_dir: Path):
    schema = load_schema()
    failures = []
    for md in sorted(skill_dir.rglob("*.md")):
        text = md.read_text()
        rel = md.relative_to(skill_dir)
        mismatch = _fence_mismatch(text)
        if mismatch:
            fence, opens, blocks = mismatch
            failures.append((rel, "fence-mismatch", [(
                "E_FENCE_MISMATCH", None,
                f"{opens} ```{fence} opening fence(s) but only {blocks} block(s) parsed — "
                "a closing ``` is probably glued to the last content line instead of on its own line",
            )]))
            continue
        for i, (kind, src) in enumerate(_examples(rel, text)):
            src = src.strip()
            if kind == "divi5" and detect_content(src) != "blocks":
                failures.append((rel, i, [("E_FENCE_FORMAT", None, "a ```divi5 example must be Divi 5 block "
                                                                   f"markup, not {detect_content(src)} content")]))
                continue
            findings = validate_source(src, schema, fragment=not is_whole_page(rel))
            errors = [f for f in findings if f.level == "error" or f.code in FAILING_WARNINGS]
            if errors:
                failures.append((rel, i, [(e.code, e.attr, e.message) for e in errors[:5]]))
    return failures


def count_blocks(skill_dir: Path, kind: str = None) -> int:
    """Examples check() validates (kind "divi" or "divi5" to count one format)."""
    return sum(1 for md in skill_dir.rglob("*.md")
               for k, _src in _examples(md.relative_to(skill_dir), md.read_text()) if kind in (None, k))


if __name__ == "__main__":
    skill_dir = Path(sys.argv[1])
    fails = check(skill_dir)
    for path, i, errs in fails:
        print(f"{path} block {i}: {errs}")
    print(f"{count_blocks(skill_dir, 'divi')} Divi 4 and {count_blocks(skill_dir, 'divi5')} Divi 5 example(s) checked")
    print(f"{len(fails)} failing block(s)")
    sys.exit(1 if fails else 0)
