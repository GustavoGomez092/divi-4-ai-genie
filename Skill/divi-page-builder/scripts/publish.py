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
Divi 5: `draft`/`publish` detect the page format (Divi 4 shortcode or Divi 5 blocks) and the site's Divi
major version (tokens.json `site.divi_major` with --tokens, else divi_format.detect_site), and refuse shortcode
for a Divi 5 site and blocks for a Divi 4 site (an undetectable version only warns). Block pages with parse
problems are refused. On Divi 5 the builder meta `_et_pb_use_builder=on` cannot be set by a plain REST save, so
`draft` creates (or, for an existing draft without the meta, overwrites) the page with a Divi 4 stub, then sends
one /batch/v1 request (touch the title; set content + meta) and checks the stored meta, exit 2 if it is not
`on`. `publish` on a page that isn't live yet runs the same stub + batch (with --content, or the page's current
content) before changing the status; on a live page `--content` sends content only and refuses when the meta is
known off; a Divi 5 page left published is checked on its public HTML (exit 2 without the builder layout). Before
the stub replaces an existing page's content, that content is saved to page-<ID>-before-stub-<time>.txt (next to the
page file, else the current directory); `publish` without --content refuses a page holding only the stub. Page files are
read and written byte-exact (CRLF kept) for block content. See reference/publishing.md, "Divi 5".
Exit status: 0 ok, 1 validation errors or refused, 2 usage/HTTP/I-O error.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import divi5_blocks  # noqa: E402
import divi_format  # noqa: E402
from divi_schema import load_schema  # noqa: E402
from divi_shortcode import escape_attr_value, parse, serialize  # noqa: E402
from local_media import LOCAL_PREFIXES, image_alt5, iter_local_images, set_image5  # noqa: E402,F401  (LOCAL_PREFIXES: back-compat re-export)
from validate import validate_source  # noqa: E402
from wp_keys import KeysError, file_elegant_themes, list_keys, resolve_credentials, resolve_keys_path  # noqa: E402


class PublishError(Exception):
    pass


class WordPress:
    def __init__(self, site: str, user: str, password: str):
        self.base = site.rstrip("/") + "/wp-json/wp/v2"
        self.site = site.rstrip("/")
        self._auth = "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()

    def batch(self, requests: list) -> list:
        """POST /wp-json/batch/v1 (one PHP process for all requests); the per-request responses."""
        out = self.request("POST", "/batch/v1", json_body={"requests": requests}, root=self.site + "/wp-json")
        return out.get("responses") or []

    def request(self, method: str, path: str, json_body=None, data: bytes = None, headers=None, root=None) -> dict:
        hdrs = {"Authorization": self._auth, "Accept": "application/json", "User-Agent": "divi-page-builder/1.0"}
        if json_body is not None:
            data = json.dumps(json_body).encode()
            hdrs["Content-Type"] = "application/json"
        hdrs.update(headers or {})
        req = urllib.request.Request((root or self.base) + path, data=data, method=method, headers=hdrs)
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


def upload_local_images5(wp: WordPress, source: str, base_dir: Path):
    """Divi 5 blocks: upload every local image leaf (local_media.iter_local_images) and point it at the uploaded
    URL. Only the blocks holding one are re-serialized; the rest of the page keeps its exact bytes."""
    doc = divi5_blocks.parse(source)
    tasks = []
    for block, ref, local in iter_local_images(doc, base_dir):  # preflight: all paths must exist first
        if not local.is_file():
            raise PublishError(f"{block.name} {ref.label}: local image not found: {local}")
        tasks.append((block, ref, local))
    if not tasks:
        return source, []
    uploaded, cache = [], {}
    for block, ref, local in tasks:
        if local not in cache:
            alt = image_alt5(block, ref) or local.stem.replace("-", " ")
            cache[local] = upload_media(wp, local, alt)
            uploaded.append(cache[local])
        set_image5(block, ref, cache[local]["url"])
    return divi5_blocks.serialize(doc), uploaded


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


