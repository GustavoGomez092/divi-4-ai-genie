"""Parse, edit and serialize Divi 4 page content (nested [et_pb_*] shortcodes).

Stdlib only. For well-formed input, serialize(parse(s)) == s byte-for-byte.
Attribute values in Node.attrs are kept exactly as written (still escaped);
use Node.value(name) for the unescaped value.
"""
from __future__ import annotations

import bisect
import re
from dataclasses import dataclass, field
from typing import Iterator, List, Optional, Tuple, Union

TAG_RE = re.compile(r"\[(/?)(et_pb_[A-Za-z0-9_]+)((?:[^\]\"']|\"[^\"]*\"|'[^']*')*)\]")
# WordPress get_shortcode_atts_regex(), in the same alternation order.
ATTR_RE = re.compile(
    r'([\w-]+)\s*=\s*"([^"]*)"(?:\s|$)'
    r"|([\w-]+)\s*=\s*'([^']*)'(?:\s|$)"
    r"|([\w-]+)\s*=\s*([^\s'\"]+)(?:\s|$)"
    r'|"([^"]*)"(?:\s|$)'
    r"|'([^']*)'(?:\s|$)"
    r"|(\S+)(?:\s|$)"
)
# Attributes whose backslashes Divi encodes as %92 (functions.php:2063-2067).
BACKSLASH_ATTRS = ("checkbox_options", "radio_options", "select_options", "conditional_logic_rules")
_WP_LT_OK = re.compile(r"^[^<]*(?:<[^>]*>[^<]*)*$")
_PATH_PART = re.compile(r"^(et_pb_\w+)\[(\d+)\]$")


@dataclass
class Problem:
    code: str
    message: str
    offset: int


@dataclass
class Text:
    value: str
    start: int = -1
    end: int = -1


@dataclass
class Node:
    tag: str
    attrs: dict
    start: int = -1
    open_end: int = -1
    close_start: Optional[int] = None
    end: int = -1
    raw_open: str = ""
    raw_close: str = ""
    self_closing: bool = False
    children: list = field(default_factory=list)
    orig_attrs: dict = field(default_factory=dict)
    quoting: dict = field(default_factory=dict)
    duplicate_attrs: list = field(default_factory=list)
    positional: list = field(default_factory=list)

    @property
    def content(self) -> str:
        return "".join(c.value if isinstance(c, Text) else serialize_node(c) for c in self.children)

    @property
    def modules(self) -> List["Node"]:
        return [c for c in self.children if isinstance(c, Node)]

    def value(self, attr: str, default: str = "") -> str:
        return unescape_attr_value(self.attrs.get(attr, default))


@dataclass
class Document:
    source: str
    nodes: list
    problems: List[Problem]
    _line_starts: List[int] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self._line_starts = [0] + [m.end() for m in re.finditer(r"\n", self.source)]

    def line_col(self, offset: int) -> Tuple[int, int]:
        i = bisect.bisect_right(self._line_starts, max(offset, 0)) - 1
        return i + 1, offset - self._line_starts[i] + 1

    def walk(self) -> Iterator[Tuple[Node, str, Optional[Node]]]:
        def rec(children, prefix, parent):
            counts = {}
            for child in children:
                if isinstance(child, Node):
                    idx = counts.get(child.tag, 0)
                    counts[child.tag] = idx + 1
                    path = f"{prefix} > {child.tag}[{idx}]" if prefix else f"{child.tag}[{idx}]"
                    yield child, path, parent
                    yield from rec(child.children, path, child)
        yield from rec(self.nodes, "", None)

    def find(self, path: str) -> Optional[Node]:
        children = self.nodes
        node = None
        for part in (p.strip() for p in path.split(">")):
            m = _PATH_PART.match(part)
            if not m:
                raise ValueError(f"bad path segment {part!r}")
            same = [c for c in children if isinstance(c, Node) and c.tag == m.group(1)]
            idx = int(m.group(2))
            if idx >= len(same):
                return None
            node = same[idx]
            children = node.children
        return node

    def sections(self) -> List[Node]:
        return [n for n in self.nodes if isinstance(n, Node) and n.tag == "et_pb_section"]


def parse_attrs(text: str):
    """WordPress shortcode_parse_atts(): returns (attrs, quoting, duplicates, positional)."""
    attrs, quoting, dups, positional = {}, {}, [], []
    text = re.sub("[ ​]+", " ", text)
    for m in ATTR_RE.finditer(text):
        if m.group(1) is not None:
            name, value, q = m.group(1), m.group(2), '"'
        elif m.group(3) is not None:
            name, value, q = m.group(3), m.group(4), "'"
        elif m.group(5) is not None:
            name, value, q = m.group(5), m.group(6), ""
        else:
            positional.append(next(g for g in m.groups()[6:] if g is not None))
            continue
        name = name.lower()
        if name in attrs:
            dups.append(name)
        attrs[name] = value
        quoting[name] = q
    return attrs, quoting, dups, positional


