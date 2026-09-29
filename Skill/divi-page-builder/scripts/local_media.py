"""Local-image detection shared by publish.py (uploads to the Media Library) and preview.py
(embeds/serves them locally), so both use exactly the same rule: a value in an image attribute
that is `file://…`, `./…` or `../…`, resolved against the page file's own directory.

Divi 5 block documents (divi5_blocks.Document): the image attributes are the leaves the compiled Divi 5
schema types `image` (`image.innerContent` `src`, blurb `imageIcon.innerContent` `src`, background
`image.url`, team member `image.innerContent` `url`, ...). iter_local_images yields an Image5Ref for them,
set_image5 rewrites one leaf (only that key: the image value has no `id` in Divi 5, and Divi finds the
attachment from the URL), and the block is re-serialized because set_attr marks it dirty.

publish.py's `draft`/`publish` upload every local reference this module finds; preview.py's
`render` embeds them as `data:` URIs and `serve` routes them through a per-request allowlist —
neither preview ever uploads anything or contacts WordPress.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterator, Optional, Tuple, Union
from urllib.parse import unquote, urlparse

import divi5_blocks
from divi5_checks_values import _alt_text
from divi5_schema import load_schema5
from divi_checks_values import IMAGE_ATTRS
from divi_shortcode import Document, Node, escape_attr_value, parse, serialize

LOCAL_PREFIXES = ("file://", "./", "../")

# jpg/jpeg/png/gif/webp/svg, per the brief: the extensions render/serve recognize as embeddable
# or servable local images.
IMAGE_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif",
             ".webp": "image/webp", ".svg": "image/svg+xml"}


def is_image_attr(attr: str) -> bool:
    return attr in IMAGE_ATTRS or attr.endswith("_image")


def local_path(value: str, base_dir: Path) -> Optional[Path]:
    """The filesystem path a local image *value* refers to (file://, ./, ../), resolved against
    base_dir (the page file's own directory) -- or None if *value* isn't a local reference."""
    if value.startswith("file://"):
        return Path(unquote(urlparse(value).path))
    if value.startswith(("./", "../")):
        return (base_dir / value).resolve()
    return None


@dataclass(frozen=True)
class Image5Ref:
    """Where one image leaf sits in a Divi 5 block: attrs[attr][breakpoint][state], then `sub` (a dotted key
    path inside that value; None when the value itself is the URL string)."""
    attr: str
    breakpoint: str
    state: str
    sub: Optional[str]

    @property
    def label(self) -> str:
        return f"{self.attr}.{self.breakpoint}.{self.state}" + (f".{self.sub}" if self.sub else "")


def _iter_local_images5(doc: "divi5_blocks.Document", base_dir: Path,
                        schema5=None) -> Iterator[Tuple["divi5_blocks.Block", Image5Ref, Path]]:
    schema5 = schema5 or load_schema5()
    for block, _path, _parent in doc.walk():
        mod = schema5.module(block.name)
        if mod is None:
            continue
        for attr, bp, st, value in divi5_blocks.iter_leaves(block.attrs):
            if bp is None:
                continue
            for res, v in mod.walk_value(attr, bp, st, value):
                if res.status != "ok" or not res.leaf or res.leaf.get("type") != "image" or not isinstance(v, str):
                    continue
                local = local_path(v, base_dir)
                if local is None:
                    continue
                yield block, Image5Ref(attr, bp, st, res.sub_path if res.attr_path == attr else None), local


def set_image5(block: "divi5_blocks.Block", ref: Image5Ref, url: str) -> None:
    """Set one image leaf to *url*; nothing else in the block changes (builderVersion included)."""
    if ref.sub is None:
        divi5_blocks.set_attr(block, ref.attr, url, ref.breakpoint, ref.state)
        return
    value = copy.deepcopy(divi5_blocks.get_attr(block, ref.attr, ref.breakpoint, ref.state))
    keys = ref.sub.split(".")
    cur = value
    for k in keys[:-1]:
        cur = cur[k]
    cur[keys[-1]] = url
    divi5_blocks.set_attr(block, ref.attr, value, ref.breakpoint, ref.state)


def image_alt5(block: "divi5_blocks.Block", ref: Image5Ref) -> str:
    """The alt text the page gives this image: the `alt` (else `titleText`) beside the leaf, else (for the
    image module) the converter's module.decoration.attributes alt; "" when there is none."""
    if ref.sub is not None:
        parent = divi5_blocks.get_attr(block, ref.attr, ref.breakpoint, ref.state)
        for k in ref.sub.split(".")[:-1]:
            parent = parent.get(k) if isinstance(parent, dict) else None
        if isinstance(parent, dict):
            for key in ("alt", "titleText"):
                if isinstance(parent.get(key), str) and parent[key].strip():
                    return parent[key]
    if ref.attr == "image.innerContent":
        return _alt_text(block)
    return ""


def iter_local_images(doc: Union[Document, "divi5_blocks.Document"],
                      base_dir: Path) -> Iterator[Tuple[Union[Node, "divi5_blocks.Block"], Union[str, Image5Ref], Path]]:
    """Every (node, attr, local path) for local image references in *doc*, resolved against
    base_dir. Does not check whether the file exists -- callers decide what to do about that.
    For a Divi 5 block document: (block, Image5Ref, local path)."""
    if isinstance(doc, divi5_blocks.Document):
        yield from _iter_local_images5(doc, base_dir)
        return
    for node, _path, _parent in doc.walk():
        for attr in list(node.attrs):
            if not is_image_attr(attr):
                continue
            local = local_path(node.value(attr), base_dir)
            if local is None:
                continue
            yield node, attr, local


def image_mime_type(path: Path) -> Optional[str]:
    """The image MIME type for *path*'s extension, or None if it isn't a recognized image type."""
    return IMAGE_MIME.get(path.suffix.lower())


def data_uri(path: Path) -> Optional[str]:
    """A data: URI for *path*, or None if its extension isn't a recognized image type."""
    mime = image_mime_type(path)
    if mime is None:
        return None
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def _default_warn(message: str) -> None:
    print(message, file=sys.stderr)


def embed_local_images(source: str, base_dir: Path, warn: Optional[Callable[[str], None]] = None) -> str:
    """Replace every local image reference in *source* that exists on disk (and is a recognized
    image type) with a data: URI, so the rendered page is standalone. A local reference that's
    missing, or whose extension isn't recognized, is left as-is and reported via *warn* (default:
    a one-line stderr message naming the attr and path) -- this never raises, so the preview still
    renders."""
    warn = warn or _default_warn
    doc = parse(source)
    for node, attr, local in iter_local_images(doc, base_dir):
        if not local.is_file():
            warn(f"{node.tag} {attr}: local image not found: {local}")
            continue
        uri = data_uri(local)
        if uri is None:
            warn(f"{node.tag} {attr}: not a recognized image type: {local}")
            continue
        node.attrs[attr] = escape_attr_value(uri, attr)
    return serialize(doc)


def route_token(path: Path) -> str:
    """A stable, urlsafe token identifying *path*, used as the last segment of its serve route."""
    return hashlib.sha256(str(path).encode()).hexdigest()[:32]


def rewrite_for_serve(source: str, base_dir: Path, route_prefix: str) -> Tuple[str, Dict[str, Path]]:
    """Rewrite local image references in *source* to `route_prefix + token` URLs, and return the
    rewritten source plus a {token: resolved path} allowlist -- exactly (and only) the local,
    existing, image-mime files this page's own attributes reference, for the caller to serve from.
    A missing (or non-image) local reference is left as-is: nothing new is served for it."""
    doc = parse(source)
    allowed: Dict[str, Path] = {}
    for node, attr, local in iter_local_images(doc, base_dir):
        if not local.is_file() or image_mime_type(local) is None:
            continue
        token = route_token(local)
        allowed[token] = local
        node.attrs[attr] = escape_attr_value(route_prefix + token, attr)
    return serialize(doc), allowed