def read_page(path) -> str:
    """A page file as text, byte-exact (newline="": CRLF survives)."""
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def read_source(path) -> tuple:
    """(format, text): Divi 5 block content is kept byte-exact; anything else is read exactly as before
    (universal newlines), so Divi 4 requests are unchanged."""
    raw = read_page(path)
    kind = divi_format.detect_content(raw)
    if kind == "blocks":
        return kind, raw
    return kind, raw.replace("\r\n", "\n").replace("\r", "\n")


def cmd_fetch(wp, a):
    page = wp.request("GET", f"/pages/{a.page_id}?context=edit")
    raw = page["content"]["raw"]
    with open(a.out, "w", encoding="utf-8", newline="") as fh:
        fh.write(raw)
    if divi_format.detect_content(raw) == "blocks":
        print("publish.py: note: this is Divi 5 block content; on WordPress 7.0+ content.raw is WordPress's "
              "canonical re-serialization of the stored blocks, not necessarily the stored bytes. Use it as the "
              "baseline as-is.", file=sys.stderr)
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
        return read_source(a.baseline)[1]
    if current is not None:
        return (current.get("content") or {}).get("raw")
    return None


# ---- Divi 5 ------------------------------------------------------------------------------------------------

D4_STUB = "[et_pb_section][/et_pb_section]"
BUILDER_META = "_et_pb_use_builder"
META_NOT_STORED = ("WordPress did not store _et_pb_use_builder=on; the page will render inside the theme's "
                   "title+sidebar template. See reference/publishing.md → Divi 5 builder meta.")
_SITE_CACHE: dict = {}
_BODY_CLASS = re.compile(r"<body\b[^>]*\bclass=[\"']([^\"']*)[\"']", re.I)


def site_major(wp, tokens=None):
    """The site's Divi major version (None when unknown): tokens.json site.divi_major (or site.divi_version)
    when given, else divi_format.detect_site(), once per run."""
    site = (tokens or {}).get("site") or {}
    major = site.get("divi_major")
    if not isinstance(major, int) or isinstance(major, bool):
        major = divi_format.major_from_version(site.get("divi_version"))
    if major is not None:
        return major
    if wp.site not in _SITE_CACHE:
        _SITE_CACHE[wp.site] = divi_format.detect_site(wp.site)
    found = _SITE_CACHE[wp.site]
    major = found.get("divi_major")
    if major is None:
        print(f"publish.py: warning: could not detect the site's Divi version ({found.get('evidence')}); "
              f"skipping the Divi 4/5 format check", file=sys.stderr)
    return major


def format_refusal(kind, major, label) -> bool:
    """Print why this content can't go to this site; True when refused."""
    if kind == "shortcode" and major is not None and major >= 5:
        print(f"{label}: this is Divi 4 shortcode; the site runs Divi 5 — write Divi 5 blocks "
              f"(reference/divi5/page-format.md). A Divi 4 page on a Divi 5 site renders through a degraded "
              f"legacy path and is never converted.", file=sys.stderr)
        return True
    if kind == "blocks" and major is not None and major < 5:
        print(f"{label}: this is Divi 5 block content; the site runs Divi {major} — write Divi 4 shortcode "
              f"(reference/page-format.md).", file=sys.stderr)
        return True
    return False


def parse_refusal(source, label) -> bool:
    """Block content that doesn't parse cleanly is never sent: rewriting a block whose JSON is bad would drop
    its attributes."""
    doc = divi5_blocks.parse(source)
    problems = doc.problems
    if not problems:
        return False
    for p in problems:
        line, col = doc.line_col(p.offset)
        print(f"{label}:{line}:{col} {p.code}: {p.message}", file=sys.stderr)
    print(f"refusing to send: {len(problems)} block parse problem(s); run scripts/validate.py for details",
          file=sys.stderr)
    return True


def check_site(wp, kind, source, label, tokens=None) -> bool:
    """The format checks shared by draft and publish; True when refused."""
    if kind == "blocks" and parse_refusal(source, label):
        return True
    if kind not in ("blocks", "shortcode"):
        return False
    return format_refusal(kind, site_major(wp, tokens), label)


def meta_state(page):
    """_et_pb_use_builder as the REST response shows it: "on", "off" (registered but not on), or None when the
    response doesn't carry the key (Divi registers it only after rendering a Divi 4 shortcode in the same
    request, so a page holding Divi 5 blocks never shows it)."""
    meta = page.get("meta")
    if not isinstance(meta, dict) or BUILDER_META not in meta:
        return None
    return "on" if meta[BUILDER_META] == "on" else "off"


