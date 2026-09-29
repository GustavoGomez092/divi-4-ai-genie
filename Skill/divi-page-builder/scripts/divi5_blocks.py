"""Parse, edit and serialize Divi 5 page content (WordPress block markup, `<!-- wp:divi/* {json} -->`).

Stdlib only. For well-formed input, serialize(parse(s)) == s byte-for-byte: untouched blocks reuse their
source spans. Blocks that are new (start == -1) or edited (dirty=True) are written in WordPress's canonical
form (get_comment_delimited_block_content() + serialize_block_attributes(), wp-includes/blocks.php).
Block.attrs holds the decoded JSON; Block.raw_json the exact source text of it.
"""
from __future__ import annotations

import bisect
import json
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Iterator, List, Optional, Tuple, Union

# WP_Block_Parser::next_token() (wp-includes/class-wp-block-parser.php). PHP's possessive `*+` is emulated
# with an atomic lookahead + backreference (Python 3.9 has no possessive quantifiers); re.A keeps `\s`
# to ASCII whitespace like PCRE without /u.
BLOCK_RE = re.compile(
    r"<!--\s+(?P<closer>/)?wp:(?P<ns>[a-z][a-z0-9_-]*/)?(?P<name>[a-z][a-z0-9_-]*)\s+"
    r"(?P<attrs>\{(?=(?P<body>(?:[^}]+|\}+(?=\})|(?!\}\s+/?-->).)*))(?P=body)\}\s+)?"
    r"(?P<void>/)?-->",
    re.S | re.A)
_PATH_PART = re.compile(r"^([a-z][a-z0-9_-]*(?:/[a-z][a-z0-9_-]*)?)\[(\d+)\]$")
_SURROGATE_ESC = re.compile(r"\\u[dD][89a-fA-F]")
# serialize_block_attributes(): strtr() pairs, applied in one left-to-right pass.
_WP_ESCAPES = {"\\\\": "\\u005c", "--": "\\u002d\\u002d", "<": "\\u003c", ">": "\\u003e", "&": "\\u0026",
               '\\"': "\\u0022"}
_WP_ESCAPE_RE = re.compile(r'\\\\|--|<|>|&|\\"')
_INT64 = (-2 ** 63, 2 ** 63 - 1)

BREAKPOINTS = ("desktop", "tablet", "phone", "phoneWide", "tabletWide", "widescreen", "ultraWide")
# Pseudo-breakpoints Divi's converter writes into module.decoration.disabledOn (convertDisabledOnBreakpoint).
DISABLED_ON_BREAKPOINTS = ("desktopAbove", "tabletOnly")
STATES = ("value", "hover", "sticky", "focus", "checked", "active", "disabled")
NON_RESPONSIVE = ("builderVersion", "modulePreset", "groupPreset", "locked")
_BP_SET, _STATE_SET = frozenset(BREAKPOINTS + DISABLED_ON_BREAKPOINTS), frozenset(STATES)


@dataclass
class Problem:
    code: str
    message: str
    offset: int


@dataclass
class Freeform:
    value: str
    start: int = -1
    end: int = -1


@dataclass
class Block:
    name: str
    attrs: dict
    raw_json: str = ""
    children: list = field(default_factory=list)
    start: int = -1
    open_end: int = -1
    close_start: Optional[int] = None
    end: int = -1
    self_closing: bool = False
    dirty: bool = False
    source: str = field(default="", repr=False, compare=False)

    @property
    def blocks(self) -> List["Block"]:
        return [c for c in self.children if isinstance(c, Block)]


def _short(name: str) -> str:
    return name[5:] if name.startswith("divi/") else name


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

    def walk(self) -> Iterator[Tuple[Block, str, Optional[Block]]]:
        def rec(children, prefix, parent):
            counts: dict = {}
            for child in children:
                if isinstance(child, Block):
                    idx = counts.get(child.name, 0)
                    counts[child.name] = idx + 1
                    seg = f"{_short(child.name)}[{idx}]"
                    path = f"{prefix} > {seg}" if prefix else seg
                    yield child, path, parent
                    yield from rec(child.children, path, child)
        yield from rec(self.nodes, "", None)

    def find(self, path: str) -> Optional[Block]:
        children, node = self.nodes, None
        for part in (p.strip() for p in path.split(">")):
            m = _PATH_PART.match(part)
            if not m:
                raise ValueError(f"bad path segment {part!r}")
            name = m.group(1) if "/" in m.group(1) else "divi/" + m.group(1)
            same = [c for c in children if isinstance(c, Block) and c.name == name]
            idx = int(m.group(2))
            if idx >= len(same):
                return None
            node = same[idx]
            children = node.children
        return node

    def sections(self) -> List[Block]:
        tops = [n for n in self.nodes if isinstance(n, Block)]
        holders = [b for b in tops if b.name == "divi/placeholder"]
        pool = [c for h in holders for c in h.children] if holders else tops
        return [b for b in pool if isinstance(b, Block) and b.name == "divi/section"]


