#!/usr/bin/env python3
"""Validate Divi 4 page shortcode against Divi's module schema.

Usage: validate.py PAGE [--tokens tokens.json] [--baseline ORIGINAL] [--site-url URL] [--json]
Exit status: 0 = no blocking errors, 1 = errors found, 2 = usage or I/O problem.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from divi_checks_structure import check_structure  # noqa: E402
from divi_checks_tokens import check_tokens  # noqa: E402
from divi_checks_values import check_attributes  # noqa: E402
from divi_schema import Schema, load_schema  # noqa: E402
from divi_shortcode import Document, parse  # noqa: E402


@dataclass
class Finding:
    level: str
    code: str
    message: str
    line: int
    col: int
    path: str
    tag: str = ""
    attr: str = ""
    value: str = ""
    hint: str = ""
    preexisting: bool = False


class Reporter:
    def __init__(self, doc: Document):
        self.doc = doc
        self.findings: List[Finding] = []

    def __call__(self, level, code, message, node=None, path="", offset=None, attr="", value="", hint=""):
        pos = offset if offset is not None else (node.start if node is not None else 0)
        line, col = self.doc.line_col(pos)
        self.findings.append(Finding(level, code, message, line, col, path,
                                     tag=node.tag if node is not None else "", attr=attr, value=value, hint=hint))


def mark_preexisting(findings, baseline_findings) -> None:
    pool = Counter((f.code, f.tag, f.attr, f.value) for f in baseline_findings)
    for f in findings:
        key = (f.code, f.tag, f.attr, f.value)
        if pool[key] > 0:
            pool[key] -= 1
            f.preexisting = True


def validate_source(source: str, schema: Schema, tokens: Optional[dict] = None,
                    site_url: Optional[str] = None, baseline: Optional[str] = None) -> List[Finding]:
    doc = parse(source)
    report = Reporter(doc)
    check_structure(doc, schema, report)
    known = {p["uuid"] for lst in (tokens or {}).get("presets", {}).values() for p in lst}
    host = urlparse(site_url or (tokens or {}).get("site", {}).get("url", "")).hostname
    check_attributes(doc, schema, report, known_presets=known, site_host=host)
    if tokens:
        check_tokens(doc, schema, tokens, report)
    if baseline is not None:
        mark_preexisting(report.findings, validate_source(baseline, schema, tokens=tokens, site_url=site_url))
    return report.findings


def _format(f: Finding, filename: str) -> str:
    out = f"{filename}:{f.line}:{f.col} {f.level} {f.code} {f.path}\n  {f.message}"
    if f.hint:
        out += f"\n  hint: {f.hint}"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("--tokens")
    ap.add_argument("--baseline")
    ap.add_argument("--site-url")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        source = Path(args.page).read_text(encoding="utf-8")
        tokens = json.loads(Path(args.tokens).read_text()) if args.tokens else None
        baseline = Path(args.baseline).read_text(encoding="utf-8") if args.baseline else None
        schema = load_schema()
    except (OSError, ValueError) as exc:
        print(f"validate.py: {exc}", file=sys.stderr)
        return 2
    findings = validate_source(source, schema, tokens=tokens, site_url=args.site_url, baseline=baseline)
    blocking = [f for f in findings if f.level == "error" and not f.preexisting]
    warnings = sum(f.level == "warning" and not f.preexisting for f in findings)
    if args.json:
        print(json.dumps({"file": args.page, "errors": len(blocking),
                          "warnings": warnings,
                          "findings": [asdict(f) for f in findings]}, indent=1))
    else:
        for f in findings:
            if not f.preexisting:
                print(_format(f, args.page))
        pre = [f for f in findings if f.preexisting]
        if pre:
            print(f"\n{len(pre)} pre-existing finding(s) also present in the baseline (not blocking):")
            for f in pre:
                print(_format(f, args.page))
        print(f"\nSummary: {len(blocking)} error(s), {warnings} warning(s), {len(pre)} pre-existing")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