def front_end_state(page):
    """For a published page: its public HTML's body classes (read-only, no auth). Divi adds
    et_pb_pagebuilder_layout exactly when _et_pb_use_builder is on. None when it can't be told."""
    link, pid = page.get("link"), page.get("id")
    if not link:
        return None
    try:
        html = divi_format._default_fetch(link).decode("utf-8", "replace")
    except Exception:
        return None
    m = _BODY_CLASS.search(html)
    classes = m.group(1).split() if m else []
    if f"page-id-{pid}" not in classes:
        return None
    return "on" if "et_pb_pagebuilder_layout" in classes else "off"


def is_stub(raw) -> bool:
    """The page holds only the Divi 4 stub an interrupted builder-meta sequence can leave behind."""
    return isinstance(raw, str) and raw.strip() == D4_STUB


def backup_before_stub(page_id, raw, page_file=None):
    """Save the page's current content.raw before it is replaced by the stub, next to the input page file (cwd
    when there is none); print and return the path. None when there is nothing worth keeping."""
    if not isinstance(raw, str) or not raw.strip() or is_stub(raw):
        return None
    folder = Path(page_file).resolve().parent if page_file else Path.cwd()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path, n = folder / f"page-{page_id}-before-stub-{stamp}.txt", 1
    while path.exists():
        n += 1
        path = folder / f"page-{page_id}-before-stub-{stamp}-{n}.txt"
    with open(path, "x", encoding="utf-8", newline="") as fh:
        fh.write(raw)
    print(f"publish.py: saved page {page_id}'s current content to {path} before replacing it with the Divi 4 "
          f"stub", file=sys.stderr)
    return path


def recovery_hint(page_id, page_file=None, backup=None, title=None) -> str:
    """The exact commands that finish an interrupted builder-meta sequence."""
    source = page_file or backup
    parts = [f"Page {page_id} is not published and may hold only the Divi 4 stub."]
    if backup:
        parts.append(f"Its previous content is saved in {backup}.")
    if source:
        t = title.replace('"', '\\"') if title else "…"
        parts.append(f'Retry with `publish.py draft {source} --page-id {page_id} --title "{t}"` (keeps it a draft) '
                     f"or, once approved, `publish.py publish --page-id {page_id} --content {source} --yes`.")
    else:
        parts.append(f"Retry with `publish.py draft PAGE --page-id {page_id} --title …` using your page file.")
    return " ".join(parts)


def _check_batch(responses, page_id, hint=""):
    if len(responses) != 2 or any(r.get("status") != 200 for r in responses):
        detail = "; ".join(f"request {i + 1}: HTTP {r.get('status')} — {(r.get('body') or {}).get('code', '')}: "
                           f"{(r.get('body') or {}).get('message', '')}" for i, r in enumerate(responses)
                           if r.get("status") != 200) or f"{len(responses)} responses"
        raise PublishError(f"POST /batch/v1 failed ({detail}). {hint}")
    return responses[1].get("body") or {}


def builder_meta_sequence(wp, page_id, title, content, hint=""):
    """The batch that sets content + _et_pb_use_builder (the page must hold D4_STUB), then the read-back.
    Returns the read-back page; raises MetaNotStored when the meta did not stick."""
    item = f"/wp/v2/pages/{page_id}"
    try:
        responses = wp.batch([
            {"method": "POST", "path": item, "body": {"title": title}},
            {"method": "POST", "path": item, "body": {"content": content, "meta": {BUILDER_META: "on"}}},
        ])
    except PublishError as exc:
        raise PublishError(f"{exc}. {hint}") from None
    written = _check_batch(responses, page_id, hint)
    back = wp.request("GET", f"/pages/{page_id}?context=edit")
    # The batch's own response reads the stored meta right after writing it (the key is registered in that
    # process); a plain GET of Divi 5 content cannot show the key, but when it does, it must agree.
    if meta_state(written) != "on" or meta_state(back) == "off":
        raise MetaNotStored(page_id)
    if (back.get("content") or {}).get("raw") not in (None, content):
        print(f"publish.py: note: page {page_id}'s stored content.raw differs from the file sent (WordPress 7.0+ "
              f"re-serializes blocks canonically; kses may also have filtered it). Fetch it and diff if unsure.",
              file=sys.stderr)
    return back