def _reject_constant(name: str):
    raise ValueError(f"{name} is not valid JSON")


def _loads(raw: str) -> dict:
    """json_decode($raw, true) semantics: NaN/Infinity and unpaired surrogates are errors, as in PHP."""
    obj = json.loads(raw, parse_constant=_reject_constant)
    if _SURROGATE_ESC.search(raw):
        try:
            json.dumps(obj, ensure_ascii=False).encode("utf-8")
        except UnicodeEncodeError:
            raise ValueError("unpaired UTF-16 surrogate") from None
    return obj


def parse(source: str) -> Document:
    problems: List[Problem] = []
    roots: list = []
    stack: List[Block] = []
    pos = 0

    def container() -> list:
        return stack[-1].children if stack else roots

    for m in BLOCK_RE.finditer(source):
        start, end = m.start(), m.end()
        if start > pos:
            container().append(Freeform(source[pos:start], pos, start))
        pos = end
        name = (m.group("ns") or "core/") + m.group("name")
        if m.group("closer"):
            if not stack:
                problems.append(Problem("E5_STRAY_CLOSE", f"<!-- /wp:{name} --> has no opening block", start))
                container().append(Freeform(m.group(0), start, end))
                continue
            if stack[-1].name != name:
                problems.append(Problem("E5_MISNESTED", f"<!-- /wp:{name} --> closes {stack[-1].name}, which is "
                                                        f"still open", start))
                if not any(b.name == name for b in stack):
                    container().append(Freeform(m.group(0), start, end))
                    continue
                while stack[-1].name != name:
                    inner = stack.pop()
                    inner.close_start = inner.end = start
            block = stack.pop()
            block.close_start, block.end = start, end
            continue
        raw = m.group("attrs")
        raw_json = raw.rstrip(" \t\n\r\f\v") if raw else ""
        attrs: dict = {}
        if raw_json:
            try:
                attrs = _loads(raw_json)
            except ValueError as e:
                problems.append(Problem("E5_BAD_JSON", f"{name}: attributes are not valid JSON ({e})", start))
        void = bool(m.group("void"))
        block = Block(name, attrs, raw_json, [], start, end, None, end, void, source=source)
        container().append(block)
        if not void:
            stack.append(block)
    if pos < len(source):
        container().append(Freeform(source[pos:], pos, len(source)))
    while stack:
        block = stack.pop()
        problems.append(Problem("E5_UNCLOSED", f"{block.name} is never closed", block.start))
        block.close_start = block.end = len(source)
    return Document(source, roots, problems)


# ---- canonical (WordPress) serialization -------------------------------------------------------------

def _phpify(v):
    """What json_decode($json, true) + json_encode() does to the shape: {} -> [], {"0":…,"1":…} -> list,
    integers outside int64 -> float."""
    if isinstance(v, dict):
        if not v:
            return []
        items = [(str(k), _phpify(x)) for k, x in v.items()]
        if all(k == str(i) for i, (k, _) in enumerate(items)):
            return [x for _, x in items]
        return dict(items)
    if isinstance(v, (list, tuple)):
        return [_phpify(x) for x in v]
    if isinstance(v, int) and not isinstance(v, bool) and not _INT64[0] <= v <= _INT64[1]:
        return float(v)
    return v


def _php_float(x: float) -> str:
    """PHP json_encode() with serialize_precision=-1: shortest digits, php_gcvt(precision 17) layout."""
    if x != x or x in (float("inf"), float("-inf")):
        raise ValueError("PHP cannot JSON-encode NaN or Infinity")
    if x == 0:
        return "-0" if str(x).startswith("-") else "0"
    sign, digits, exp = Decimal(repr(x)).as_tuple()
    decpt = len(digits) + exp
    ds = "".join(map(str, digits)).rstrip("0") or "0"
    neg = "-" if sign else ""
    if decpt < -3 or decpt > 17:
        e = decpt - 1
        return f"{neg}{ds[0]}.{ds[1:] or '0'}e{'-' if e < 0 else '+'}{abs(e)}"
    if decpt <= 0:
        return f"{neg}0.{'0' * -decpt}{ds}"
    if len(ds) <= decpt:
        return neg + ds + "0" * (decpt - len(ds))
    return f"{neg}{ds[:decpt]}.{ds[decpt:]}"


