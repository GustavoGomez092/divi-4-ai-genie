#!/usr/bin/env python3
"""Surgical edits to a Divi page: everything outside the targeted node stays byte-identical.

Usage: page_edit.py PAGE outline
       page_edit.py PAGE extract PATH
       page_edit.py PAGE replace PATH FILE | insert-after PATH FILE | insert-before PATH FILE
       page_edit.py PAGE set-attr PATH NAME VALUE      (VALUE is plain text; it is escaped for you)
       page_edit.py PAGE delete PATH
Options: --out FILE (default: stdout); --site-major N or --tokens tokens.json (refuse content in the wrong
format for the site: Divi 4 shortcode on a Divi 5 site, Divi 5 blocks on a Divi 4 site).

Divi 4 shortcode: PATH looks like et_pb_section[1] > et_pb_row[0] > et_pb_column[2] > et_pb_blurb[0].

Divi 5 blocks (auto-detected): PATH looks like placeholder[0] > section[1] > row[0] > column[2] > blurb[0]; the
leading "placeholder[0] >" may be left out. set-attr takes a dotted attribute path and a VALUE that is JSON when it
parses as JSON, otherwise a string:
       page_edit.py PAGE set-attr PATH title.innerContent "New headline"
       page_edit.py PAGE set-attr PATH button.decoration.background '{"color":"#0f172a"}' --state hover
--breakpoint (default desktop) and --state (default value) pick the responsive slot; builderVersion,
modulePreset, groupPreset, locked, existing non-responsive leaves and a NAME that already spells the slot
(button.innerContent.desktop.value.text) are written without one (or pass --breakpoint none). A NAME that reaches
inside a responsive value (button.decoration.background.color) sets just that key in the chosen slot.
Only the edited block is re-rendered (canonically; its builderVersion is kept); replace/insert-* splice FILE's
block markup verbatim at the target's span boundaries. Mutating verbs refuse a page with block parse problems
(outline/extract still run, with a warning), and refuse a FILE that isn't clean Divi 5 block markup.

Exit status: 0 = done, 1 = refused (wrong format for the site, parse problems, bad FILE), 2 = usage or no such node.

Note: the page (and any snippet FILE for replace/insert-after/insert-before) is read and written
with no newline translation, so CRLF/LF line endings outside the target span are never rewritten;
a snippet file's own line endings are kept as provided (only leading/trailing whitespace is
stripped).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from divi_shortcode import build_open_tag, escape_attr_value, parse, replace_span  # noqa: E402
import divi5_blocks  # noqa: E402
from divi_format import detect_content, major_from_version  # noqa: E402

PROG = "page_edit.py"
MUTATING = ("replace", "insert-after", "insert-before", "set-attr", "delete")
_HEADING_HTML = re.compile(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", re.S | re.I)
_TAG = re.compile(r"<[^>]+>")


class Refused(Exception):
    """The edit is refused (exit 1); the message says why."""


class NotFound(Exception):
    """No such node, or a malformed PATH / attribute path (exit 2)."""


def _read_raw(path) -> str:
    # newline="" disables universal-newline translation: \r\n, \r and \n all come through exactly
    # as stored on disk, so byte offsets computed against this string match the file's real bytes.
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def _write_raw(path, data: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(data)


def _warn(msg: str) -> None:
    print(f"{PROG}: warning: {msg}", file=sys.stderr)


# ---- site format -------------------------------------------------------------------------------------------

def _site_major(a):
    """--site-major, else tokens.json site.divi_major (or site.divi_version); None when unknown."""
    if a.site_major is not None:
        return a.site_major
    if not a.tokens:
        return None
    with open(a.tokens, encoding="utf-8") as f:
        tokens = json.load(f)
    site = tokens.get("site") if isinstance(tokens, dict) else None
    site = site if isinstance(site, dict) else {}
    major = site.get("divi_major")
    if isinstance(major, int) and not isinstance(major, bool):
        return major
    return major_from_version(site.get("divi_version") if isinstance(site.get("divi_version"), str) else None)


def _format_refusal(kind: str, major) -> None:
    if kind == "mixed":
        raise Refused("this page mixes Divi 4 shortcode and Divi 5 blocks; it can't be edited safely. Divi 5 sites "
                      "take divi/* blocks only, Divi 4 sites shortcode only (run scripts/validate.py).")
    if major is None:
        return
    if kind == "shortcode" and major >= 5:
        raise Refused("this is Divi 4 shortcode; the site runs Divi 5 — write Divi 5 blocks "
                      "(reference/divi5/page-format.md). A Divi 4 page on a Divi 5 site renders through a degraded "
                      "legacy path and is never converted.")
    if kind == "blocks" and major < 5:
        raise Refused(f"this is Divi 5 block content; the site runs Divi {major} — write Divi 4 shortcode "
                      "(reference/page-format.md).")


# ---- Divi 5 blocks -----------------------------------------------------------------------------------------

def _problem_lines(doc, label: str):
    for p in doc.problems:
        line, col = doc.line_col(p.offset)
        yield f"{label}:{line}:{col} {p.code}: {p.message}"


def _find_block(doc, path: str):
    """doc.find() that also takes the short form without `placeholder[0] >` (and the long form on a page that
    has no placeholder wrapper). ValueError on a malformed segment."""
    parts = [p.strip() for p in path.split(">")]
    first = parts[0].split("[")[0]
    first = first[5:] if first.startswith("divi/") else first
    tops = [n for n in doc.nodes if isinstance(n, divi5_blocks.Block)]
    wrapped = any(b.name == "divi/placeholder" for b in tops)
    if wrapped and first != "placeholder":
        parts = ["placeholder[0]"] + parts
    elif not wrapped and first == "placeholder" and parts[0].endswith("[0]") and len(parts) > 1:
        parts = parts[1:]
    return doc.find(" > ".join(parts))


def _text(value):
    if isinstance(value, dict):
        value = value.get("text")
    return value if isinstance(value, str) else None


def _heading_text(block):
    """What an outline reader recognises a module by: its title (heading, blurb, cta, toggle, slide, header…),
    else the first HTML heading in its content, else a button's text."""
    title = _text(divi5_blocks.get_attr(block, "title.innerContent"))
    if not title:
        content = _text(divi5_blocks.get_attr(block, "content.innerContent"))
        m = _HEADING_HTML.search(content or "")
        title = _TAG.sub("", m.group(1)) if m else None
    if not title:
        title = _text(divi5_blocks.get_attr(block, "button.innerContent"))
    if not title:
        return None
    title = " ".join(title.split())
    return title if len(title) <= 70 else title[:67] + "..."


