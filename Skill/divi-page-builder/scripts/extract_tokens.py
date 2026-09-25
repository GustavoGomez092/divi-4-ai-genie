#!/usr/bin/env python3
"""Extract a Divi site's design tokens into tokens.json.

Online:  extract_tokens.py --key NAME --page 12 [--page 34] --out tokens.json
         extract_tokens.py --site https://client.com --user USER --page 12 [--page 34] --out tokens.json
         (credentials from keys.json via --key, or --site/--user with the password in env
         WP_APP_PASSWORD; --keys PATH overrides the keys file location -- see wp_keys.py)
Offline: extract_tokens.py --shortcode-file page.txt --url https://client.com/page/ --out tokens.json
"""
from __future__ import annotations

import argparse
import base64
import datetime
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from divi_schema import load_schema  # noqa: E402
from divi_shortcode import parse  # noqa: E402
from tokens_from_html import tokens_from_html  # noqa: E402
from tokens_from_shortcode import tokens_from_documents  # noqa: E402
from wp_keys import KeysError, resolve_credentials  # noqa: E402


def _get(url: str, auth: str = "") -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "divi-page-builder/1.0"})
    if auth:
        req.add_header("Authorization", "Basic " + base64.b64encode(auth.encode()).decode())
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def fetch_page(site: str, user: str, password: str, page_id: int) -> dict:
    data = json.loads(_get(f"{site.rstrip('/')}/wp-json/wp/v2/pages/{page_id}?context=edit", f"{user}:{password}"))
    return {"id": page_id, "url": data["link"], "raw": data["content"]["raw"]}


def build_tokens(sources, html_by_url, site_url, schema) -> dict:
    tokens = tokens_from_documents([parse(s["raw"]) for s in sources], schema)
    html_parts = [tokens_from_html(h) for h in html_by_url.values() if h]
    customizer, global_colors, fonts, version = {}, {}, [], ""
    for part in html_parts:
        customizer.update({k: v for k, v in part["customizer"].items() if k not in customizer})
        global_colors.update(part["global_colors"])
        fonts += [f for f in part["fonts"] if f not in fonts]
        version = version or part["divi_version"]
    tokens["colors"]["global"] = global_colors
    tokens["colors"]["customizer"] = customizer
    tokens["typography"]["loaded_fonts"] = fonts
    if not tokens["typography"]["heading_font"]:
        tokens["typography"]["heading_font"] = customizer.get("heading_font", "")
    if not tokens["typography"]["body_font"]:
        tokens["typography"]["body_font"] = customizer.get("body_font", "")
    tokens["site"] = {"url": site_url, "divi_version": version,
                      "source_pages": [{"id": s["id"], "url": s["url"]} for s in sources],
                      "extracted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    return dict(sorted(tokens.items(), key=lambda kv: kv[0] != "site"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", help="required unless --key resolves it, or a keys.json entry matches --user")
    ap.add_argument("--user", help="required unless --key resolves it, or a keys.json entry matches --site")
    ap.add_argument("--key", help="name of an entry in keys.json to use for credentials")
    ap.add_argument("--keys", help="keys.json path (default: env DIVI_KEYS_FILE, then "
                                   "~/.config/divi-page-builder/keys.json)")
    ap.add_argument("--page", type=int, action="append", default=[])
    ap.add_argument("--shortcode-file")
    ap.add_argument("--url")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        if a.shortcode_file:
            sources = [{"id": 0, "url": a.url or "", "raw": Path(a.shortcode_file).read_text(encoding="utf-8")}]
            site = a.url or ""
        else:
            if not a.page:
                ap.error("online mode needs --page")
            site, user, password = resolve_credentials(key_name=a.key, site=a.site, user=a.user, keys_path=a.keys)
            sources = [fetch_page(site, user, password, pid) for pid in a.page]
        html = {}
        for s in sources:
            if s["url"]:
                try:
                    html[s["url"]] = _get(s["url"]).decode("utf-8", "replace")
                except OSError as exc:
                    print(f"warning: could not fetch {s['url']}: {exc}", file=sys.stderr)
        tokens = build_tokens(sources, html, site, load_schema())
        Path(a.out).write_text(json.dumps(tokens, indent=1, ensure_ascii=False))
    except KeysError as exc:
        print(f"extract_tokens.py: {exc}", file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError) as exc:
        # Never include the password or an Authorization header here: `exc` only ever carries
        # things like a filesystem error, a JSON-decode error, or a missing REST response key
        # (e.g. "link"/"content"/"raw") -- none of which include the credentials, which only ever
        # travel inside the base64-encoded Authorization header built in `_get`.
        print(f"extract_tokens.py: {exc}", file=sys.stderr)
        return 2
    ms = tokens["module_styles"]
    print(f"wrote {a.out}: {sum(len(v) for v in ms.values())} style bundles across {len(ms)} modules, "
          f"{len(tokens['colors']['palette'])} palette colors, {len(tokens['section_exemplars'])} section exemplars, "
          f"{sum(len(v) for v in tokens['presets'].values())} presets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