def _encode(v) -> str:
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return _php_float(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False).replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    if isinstance(v, list):
        return "[" + ",".join(_encode(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ",".join(_encode(k) + ":" + _encode(x) for k, x in v.items()) + "}"
    raise TypeError(f"cannot encode {type(v).__name__} as block JSON")


def canonical_json(attrs) -> str:
    """Byte-identical to WordPress serialize_block_attributes(json_decode(<json of attrs>, true))."""
    return _wp_escape(_encode(_phpify(attrs)))


def _wp_escape(encoded: str) -> str:
    return _WP_ESCAPE_RE.sub(lambda m: _WP_ESCAPES[m.group(0)], encoded)


def _delimit(block: Block, inner: str) -> str:
    name = block.name[5:] if block.name.startswith("core/") else block.name
    php_attrs = _phpify(block.attrs)  # get_comment_delimited_block_content() omits empty() attributes
    attrs = _wp_escape(_encode(php_attrs)) + " " if php_attrs else ""
    if not inner:
        return f"<!-- wp:{name} {attrs}/-->"
    return f"<!-- wp:{name} {attrs}-->{inner}<!-- /wp:{name} -->"


def render_block(block: Union[Block, Freeform]) -> str:
    """Canonical text of one block and all its children."""
    if isinstance(block, Freeform):
        return block.value
    return _delimit(block, "".join(render_block(c) for c in block.children))


def _serialize_node(node: Union[Block, Freeform]) -> str:
    if isinstance(node, Freeform):
        return node.value
    inner = "".join(_serialize_node(c) for c in node.children)
    if node.dirty or node.start < 0 or (node.self_closing and inner):
        return _delimit(node, inner)
    src = node.source
    close = src[node.close_start:node.end] if node.close_start is not None else ""
    return src[node.start:node.open_end] + inner + close


def serialize(doc_or_nodes: Union[Document, list]) -> str:
    nodes = doc_or_nodes.nodes if isinstance(doc_or_nodes, Document) else doc_or_nodes
    return "".join(_serialize_node(n) for n in nodes)


def new_block(name: str, attrs: Optional[dict] = None, children: Optional[list] = None) -> Block:
    return Block(name if "/" in name else "divi/" + name, dict(attrs or {}), children=list(children or []))


def wrap_placeholder(blocks: list) -> List[Block]:
    blocks = list(blocks)
    if len(blocks) == 1 and isinstance(blocks[0], Block) and blocks[0].name == "divi/placeholder":
        return blocks
    return [new_block("placeholder", None, blocks)]


# ---- attribute access --------------------------------------------------------------------------------

def _keys(dotted: str, breakpoint: Optional[str], state: Optional[str]) -> List[str]:
    keys = dotted.split(".")
    if breakpoint is not None:
        keys.append(breakpoint)
        if state is not None:
            keys.append(state)
    return keys


def get_attr(block: Block, dotted: str, breakpoint: Optional[str] = "desktop", state: Optional[str] = "value",
             default=None):
    """attrs[a][b]…[breakpoint][state]; pass breakpoint=None for non-responsive keys like builderVersion."""
    cur = block.attrs
    for k in _keys(dotted, breakpoint, state):
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def set_attr(block: Block, dotted: str, value, breakpoint: Optional[str] = "desktop",
             state: Optional[str] = "value") -> None:
    keys = _keys(dotted, breakpoint, state)
    if not isinstance(block.attrs, dict):
        block.attrs = {}
    cur = block.attrs
    for k in keys[:-1]:
        nxt = cur.get(k)
        if nxt is None or nxt == []:  # PHP's empty object decodes to []
            nxt = cur[k] = {}
        elif not isinstance(nxt, dict):
            raise TypeError(f"{block.name}: {k!r} in {dotted!r} holds {type(nxt).__name__}, not an object")
        cur = nxt
    cur[keys[-1]] = value
    block.dirty = True


def is_responsive(d) -> bool:
    """True for a {breakpoint: {state: value}} object (disabledOn's pseudo-breakpoints included)."""
    if not isinstance(d, dict):
        return False
    return bool(d) and all(k in _BP_SET for k in d) and all(
        isinstance(s, dict) and s and all(k in _STATE_SET for k in s) for s in d.values())


def iter_leaves(attrs, _prefix: str = "") -> Iterator[Tuple[str, Optional[str], Optional[str], object]]:
    """Yield (attr path, breakpoint, state, value); breakpoint/state are None for non-responsive values."""
    if not isinstance(attrs, dict):
        return
    for k, v in attrs.items():
        path = f"{_prefix}.{k}" if _prefix else k
        if isinstance(v, dict):
            if is_responsive(v):
                for bp, states in v.items():
                    for st, val in states.items():
                        yield path, bp, st, val
            else:
                yield from iter_leaves(v, path)
        else:
            yield path, None, None, v


def _object_end(s: str, i: int) -> Optional[int]:
    """Index just past the JSON object starting at s[i] (braces counted outside strings)."""
    if i >= len(s) or s[i] != "{":
        return None
    depth, in_str, k = 0, False, i
    while k < len(s):
        c = s[k]
        if in_str:
            if c == "\\":
                k += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return k + 1
        k += 1
    return None


def variable_refs(value) -> List[dict]:
    """Every `$variable({...})$` (global colors, fonts, dynamic content) inside a string, decoded."""
    if not isinstance(value, str):
        return []
    out, i, marker = [], 0, "$variable("
    while True:
        i = value.find(marker, i)
        if i < 0:
            return out
        j = i + len(marker)
        end = _object_end(value, j)
        if end is not None and value.startswith(")$", end):
            try:
                obj = json.loads(value[j:end])
            except ValueError:
                obj = None
            if isinstance(obj, dict):
                out.append(obj)
            i = end + 2
        else:
            i = j