def _outline5(doc) -> str:
    lines = []
    for b, path, _ in doc.walk():
        label = _text(divi5_blocks.get_attr(b, "module.meta.adminLabel"))
        heading = _heading_text(b)
        extra = f'  title="{heading}"' if heading else ""
        lines.append(f"{path}  admin_label={label}{extra}  ({b.end - b.start} chars)")
    return "\n".join(lines) + "\n"


def _load_snippet5(path: str, target) -> str:
    """FILE's block markup (stripped), refused unless it is clean Divi 5 block markup; warns about blocks
    without builderVersion (they are kept as provided, never filled in)."""
    text = _read_raw(path).strip()
    kind = detect_content(text)
    if kind != "blocks":
        raise Refused(f"{path}: this is {kind} content, not Divi 5 block markup; the page is Divi 5 blocks")
    sdoc = divi5_blocks.parse(text)
    if sdoc.problems:
        raise Refused("\n".join(_problem_lines(sdoc, path))
                      + f"\nrefusing to insert: {len(sdoc.problems)} block parse problem(s) in {path}")
    stray = next((n for n in sdoc.nodes if isinstance(n, divi5_blocks.Freeform) and n.value.strip()), None)
    if stray is not None:
        line, col = sdoc.line_col(stray.start)
        raise Refused(f"{path}:{line}:{col} text outside any block ({stray.value.strip()[:40]!r}); "
                      "a snippet must be whole blocks")
    walked = list(sdoc.walk())
    if target.name != "divi/placeholder" and any(b.name == "divi/placeholder" for b, _, _ in walked):
        raise Refused(f"{path}: holds a divi/placeholder wrapper; the page already has one — "
                      "insert the sections inside it, not the wrapper")
    for b, bpath, _ in walked:
        version = b.attrs.get("builderVersion")
        if b.name.startswith("divi/") and b.name != "divi/placeholder" and not (isinstance(version, str) and version):
            _warn(f"{path}: {bpath} [{b.name}] has no builderVersion; it is inserted as provided. Blocks you create "
                  "carry the site's Divi version (reference/divi5/page-format.md#builderversion)")
    return text


