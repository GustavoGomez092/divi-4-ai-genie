"""Local-image detection shared by publish.py (uploads to the Media Library) and preview.py
(embeds/serves them locally), so both use exactly the same rule: a value in an image attribute
that is `file://…`, `./…` or `../…`, resolved against the page file's own directory.

publish.py's `draft`/`publish` upload every local reference this module finds; preview.py's
`render` embeds them as `data:` URIs and `serve` routes them through a per-request allowlist —
neither preview ever uploads anything or contacts WordPress.
"""
from __future__ import annotations

import base64
import hashlib
import sys
from pathlib import Path
from typing import Callable, Dict, Iterator, Optional, Tuple
from urllib.parse import unquote, urlparse

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


def iter_local_images(doc: Document, base_dir: Path) -> Iterator[Tuple[Node, str, Path]]:
    """Every (node, attr, local path) for local image references in *doc*, resolved against
    base_dir. Does not check whether the file exists -- callers decide what to do about that."""
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
