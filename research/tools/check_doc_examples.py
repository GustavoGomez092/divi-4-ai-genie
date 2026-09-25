#!/usr/bin/env python3
"""Validate every ```divi fenced block in the skill's Markdown. Usage: check_doc_examples.py <skill_dir>

A block fails on any validation error, and on the heading-outline warnings: W_HEADING_SKIP in any
block, W_NO_H1 only in whole-page recipes (recipes/pages/). Every other block (section recipes,
edit recipes, module reference snippets) is a fragment of a page and is validated with
fragment=True (validate.py --fragment), which skips the page-level W_NO_H1.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Skill" / "divi-page-builder" / "scripts"))
from divi_schema import load_schema  # noqa: E402
from validate import validate_source  # noqa: E402

BLOCK_RE = re.compile(r"^```divi\n(.*?)^```", re.S | re.M)
# An opening ```divi fence on its own line. Compared against BLOCK_RE's match count below so a
# closing ``` glued to the last content line (no newline before it) can't silently vanish: BLOCK_RE
# would then either fail to match that block at all, or (with more than one block in the file)
# swallow a later block's fence as its own closer. Either way the counts stop agreeing.
OPEN_FENCE_RE = re.compile(r"^```divi[ \t]*$", re.M)
FAILING_WARNINGS = {"W_HEADING_SKIP", "W_NO_H1"}


def is_whole_page(rel: Path) -> bool:
    return rel.parts[:2] == ("recipes", "pages")


def check(skill_dir: Path):
    schema = load_schema()
    failures = []
    for md in sorted(skill_dir.rglob("*.md")):
        text = md.read_text()
        opens = len(OPEN_FENCE_RE.findall(text))
        blocks = list(BLOCK_RE.finditer(text))
        if len(blocks) != opens:
            failures.append((md.relative_to(skill_dir), "fence-mismatch", [(
                "E_FENCE_MISMATCH", None,
                f"{opens} ```divi opening fence(s) but only {len(blocks)} block(s) parsed — "
                "a closing ``` is probably glued to the last content line instead of on its own line",
            )]))
            continue
        rel = md.relative_to(skill_dir)
        for i, m in enumerate(blocks):
            findings = validate_source(m.group(1).strip(), schema, fragment=not is_whole_page(rel))
            errors = [f for f in findings if f.level == "error" or f.code in FAILING_WARNINGS]
            if errors:
                failures.append((md.relative_to(skill_dir), i, [(e.code, e.attr, e.message) for e in errors[:5]]))
    return failures


def count_blocks(skill_dir: Path) -> int:
    return sum(len(BLOCK_RE.findall(md.read_text())) for md in skill_dir.rglob("*.md"))


if __name__ == "__main__":
    skill_dir = Path(sys.argv[1])
    fails = check(skill_dir)
    for path, i, errs in fails:
        print(f"{path} block {i}: {errs}")
    print(f"{count_blocks(skill_dir)} ```divi block(s) checked")
    print(f"{len(fails)} failing block(s)")
    sys.exit(1 if fails else 0)