def _json_or_text(raw: str):
    def reject(name):
        raise ValueError(name)
    try:
        return json.loads(raw, parse_constant=reject)
    except ValueError:
        return raw


def _inside_responsive(block, keys):
    """i when keys[:i] names a responsive attribute ({breakpoint: {state: value}}) and keys[i:] reach inside its
    value (button.decoration.background.color); None otherwise."""
    for i in range(1, len(keys)):
        cur = divi5_blocks.get_attr(block, ".".join(keys[:i]), breakpoint=None)
        if not isinstance(cur, dict):
            return None
        if divi5_blocks._is_responsive(cur):
            return i
    return None


def _set_attr5(ap, a, src, block) -> str:
    if len(a.args) != 3:
        ap.error("set-attr needs PATH NAME VALUE")
    dotted, value = a.args[1], _json_or_text(a.args[2])
    keys, state = dotted.split("."), a.state or "value"
    named = any(bp in divi5_blocks.BREAKPOINTS and st in divi5_blocks.STATES for bp, st in zip(keys, keys[1:]))
    inside = None if named or a.breakpoint == "none" else _inside_responsive(block, keys)
    if inside is not None and keys[inside] in divi5_blocks.BREAKPOINTS + divi5_blocks.STATES:
        ap.error(f"{dotted}: name both the breakpoint and the state ({'.'.join(keys[:inside])}.<breakpoint>.<state>"
                 "...), or use --breakpoint/--state")
    if inside is not None:
        # Write the one key inside the slot's value, keeping the value's other keys (a background's gradient
        # stays when only its color changes).
        dotted = ".".join(keys[:inside] + [a.breakpoint or "desktop", state] + keys[inside:])
        breakpoint = None
    elif a.breakpoint is not None:
        breakpoint = None if a.breakpoint == "none" else a.breakpoint
    else:
        existing = divi5_blocks.get_attr(block, dotted, breakpoint=None)
        # Top-level keys that never hold a {breakpoint: {state: value}} object, a NAME that already spells the
        # slot, or an existing non-responsive leaf ([] is PHP's empty object: not a leaf).
        flat = (keys[0] in divi5_blocks.NON_RESPONSIVE or named
                or (existing is not None and existing != [] and not isinstance(existing, dict)))
        breakpoint = None if flat else "desktop"
    if breakpoint is None and inside is None and a.state not in (None, "value"):
        ap.error(f"--state {a.state} needs a responsive attribute ({dotted} is written without a breakpoint)")
    if breakpoint is not None:
        existing = divi5_blocks.get_attr(block, dotted, breakpoint=None)
        if isinstance(existing, dict) and existing and not divi5_blocks._is_responsive(existing):
            raise NotFound(f"{dotted} is a group of attributes on {block.name}, not one value; name one inside it "
                           f"(e.g. {dotted}.{next(iter(existing))})")
    if keys[0] == "builderVersion":
        _warn("changing builderVersion on an existing block changes which render-time migrations Divi runs on it; "
              "leave it as it is unless you mean that")
    try:
        divi5_blocks.set_attr(block, dotted, value, breakpoint=breakpoint, state=state)
    except TypeError as e:
        raise NotFound(str(e)) from None
    # Only this block is dirty: serialize() re-renders its own delimiters and reuses every child's source span.
    return src[:block.start] + divi5_blocks.serialize([block]) + src[block.end:]


