#!/usr/bin/env python3
"""Send Divi pages to WordPress over the REST API, authenticated with an Application Password.

  publish.py fetch   --site URL --user USER --page-id ID --out FILE
  publish.py media   --site URL --user USER FILE --alt TEXT
  publish.py draft   PAGE --site URL --user USER --title TITLE [--slug S] [--page-id ID] [--tokens tokens.json] [--page-fields JSON]
  publish.py publish --site URL --user USER --page-id ID --yes

The password is read from env WP_APP_PASSWORD and never printed. `draft` validates the page first and
refuses on errors; image attributes pointing at local files (file://, ./, ../) are uploaded to the
Media Library and rewritten. Pages are saved as drafts; `publish` requires --yes (after user approval).
Exit status: 0 ok, 1 validation errors or refused, 2 usage/HTTP/I-O error.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from divi_checks_values import IMAGE_ATTRS  # noqa: E402
from divi_schema import load_schema  # noqa: E402
from divi_shortcode import escape_attr_value, parse, serialize  # noqa: E402
from validate import validate_source  # noqa: E402

LOCAL_PREFIXES = ("file://", "./", "../")


class PublishError(Exception):
    pass


class WordPress:
    def __init__(self, site: str, user: str, password: str):
        self.base = site.rstrip("/") + "/wp-json/wp/v2"
        self.site = site.rstrip("/")
        self._auth = "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()

    def request(self, method: str, path: str, json_body=None, data: bytes = None, headers=None) -> dict:
        hdrs = {"Authorization": self._auth, "Accept": "application/json", "User-Agent": "divi-page-builder/1.0"}
        if json_body is not None:
            data = json.dumps(json_body).encode()
            hdrs["Content-Type"] = "application/json"
        hdrs.update(headers or {})
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=hdrs)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as exc:
            try:
                err = json.loads(exc.read())
                detail = f"{err.get('code', '')}: {err.get('message', '')}"
            except ValueError:
                detail = exc.reason
            raise PublishError(f"HTTP {exc.code} on {method} {path} — {detail}") from None
        except urllib.error.URLError as exc:
            raise PublishError(f"cannot reach {self.site}: {exc.reason}") from None


def upload_media(wp: WordPress, path: Path, alt: str) -> dict:
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    media = wp.request("POST", "/media", data=path.read_bytes(),
                       headers={"Content-Type": ctype, "Content-Disposition": f'attachment; filename="{path.name}"'})
    if alt:
        wp.request("POST", f"/media/{media['id']}", json_body={"alt_text": alt})
    return {"id": media["id"], "url": media["source_url"], "file": str(path)}


def _local_path(value: str, base_dir: Path):
    if value.startswith("file://"):
        return Path(unquote(urlparse(value).path))
    if value.startswith(("./", "../")):
        return (base_dir / value).resolve()
    return None


def upload_local_images(wp: WordPress, source: str, base_dir: Path):
    doc = parse(source)
    uploaded, cache = [], {}
    for node, _path, _parent in doc.walk():
        for attr in list(node.attrs):
            if attr not in IMAGE_ATTRS and not attr.endswith("_image"):
                continue
            local = _local_path(node.value(attr), base_dir)
            if local is None:
                continue
            if not local.is_file():
                raise PublishError(f"{node.tag} {attr}: local image not found: {local}")
            if local not in cache:
                alt = node.value("alt") or node.value("title_text") or local.stem.replace("-", " ")
                cache[local] = upload_media(wp, local, alt)
                uploaded.append(cache[local])
            node.attrs[attr] = escape_attr_value(cache[local]["url"], attr)
    return serialize(doc), uploaded


def _preview_url(link: str) -> str:
    return link + ("&" if "?" in link else "?") + "preview=true"


def _print(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def cmd_fetch(wp, a):
    page = wp.request("GET", f"/pages/{a.page_id}?context=edit")
    Path(a.out).write_text(page["content"]["raw"], encoding="utf-8")
    _print({"id": page["id"], "link": page.get("link", ""), "out": a.out})
    return 0


def cmd_media(wp, a):
    _print(upload_media(wp, Path(a.file), a.alt))
    return 0


def cmd_draft(wp, a):
    page_path = Path(a.page)
    source = page_path.read_text(encoding="utf-8")
    tokens = json.loads(Path(a.tokens).read_text()) if a.tokens else None
    errors = [f for f in validate_source(source, load_schema(), tokens=tokens) if f.level == "error"]
    if errors:
        for f in errors:
            print(f"{a.page}:{f.line}:{f.col} {f.code} {f.path}: {f.message}", file=sys.stderr)
        print(f"refusing to save: {len(errors)} validation error(s); run scripts/validate.py for details", file=sys.stderr)
        return 1
    content, uploaded = upload_local_images(wp, source, page_path.resolve().parent)
    body = {"title": a.title, "content": content, "status": "draft", "meta": {"_et_pb_use_builder": "on"}}
    if a.slug:
        body["slug"] = a.slug
    body.update(json.loads(a.page_fields) if a.page_fields else {})
    page = wp.request("POST", f"/pages/{a.page_id}" if a.page_id else "/pages", json_body=body)
    _print({"id": page["id"], "status": page.get("status", "draft"), "link": page.get("link", ""),
            "preview_url": _preview_url(page.get("link", "")),
            "edit_url": f"{wp.site}/wp-admin/post.php?post={page['id']}&action=edit", "uploaded": uploaded})
    return 0


def cmd_publish(wp, a):
    if not a.yes:
        print("refusing to publish without --yes (publish only after the user approves the draft)", file=sys.stderr)
        return 1
    page = wp.request("POST", f"/pages/{a.page_id}", json_body={"status": "publish"})
    _print({"id": page["id"], "status": page.get("status", ""), "link": page.get("link", "")})
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--site", required=True)
    common.add_argument("--user", required=True)
    p = sub.add_parser("fetch", parents=[common])
    p.add_argument("--page-id", type=int, required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("media", parents=[common])
    p.add_argument("file")
    p.add_argument("--alt", required=True)
    p = sub.add_parser("draft", parents=[common])
    p.add_argument("page")
    p.add_argument("--title", required=True)
    p.add_argument("--slug")
    p.add_argument("--page-id", type=int)
    p.add_argument("--tokens")
    p.add_argument("--page-fields", help="extra JSON fields for the page, e.g. a template (see reference/publishing.md)")
    p = sub.add_parser("publish", parents=[common])
    p.add_argument("--page-id", type=int, required=True)
    p.add_argument("--yes", action="store_true")
    a = ap.parse_args(argv)
    password = os.environ.get("WP_APP_PASSWORD", "")
    if not password:
        print("publish.py: set WP_APP_PASSWORD to a WordPress Application Password", file=sys.stderr)
        return 2
    wp = WordPress(a.site, a.user, password)
    try:
        return {"fetch": cmd_fetch, "media": cmd_media, "draft": cmd_draft, "publish": cmd_publish}[a.command](wp, a)
    except (PublishError, OSError, ValueError, KeyError) as exc:
        print(f"publish.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
