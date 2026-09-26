#!/usr/bin/env python3
"""Send Divi pages to WordPress over the REST API, authenticated with an Application Password.

  publish.py fetch   [--key NAME | --site URL --user USER] [--keys PATH] --page-id ID --out FILE
  publish.py media   [--key NAME | --site URL --user USER] [--keys PATH] FILE --alt TEXT
  publish.py draft   PAGE [--key NAME | --site URL --user USER] [--keys PATH] --title TITLE [--slug S]
                     [--page-id ID] [--baseline FILE] [--tokens tokens.json] [--page-fields JSON]
  publish.py publish [--key NAME | --site URL --user USER] [--keys PATH] --page-id ID --yes
                     [--content PAGE] [--baseline FILE] [--status publish]
  publish.py keys    [--keys PATH]

Credentials come from a keys.json file (`--key NAME` picks an entry, or `--site`/`--user` are
matched against it) or, for backward compatibility, `--site`/`--user` plus env WP_APP_PASSWORD.
`--keys PATH` overrides the keys file location (otherwise env DIVI_KEYS_FILE, then
~/.config/divi-page-builder/keys.json); see wp_keys.py and reference/publishing.md. `keys` lists
the available `name`/`site`/`user` entries, plus `elegant_themes: {"username": ..., "configured": true}`
when the keys file has that optional section (`{"configured": false}` otherwise); a key value or
api_key is never printed. `draft` validates the page first and
refuses on errors; image attributes pointing at local files (file://, ./, ../) are uploaded to the
Media Library and rewritten. Pages are saved as drafts; `publish` requires --yes (after user approval).
Validation baseline: with --baseline FILE, or (with --page-id) the page's current content.raw, findings
already present there are pre-existing and do not block, exactly like `validate.py --baseline`.
`--page-fields` may not set status/content/meta (those are managed by the command itself) and must be
a JSON object. `draft --page-id` refuses to touch a page that is currently publish/future/private,
since forcing it back to draft would take a client's live page offline — use `publish --page-id ID
--content PAGE --yes` instead, after reviewing a separate draft copy. `publish` never changes the
visibility of a page that is private or scheduled (future): with --content it sends only content and
meta, and without --content it refuses; pass `--status publish` to deliberately make it public now.
Exit status: 0 ok, 1 validation errors or refused, 2 usage/HTTP/I-O error.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from divi_schema import load_schema  # noqa: E402
from divi_shortcode import escape_attr_value, parse, serialize  # noqa: E402
from local_media import LOCAL_PREFIXES, iter_local_images  # noqa: E402,F401  (LOCAL_PREFIXES: back-compat re-export)
from validate import validate_source  # noqa: E402
from wp_keys import KeysError, file_elegant_themes, list_keys, resolve_credentials, resolve_keys_path  # noqa: E402


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


def content_disposition(filename: str) -> str:
    """ASCII-only Content-Disposition: an ASCII fallback name plus RFC 5987 filename* for the real one."""
    fallback = "".join(c if " " <= c <= "~" and c not in '"\\' else "_" for c in filename)
    return f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{quote(filename, safe='')}"


def upload_media(wp: WordPress, path: Path, alt: str) -> dict:
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    media = wp.request("POST", "/media", data=path.read_bytes(),
                       headers={"Content-Type": ctype, "Content-Disposition": content_disposition(path.name)})
    if alt:
        wp.request("POST", f"/media/{media['id']}", json_body={"alt_text": alt})
    return {"id": media["id"], "url": media["source_url"], "file": str(path)}


def _find_local_images(doc, base_dir: Path):
    """Resolve every local image reference (local_media.iter_local_images) and verify it exists
    before any upload starts."""
    tasks = []
    for node, attr, local in iter_local_images(doc, base_dir):
        if not local.is_file():
            raise PublishError(f"{node.tag} {attr}: local image not found: {local}")
        tasks.append((node, attr, local))
    return tasks


def upload_local_images(wp: WordPress, source: str, base_dir: Path):
    doc = parse(source)
    tasks = _find_local_images(doc, base_dir)  # preflight: all paths must exist before any upload
    uploaded, cache = [], {}
    for node, attr, local in tasks:
        if local not in cache:
            alt = node.value("alt") or node.value("title_text") or local.stem.replace("-", " ")
            cache[local] = upload_media(wp, local, alt)
            uploaded.append(cache[local])
        node.attrs[attr] = escape_attr_value(cache[local]["url"], attr)
    return serialize(doc), uploaded


FORBIDDEN_PAGE_FIELDS = {"status", "content", "meta"}


def parse_page_fields(raw):
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PublishError(f"--page-fields is not valid JSON: {exc}") from None
    if not isinstance(obj, dict):
        raise PublishError("--page-fields must be a JSON object, e.g. '{\"template\": \"page-template-blank.php\"}'")
    if set(obj) & FORBIDDEN_PAGE_FIELDS:
        raise PublishError("--page-fields may not set status/content/meta")
    return obj


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


LIVE_STATUSES = ("publish", "future", "private")
KEEP_VISIBILITY = ("private", "future")


def blocking_errors(source: str, label: str, tokens=None, baseline=None, verb: str = "save") -> bool:
    """Print blocking (non-pre-existing) errors to stderr; return True if there are any."""
    findings = validate_source(source, load_schema(), tokens=tokens, baseline=baseline)
    errors = [f for f in findings if f.level == "error" and not f.preexisting]
    if not errors:
        return False
    for f in errors:
        print(f"{label}:{f.line}:{f.col} {f.code} {f.path}: {f.message}", file=sys.stderr)
    pre = sum(f.level == "error" and f.preexisting for f in findings)
    note = f" ({pre} pre-existing error(s) in the baseline ignored)" if pre else ""
    print(f"refusing to {verb}: {len(errors)} validation error(s){note}; run scripts/validate.py for details",
          file=sys.stderr)
    return True


def _baseline(a, current):
    """Explicit --baseline FILE wins; otherwise the page's current content.raw (when fetched)."""
    if a.baseline:
        return Path(a.baseline).read_text(encoding="utf-8")
    if current is not None:
        return (current.get("content") or {}).get("raw")
    return None