class MetaNotStored(Exception):
    pass


def stub_then_meta(wp, current, page_id, stub_body, title, content, page_file=None):
    """Back up the page's current content, write the Divi 4 stub (stub_body carries it), then
    builder_meta_sequence. Only for pages that are not live. Returns (read-back page or None when the meta did not
    stick, recovery hint)."""
    backup = backup_before_stub(page_id, (current.get("content") or {}).get("raw"), page_file)
    hint = recovery_hint(page_id, page_file, backup, title)
    wp.request("POST", f"/pages/{page_id}", json_body=stub_body)
    try:
        return builder_meta_sequence(wp, page_id, title, content, hint), hint
    except MetaNotStored:
        return None, hint


def _draft_output(wp, page, uploaded):
    _print({"id": page["id"], "status": page.get("status", "draft"), "link": page.get("link", ""),
            "preview_url": _preview_url(page.get("link", "")),
            "edit_url": f"{wp.site}/wp-admin/post.php?post={page['id']}&action=edit", "uploaded": uploaded})


def _divi5_draft(wp, a, content, current, page_fields, uploaded):
    """Divi 5 draft: stub + batch + read-back, unless an existing draft already has the builder meta on."""
    if current is not None and meta_state(current) == "on":
        body = {"title": a.title, "content": content, "status": "draft"}
        if a.slug:
            body["slug"] = a.slug
        body.update(page_fields)
        _draft_output(wp, wp.request("POST", f"/pages/{a.page_id}", json_body=body), uploaded)
        return 0
    stub = {"content": D4_STUB, "status": "draft"}
    if current is None:
        stub = {"title": a.title, **({"slug": a.slug} if a.slug else {}), "status": "draft", "content": D4_STUB}
    elif a.slug:
        stub["slug"] = a.slug
    stub.update(page_fields)
    if a.page_id:
        page = dict(current, id=a.page_id)
        back, hint = stub_then_meta(wp, current, a.page_id, stub, a.title, content, a.page)
    else:
        page = wp.request("POST", "/pages", json_body=stub)
        hint = recovery_hint(page["id"], a.page, None, a.title)
        try:
            back = builder_meta_sequence(wp, page["id"], a.title, content, hint)
        except MetaNotStored:
            back = None
    if back is None:
        print(f"page {page['id']} (draft): {META_NOT_STORED} {hint}", file=sys.stderr)
        return 2
    _draft_output(wp, {**page, **{k: back[k] for k in ("status", "link") if back.get(k)}}, uploaded)
    return 0


def _divi5_publish_plan(current, page_id) -> str:
    """How publish sends Divi 5 content: "direct" (content/status only; the meta is on, or a live Divi 5 page whose
    meta REST can't show), "stub" (a page that isn't live and whose meta isn't known to be on: set it with the
    verified stub + batch first, then change the status), or "refuse" (a live page whose meta is off or can't be
    confirmed: its content is never swapped for the stub)."""
    status = current.get("status")
    state = meta_state(current)
    if state is None and status == "publish":
        state = front_end_state(current)
    if state == "on":
        return "direct"
    if status not in LIVE_STATUSES:
        return "stub"
    divi5_page = divi_format.detect_content((current.get("content") or {}).get("raw") or "") == "blocks"
    if state is None and divi5_page:
        print(f"publish.py: note: could not read _et_pb_use_builder for page {page_id} (REST shows it only for "
              f"pages holding Divi 4 content); a content update leaves it as it is.", file=sys.stderr)
        return "direct"
    why = "is not on" if state == "off" else "could not be confirmed (and the page does not hold Divi 5 blocks)"
    print(f"page {page_id} is {status} (live) and its _et_pb_use_builder meta {why}: with Divi 5 content it "
          f"would render inside the theme's title+sidebar template. Setting that meta over REST means swapping "
          f"the page's content for a Divi 4 stub first, which is never done to a live page. Set it in "
          f"WordPress instead: open the page once in the Divi builder and save, or "
          f"`wp post meta update {page_id} _et_pb_use_builder on --user=<admin>`; or build a new draft with "
          f"publish.py draft (no --page-id), review it, and publish that. See reference/publishing.md, "
          f"Divi 5.", file=sys.stderr)
    return "refuse"