def parse(source: str) -> Document:
    problems: List[Problem] = []
    matches = list(TAG_RE.finditer(source))
    closers: dict = {}
    for m in matches:
        if m.group(1):
            closers.setdefault(m.group(2), []).append(m.start())

    roots: list = []
    stack: List[Node] = []
    pos = 0

    def container() -> list:
        return stack[-1].children if stack else roots

    def emit_text(upto: int) -> None:
        nonlocal pos
        if upto > pos:
            container().append(Text(source[pos:upto], pos, upto))
        pos = upto

    def has_closer_after(tag: str, offset: int) -> bool:
        positions = closers.get(tag, [])
        return bisect.bisect_left(positions, offset) < len(positions)

    for m in matches:
        emit_text(m.start())
        slash, tag, attr_text = m.group(1), m.group(2), m.group(3)
        if slash:
            if any(n.tag == tag for n in stack):
                while stack[-1].tag != tag:
                    orphan = stack.pop()
                    problems.append(Problem("E_UNCLOSED", f"[{orphan.tag}] is never closed (found [/{tag}] first)", orphan.start))
                    orphan.close_start = orphan.end = m.start()
                node = stack.pop()
                node.close_start, node.end, node.raw_close = m.start(), m.end(), m.group(0)
            else:
                problems.append(Problem("E_STRAY_CLOSE", f"[/{tag}] has no matching opening tag", m.start()))
                container().append(Text(m.group(0), m.start(), m.end()))
            pos = m.end()
            continue
        stripped = attr_text.rstrip()
        self_closing = stripped.endswith("/")
        if self_closing:
            attr_text = stripped[:-1]
        attrs, quoting, dups, positional = parse_attrs(attr_text)
        node = Node(tag=tag, attrs=attrs, start=m.start(), open_end=m.end(), raw_open=m.group(0),
                    orig_attrs=dict(attrs), quoting=quoting, duplicate_attrs=dups, positional=positional)
        container().append(node)
        if self_closing or not has_closer_after(tag, m.end()):
            node.self_closing = True
            node.end = m.end()
        else:
            stack.append(node)
        pos = m.end()
    emit_text(len(source))
    while stack:
        orphan = stack.pop()
        problems.append(Problem("E_UNCLOSED", f"[{orphan.tag}] is never closed", orphan.start))
        orphan.end = len(source)
    return Document(source, roots, problems)


def build_open_tag(node: Node) -> str:
    return "[" + " ".join([node.tag] + [f'{k}="{v}"' for k, v in node.attrs.items()]) + "]"


def serialize_node(node: Node) -> str:
    if node.raw_open and node.attrs == node.orig_attrs:
        opening = node.raw_open
        if node.self_closing and not node.children:
            return opening
    else:
        opening = build_open_tag(node)
    inner = "".join(c.value if isinstance(c, Text) else serialize_node(c) for c in node.children)
    return opening + inner + (node.raw_close or f"[/{node.tag}]")


def serialize(doc_or_nodes: Union[Document, list]) -> str:
    nodes = doc_or_nodes.nodes if isinstance(doc_or_nodes, Document) else doc_or_nodes
    return "".join(c.value if isinstance(c, Text) else serialize_node(c) for c in nodes)


def new_node(tag: str, attrs: Optional[dict] = None, content: str = "", children: Optional[list] = None) -> Node:
    """Build a node from plain (unescaped) attribute values."""
    escaped = {k: escape_attr_value(str(v), k) for k, v in (attrs or {}).items()}
    kids = ([Text(content)] if content else []) + list(children or [])
    return Node(tag=tag, attrs=escaped, children=kids)


def escape_attr_value(value: str, attr: str = "") -> str:
    out = value.replace('"', "%22").replace("[", "%91").replace("]", "%93")
    if attr.startswith("custom_css_") or attr in BACKSLASH_ATTRS:
        out = out.replace("\\", "%92")
    return out


def unescape_attr_value(value: str) -> str:
    for enc, dec in (("%22", '"'), ("%91", "["), ("%93", "]"), ("%92", "\\"), ("%5c", "\\"), ("%5C", "\\")):
        value = value.replace(enc, dec)
    return value


def wp_blanks_value(raw_value: str) -> bool:
    """WordPress empties a shortcode attribute containing '<' unless every '<' opens a complete tag."""
    return "<" in raw_value and not _WP_LT_OK.match(raw_value)


def replace_span(source: str, start: int, end: int, replacement: str) -> str:
    if not 0 <= start <= end <= len(source):
        raise ValueError(f"invalid span {start}:{end} for source of length {len(source)}")
    return source[:start] + replacement + source[end:]