def cmd_draft(wp, a):
    page_fields = parse_page_fields(a.page_fields)
    page_path = Path(a.page)
    source = page_path.read_text(encoding="utf-8")
    tokens = json.loads(Path(a.tokens).read_text()) if a.tokens else None
    current = wp.request("GET", f"/pages/{a.page_id}?context=edit") if a.page_id else None
    if blocking_errors(source, a.page, tokens=tokens, baseline=_baseline(a, current), verb="save"):
        return 1
    if current is not None:
        status = current.get("status")
        if status in LIVE_STATUSES:
            print(f"page {a.page_id} is {status}; saving it as a draft would take it offline. "
                  f"Create a review copy instead: publish.py draft PAGE --title … (no --page-id), "
                  f"share its preview_url, and after approval apply it with: "
                  f"publish.py publish --page-id {a.page_id} --content PAGE --yes "
                  f"(that keeps the page's current visibility: {status} stays {status})", file=sys.stderr)
            return 1
    content, uploaded = upload_local_images(wp, source, page_path.resolve().parent)
    body = {"title": a.title, "content": content, "status": "draft", "meta": {"_et_pb_use_builder": "on"}}
    if a.slug:
        body["slug"] = a.slug
    body.update(page_fields)
    page = wp.request("POST", f"/pages/{a.page_id}" if a.page_id else "/pages", json_body=body)
    _print({"id": page["id"], "status": page.get("status", "draft"), "link": page.get("link", ""),
            "preview_url": _preview_url(page.get("link", "")),
            "edit_url": f"{wp.site}/wp-admin/post.php?post={page['id']}&action=edit", "uploaded": uploaded})
    return 0


def cmd_publish(wp, a):
    if not a.yes:
        print("refusing to publish without --yes (publish only after the user approves the draft)", file=sys.stderr)
        return 1
    current = wp.request("GET", f"/pages/{a.page_id}?context=edit")
    status = current.get("status")
    keep_visibility = status in KEEP_VISIBILITY and a.status != "publish"
    if a.content:
        page_path = Path(a.content)
        source = page_path.read_text(encoding="utf-8")
        if blocking_errors(source, a.content, baseline=_baseline(a, current), verb="publish"):
            return 1
        content, _uploaded = upload_local_images(wp, source, page_path.resolve().parent)
        body = {"content": content, "meta": {"_et_pb_use_builder": "on"}}
        if not keep_visibility:
            body["status"] = "publish"
    else:
        if keep_visibility:
            print(f"page {a.page_id} is {status}; publishing it would change its visibility. "
                  f"Nothing to do without --content; pass --status publish only if the user wants it public now.",
                  file=sys.stderr)
            return 1
        body = {"status": "publish"}
    page = wp.request("POST", f"/pages/{a.page_id}", json_body=body)
    _print({"id": page["id"], "status": page.get("status", ""), "link": page.get("link", "")})
    return 0


def cmd_keys(a) -> int:
    keys = list_keys(a.keys)
    if not keys:
        path, explicit = resolve_keys_path(a.keys)
        if not explicit and not path.exists():
            print(f"no keys file found; the default location is {path}", file=sys.stderr)
    et = file_elegant_themes(a.keys)
    elegant_themes = {"username": et["username"], "configured": True} if et else {"configured": False}
    _print({"keys": keys, "elegant_themes": elegant_themes})
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--site", help="required unless --key resolves it, or a keys.json entry matches --user")
    common.add_argument("--user", help="required unless --key resolves it, or a keys.json entry matches --site")
    common.add_argument("--key", help="name of an entry in keys.json to use for credentials")
    common.add_argument("--keys", help="keys.json path (default: env DIVI_KEYS_FILE, then "
                                       "~/.config/divi-page-builder/keys.json)")
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
    p.add_argument("--baseline", help="original page source; errors already in it do not block "
                                      "(default with --page-id: the page's current content)")
    p.add_argument("--page-fields", help="extra JSON fields for the page, e.g. a template (see reference/publishing.md)")
    p = sub.add_parser("publish", parents=[common])
    p.add_argument("--page-id", type=int, required=True)
    p.add_argument("--yes", action="store_true")
    p.add_argument("--content", help="also update content from this page file in the same publish request")
    p.add_argument("--baseline", help="original page source; errors already in it do not block "
                                      "(default: the page's current content)")
    p.add_argument("--status", choices=["publish"],
                   help="explicitly make a private/scheduled page public now (otherwise its visibility is kept)")
    p = sub.add_parser("keys")
    p.add_argument("--keys", help="keys.json path (default: env DIVI_KEYS_FILE, then "
                                  "~/.config/divi-page-builder/keys.json)")
    a = ap.parse_args(argv)
    if a.command == "keys":
        try:
            return cmd_keys(a)
        except KeysError as exc:
            print(f"publish.py: {exc}", file=sys.stderr)
            return 2
    try:
        site, user, password = resolve_credentials(key_name=a.key, site=a.site, user=a.user, keys_path=a.keys)
    except KeysError as exc:
        print(f"publish.py: {exc}", file=sys.stderr)
        return 2
    wp = WordPress(site, user, password)
    try:
        return {"fetch": cmd_fetch, "media": cmd_media, "draft": cmd_draft, "publish": cmd_publish}[a.command](wp, a)
    except (PublishError, OSError, ValueError, KeyError) as exc:
        print(f"publish.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