def _page_title(current, page_id) -> str:
    title = (current.get("title") or {}).get("raw") if isinstance(current.get("title"), dict) else None
    if not isinstance(title, str):
        raise PublishError(f"GET /pages/{page_id}?context=edit returned no title.raw; cannot re-save the title "
                           f"for the builder-meta batch")
    return title


def _backstop(page, was_live=False) -> int:
    """After publish leaves a Divi 5 page public: its public HTML must carry the builder layout."""
    if page.get("status") != "publish" or front_end_state(page) != "off":
        return 0
    state = "is published" if was_live else "is now published"
    print(f"page {page['id']} {state}, but its public page lacks et_pb_pagebuilder_layout: "
          f"_et_pb_use_builder is not on, so it renders inside the theme's title+sidebar template. Fix it now: open "
          f"the page once in the Divi builder and save, or `wp post meta update {page['id']} _et_pb_use_builder on "
          f"--user=<admin>`, or switch it back to draft. See reference/publishing.md → Divi 5 builder meta.",
          file=sys.stderr)
    return 2


def cmd_draft(wp, a):
    page_fields = parse_page_fields(a.page_fields)
    page_path = Path(a.page)
    kind, source = read_source(page_path)
    tokens = json.loads(Path(a.tokens).read_text()) if a.tokens else None
    if check_site(wp, kind, source, a.page, tokens):
        return 1
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
    if kind == "blocks":
        content, uploaded = upload_local_images5(wp, source, page_path.resolve().parent)
        return _divi5_draft(wp, a, content, current, page_fields, uploaded)
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
    kind = source = None
    if a.content:
        kind, source = read_source(Path(a.content))
        if check_site(wp, kind, source, a.content):
            return 1
    current = wp.request("GET", f"/pages/{a.page_id}?context=edit")
    status = current.get("status")
    keep_visibility = status in KEEP_VISIBILITY and a.status != "publish"
    current_raw = (current.get("content") or {}).get("raw") or ""
    if not a.content and is_stub(current_raw):
        print(f"page {a.page_id} holds only the Divi 4 stub `{D4_STUB}` left by an interrupted builder-meta "
              f"sequence; publishing it would put an empty page live. Send the real content with it: "
              f"`publish.py publish --page-id {a.page_id} --content PAGE --yes` (or `publish.py draft PAGE --page-id "
              f"{a.page_id} --title …` to keep it a draft), where PAGE is your page file or the "
              f"page-{a.page_id}-before-stub-*.txt backup publish.py saved.", file=sys.stderr)
        return 1
    divi5 = kind == "blocks" or (not a.content and divi_format.detect_content(current_raw) == "blocks")
    plan = None
    if a.content:
        page_path = Path(a.content)
        if blocking_errors(source, a.content, baseline=_baseline(a, current), verb="publish"):
            return 1
        if kind == "blocks":
            plan = _divi5_publish_plan(current, a.page_id)
            if plan == "refuse":
                return 1
            content, _uploaded = upload_local_images5(wp, source, page_path.resolve().parent)
            body = {"content": content}
        else:
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
        if divi5 and status not in LIVE_STATUSES and meta_state(current) != "on":
            plan, content = "stub", current_raw
    if plan == "stub":
        # Not live yet: set the builder meta with the verified sequence, and only then make the page public.
        back, hint = stub_then_meta(wp, current, a.page_id, {"content": D4_STUB}, _page_title(current, a.page_id),
                                    content, a.content)
        if back is None:
            print(f"page {a.page_id} ({status}, not published): {META_NOT_STORED} {hint}", file=sys.stderr)
            return 2
        body = {"status": "publish"}
    page = wp.request("POST", f"/pages/{a.page_id}", json_body=body)
    _print({"id": page["id"], "status": page.get("status", ""), "link": page.get("link", "")})
    return _backstop(page, was_live=status == "publish") if divi5 else 0


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
