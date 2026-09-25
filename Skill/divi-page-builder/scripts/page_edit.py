#!/usr/bin/env python3
"""Surgical edits to a Divi page: everything outside the targeted node stays byte-identical.

Usage: page_edit.py PAGE outline
       page_edit.py PAGE extract PATH
       page_edit.py PAGE replace PATH FILE | insert-after PATH FILE | insert-before PATH FILE
       page_edit.py PAGE set-attr PATH NAME VALUE      (VALUE is plain text; it is escaped for you)
       page_edit.py PAGE delete PATH
Options: --out FILE (default: stdout). PATH looks like: et_pb_section[1] > et_pb_row[0] > et_pb_column[2] > et_pb_blurb[0]

Note: the page (and any snippet FILE for replace/insert-after/insert-before) is read and written
with no newline translation, so CRLF/LF line endings outside the target span are never rewritten;
a snippet file's own line endings are kept as provided (only leading/trailing whitespace is
stripped).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from divi_shortcode import build_open_tag, escape_attr_value, parse, replace_span  # noqa: E402


def _read_raw(path) -> str:
    # newline="" disables universal-newline translation: \r\n, \r and \n all come through exactly
    # as stored on disk, so byte offsets computed against this string match the file's real bytes.
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def _write_raw(path, data: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(data)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("command", choices=["outline", "extract", "replace", "insert-after", "insert-before", "set-attr", "delete"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    src = _read_raw(a.page)
    doc = parse(src)
    if a.command == "outline":
        lines = [f"{path}  admin_label={n.value('admin_label')}  ({n.end - n.start} chars)" for n, path, _ in doc.walk()]
        result = "\n".join(lines) + "\n"
    else:
        if not a.args:
            ap.error("PATH is required")
        node = doc.find(a.args[0])
        if node is None:
            print(f"page_edit.py: no node at {a.args[0]}", file=sys.stderr)
            return 2
        if a.command == "extract":
            result = src[node.start:node.end]
        elif a.command == "delete":
            result = replace_span(src, node.start, node.end, "")
        elif a.command == "set-attr":
            if len(a.args) != 3:
                ap.error("set-attr needs PATH NAME VALUE")
            node.attrs[a.args[1]] = escape_attr_value(a.args[2], a.args[1])
            opening = build_open_tag(node)
            if node.raw_open[:-1].rstrip().endswith("/"):
                # keep an explicit self-closing tag self-closing: without the "/", the node would
                # swallow its following siblings up to the next matching closer
                opening = opening[:-1] + " /]"
            result = replace_span(src, node.start, node.open_end, opening)
        else:
            if len(a.args) != 2:
                ap.error(f"{a.command} needs PATH FILE")
            snippet = _read_raw(a.args[1]).strip()
            if a.command == "replace":
                result = replace_span(src, node.start, node.end, snippet)
            elif a.command == "insert-after":
                result = replace_span(src, node.end, node.end, snippet)
            else:
                result = replace_span(src, node.start, node.start, snippet)
    if a.out:
        _write_raw(a.out, result)
    else:
        sys.stdout.reconfigure(newline="")  # no translation: write result's bytes exactly as-is
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
