#!/usr/bin/env python3
"""Validate a Divi page against Divi's module schema: Divi 4 shortcode or Divi 5 block content (auto-detected).

Usage: validate.py PAGE [--tokens tokens.json] [--baseline ORIGINAL] [--site-url URL] [--fragment] [--json]
--fragment: PAGE is one section or snippet, not a whole page (skips the page-level W_NO_H1, and for Divi 5
W5_NO_PLACEHOLDER).
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
from divi_checks_structure import check_headings, check_structure  # noqa: E402
from divi_checks_tokens import check_tokens  # noqa: E402
from divi_checks_values import check_attributes  # noqa: E402
from divi_format import _SHORTCODE as _SHORTCODE_TAG, detect_content  # noqa: E402
from divi_schema import Schema, load_schema  # noqa: E402
from divi_shortcode import parse  # noqa: E402
import divi5_blocks  # noqa: E402
from divi5_checks_structure import check_headings5, check_structure5  # noqa: E402
from divi5_checks_values import check_attributes5  # noqa: E402
from divi5_checks_tokens import check_tokens5  # noqa: E402
from divi5_schema import load_schema5  # noqa: E402


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
    """Collects findings for a Divi 4 (divi_shortcode) or Divi 5 (divi5_blocks) Document: both expose line_col();
    the tag is the shortcode tag (Node.tag) or the block name (Block.name)."""

    def __init__(self, doc):
        self.doc = doc
        self.findings: List[Finding] = []

    def __call__(self, level, code, message, node=None, path="", offset=None, attr="", value="", hint=""):
        pos = offset if offset is not None else (node.start if node is not None else 0)
        line, col = self.doc.line_col(pos)
        tag = "" if node is None else (node.name if isinstance(node, divi5_blocks.Block) else node.tag)
        self.findings.append(Finding(level, code, message, line, col, path,
                                     tag=tag, attr=attr, value=value, hint=hint))


def mark_preexisting(findings, baseline_findings) -> None:
    pool = Counter((f.code, f.tag, f.attr, f.value) for f in baseline_findings)
    for f in findings:
        key = (f.code, f.tag, f.attr, f.value)
        if pool[key] > 0:
            pool[key] -= 1
            f.preexisting = True


def _validate_blocks(source: str, fragment: bool, tokens: Optional[dict], site_url: Optional[str]) -> List[Finding]:
    doc = divi5_blocks.parse(source)
    report = Reporter(doc)
    schema5 = load_schema5()
    check_structure5(doc, schema5, report, fragment=fragment)
    check_headings5(doc, schema5, report, fragment=fragment)
    check_attributes5(doc, schema5, report, **_tokens5(tokens, site_url))
    if tokens:
        check_tokens5(doc, schema5, tokens, report)
    return report.findings


def _dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _preset_ids(node) -> set:
    """Every preset "id"/"uuid" under a tokens presets tree: the Divi 4 shape {slug: [{uuid}]} and the Divi 5 shape
    {module|group: {name: [{id}]}} alike."""
    out = set()
    if isinstance(node, dict):
        for key in ("id", "uuid"):
            if isinstance(node.get(key), str):
                out.add(node[key])
        for v in node.values():
            if isinstance(v, (dict, list)):
                out |= _preset_ids(v)
    elif isinstance(node, list):
        for v in node:
            out |= _preset_ids(v)
    return out


def _tokens5(tokens: Optional[dict], site_url: Optional[str]) -> dict:
    """check_attributes5 keyword arguments from tokens.json, read defensively (the D5 tokens shape is still settling:
    presets ids, colors.global keys, variables keys at either depth, site.divi_version). known_vars stays None
    without tokens, so unknown gcid-/gvid- ids are only reported against a real token list."""
    t = _dict(tokens)
    site = _dict(t.get("site"))
    colors = _dict(t.get("colors"))
    known_vars = None
    if t:
        names = set(_dict(colors.get("global")))
        palette = colors.get("palette")
        names |= {p["global"] for p in (palette if isinstance(palette, list) else ()) if isinstance(p, dict)
                  and isinstance(p.get("global"), str)}
        for key, value in _dict(t.get("variables")).items():
            names.add(key)
            names |= set(_dict(value))
        known_vars = frozenset(names)
    version = site.get("divi_version")
    return {"known_presets": frozenset(_preset_ids(t.get("presets")) | _preset_ids(t.get("group_presets"))),
            "known_vars": known_vars,
            "site_host": urlparse(site_url or (site.get("url") if isinstance(site.get("url"), str) else "")).hostname,
            "site_version": version if isinstance(version, str) and version else None}


def _mixed(source: str) -> List[Finding]:
    doc = divi5_blocks.parse(source)
    report = Reporter(doc)
    offset = next((f.start + m.start() for f in _freeforms(doc.nodes)
                   for m in [_SHORTCODE_TAG.search(f.value)] if m), 0)
    report("error", "E5_MIXED_FORMAT", "Page mixes Divi 4 shortcode and Divi 5 blocks", offset=offset, path="(page)",
           hint="Use one format: Divi 5 sites take divi/* blocks only (convert the [et_pb_*] shortcode), "
                "Divi 4 sites take shortcode only.")
    return report.findings


def _freeforms(nodes):
    for n in nodes:
        if isinstance(n, divi5_blocks.Freeform):
            yield n
        else:
            yield from _freeforms(n.children)


def validate_source(source: str, schema: Optional[Schema] = None, tokens: Optional[dict] = None,
                    site_url: Optional[str] = None, baseline: Optional[str] = None,
                    fragment: bool = False) -> List[Finding]:
    """Validate Divi 4 shortcode or Divi 5 blocks (detect_content decides). `schema` is the Divi 4 schema
    (loaded when omitted); block content always uses the Divi 5 schema (load_schema5) and ignores it."""
    kind = detect_content(source)
    if kind == "mixed":
        findings = _mixed(source)
    elif kind == "blocks":
        findings = _validate_blocks(source, fragment, tokens, site_url)
    else:
        return _validate_shortcode(source, schema if schema is not None else load_schema(), tokens, site_url,
                                   baseline, fragment)
    if baseline is not None:
        mark_preexisting(findings, validate_source(baseline, schema, tokens=tokens, site_url=site_url,
                                                   fragment=fragment))
    return findings


def _validate_shortcode(source: str, schema: Schema, tokens: Optional[dict], site_url: Optional[str],
                        baseline: Optional[str], fragment: bool) -> List[Finding]:
    doc = parse(source)
    report = Reporter(doc)
    check_structure(doc, schema, report)
    check_headings(doc, schema, report, fragment=fragment)
    known = {p["uuid"] for lst in (tokens or {}).get("presets", {}).values() for p in lst}
    host = urlparse(site_url or (tokens or {}).get("site", {}).get("url", "")).hostname
    check_attributes(doc, schema, report, known_presets=known, site_host=host)
    if tokens:
        check_tokens(doc, schema, tokens, report)
    if baseline is not None:
        mark_preexisting(report.findings, _validate_shortcode(baseline, schema, tokens, site_url, None, fragment))
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
    ap.add_argument("--fragment", action="store_true",
                    help="PAGE is a single section/snippet: skip the page-level W_NO_H1 check")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        source = Path(args.page).read_text(encoding="utf-8")
        tokens = json.loads(Path(args.tokens).read_text()) if args.tokens else None
        baseline = Path(args.baseline).read_text(encoding="utf-8") if args.baseline else None
        schema = None if detect_content(source) in ("blocks", "mixed") else load_schema()
    except (OSError, ValueError) as exc:
        print(f"validate.py: {exc}", file=sys.stderr)
        return 2
    findings = validate_source(source, schema, tokens=tokens, site_url=args.site_url, baseline=baseline,
                               fragment=args.fragment)
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
