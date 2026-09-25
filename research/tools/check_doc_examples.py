#!/usr/bin/env python3
"""Validate every ```divi fenced block in the skill's Markdown. Usage: check_doc_examples.py <skill_dir>"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Skill" / "divi-page-builder" / "scripts"))
from divi_schema import load_schema  # noqa: E402
from validate import validate_source  # noqa: E402

BLOCK_RE = re.compile(r"^```divi\n(.*?)^```", re.S | re.M)


def check(skill_dir: Path):
    schema = load_schema()
    failures = []
    for md in sorted(skill_dir.rglob("*.md")):
        for i, m in enumerate(BLOCK_RE.finditer(md.read_text())):
            errors = [f for f in validate_source(m.group(1).strip(), schema) if f.level == "error"]
            if errors:
                failures.append((md.relative_to(skill_dir), i, [(e.code, e.attr, e.message) for e in errors[:5]]))
    return failures


if __name__ == "__main__":
    fails = check(Path(sys.argv[1]))
    for path, i, errs in fails:
        print(f"{path} block {i}: {errs}")
    print(f"{len(fails)} failing block(s)")
    sys.exit(1 if fails else 0)