def _edit_blocks(ap, a, src) -> str:
    doc = divi5_blocks.parse(src)
    if doc.problems:
        lines = list(_problem_lines(doc, a.page))
        if a.command in MUTATING:
            raise Refused("\n".join(lines) + f"\nrefusing to edit: {len(lines)} block parse problem(s) "
                                             "(an edit could drop a block's attributes); run scripts/validate.py")
        for line in lines:
            _warn(line)
    if a.command == "outline":
        return _outline5(doc)
    if not a.args:
        ap.error("PATH is required")
    try:
        block = _find_block(doc, a.args[0])
    except ValueError as e:
        raise NotFound(f"bad path {a.args[0]!r}: {e}") from None
    if block is None:
        raise NotFound(f"no node at {a.args[0]}")
    if a.command == "extract":
        return src[block.start:block.end]
    if a.command == "delete":
        return src[:block.start] + src[block.end:]
    if a.command == "set-attr":
        return _set_attr5(ap, a, src, block)
    if len(a.args) != 2:
        ap.error(f"{a.command} needs PATH FILE")
    snippet = _load_snippet5(a.args[1], block)
    if a.command == "replace":
        return src[:block.start] + snippet + src[block.end:]
    at = block.end if a.command == "insert-after" else block.start
    return src[:at] + snippet + src[at:]


# ---- Divi 4 shortcode --------------------------------------------------------------------------------------

def _edit_shortcode(ap, a, src) -> str:
    if a.breakpoint is not None or a.state is not None:
        ap.error("--breakpoint/--state apply to Divi 5 block pages only")
    doc = parse(src)
    if a.command == "outline":
        lines = [f"{path}  admin_label={n.value('admin_label')}  ({n.end - n.start} chars)" for n, path, _ in doc.walk()]
        return "\n".join(lines) + "\n"
    if not a.args:
        ap.error("PATH is required")
    node = doc.find(a.args[0])
    if node is None:
        raise NotFound(f"no node at {a.args[0]}")
    if a.command == "extract":
        return src[node.start:node.end]
    if a.command == "delete":
        return replace_span(src, node.start, node.end, "")
    if a.command == "set-attr":
        if len(a.args) != 3:
            ap.error("set-attr needs PATH NAME VALUE")
        node.attrs[a.args[1]] = escape_attr_value(a.args[2], a.args[1])
        opening = build_open_tag(node)
        if node.raw_open[:-1].rstrip().endswith("/"):
            # keep an explicit self-closing tag self-closing: without the "/", the node would
            # swallow its following siblings up to the next matching closer
            opening = opening[:-1] + " /]"
        return replace_span(src, node.start, node.open_end, opening)
    if len(a.args) != 2:
        ap.error(f"{a.command} needs PATH FILE")
    snippet = _read_raw(a.args[1]).strip()
    if detect_content(snippet) in ("blocks", "mixed"):
        raise Refused(f"{a.args[1]}: this is Divi 5 block markup; the page is Divi 4 shortcode")
    if a.command == "replace":
        return replace_span(src, node.start, node.end, snippet)
    if a.command == "insert-after":
        return replace_span(src, node.end, node.end, snippet)
    return replace_span(src, node.start, node.start, snippet)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("command", choices=["outline", "extract", "replace", "insert-after", "insert-before", "set-attr", "delete"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--out")
    ap.add_argument("--site-major", type=int, help="the site's Divi major version (4 or 5)")
    ap.add_argument("--tokens", help="tokens.json; its site.divi_major / site.divi_version gives the site's version")
    ap.add_argument("--breakpoint", choices=divi5_blocks.BREAKPOINTS + ("none",),
                    help="Divi 5 set-attr: responsive slot (default desktop)")
    ap.add_argument("--state", choices=divi5_blocks.STATES, help="Divi 5 set-attr: state (default value)")
    a = ap.parse_args(argv)
    src = _read_raw(a.page)
    kind = detect_content(src)
    try:
        _format_refusal(kind, _site_major(a))
        result = _edit_blocks(ap, a, src) if kind == "blocks" else _edit_shortcode(ap, a, src)
    except Refused as e:
        print(f"{PROG}: {e}", file=sys.stderr)
        return 1
    except NotFound as e:
        print(f"{PROG}: {e}", file=sys.stderr)
        return 2
    except (OSError, ValueError) as e:
        print(f"{PROG}: {e}", file=sys.stderr)
        return 2
    if a.out:
        _write_raw(a.out, result)
    else:
        sys.stdout.reconfigure(newline="")  # no translation: write result's bytes exactly as-is
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
