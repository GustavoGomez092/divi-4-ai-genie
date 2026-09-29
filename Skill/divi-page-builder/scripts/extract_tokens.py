#!/usr/bin/env python3
"""Extract a Divi site's design tokens into tokens.json.

Online:  extract_tokens.py --key NAME --page 12 [--page 34] --out tokens.json
         extract_tokens.py --site https://client.com --user USER --page 12 [--page 34] --out tokens.json
         (credentials from keys.json via --key, or --site/--user with the password in env
         WP_APP_PASSWORD; --keys PATH overrides the keys file location -- see wp_keys.py)
Offline: extract_tokens.py --content-file page.txt --url https://client.com/page/ --out tokens.json
         (--shortcode-file is an alias of --content-file; the file may hold Divi 4 shortcode or Divi 5 blocks)

The Divi major version decides the output: detect_site (style.css / asset versions / Divi 5 markers) online, plus
the content format of the pages (Divi 5 blocks anywhere mean Divi 5). Divi 4 keeps the shortcode tokens shape;
Divi 5 merges tokens5_from_blocks (content) with tokens5_from_html (public HTML/CSS of the pages, the site home
page, and their same-origin et-cache stylesheets) -- see reference/design-tokens.md.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import divi5_blocks  # noqa: E402
from divi5_schema import load_schema5  # noqa: E402
from divi_checks_values import normalize_color  # noqa: E402
from divi_format import detect_content, detect_site  # noqa: E402
from divi_schema import load_schema  # noqa: E402
from divi_shortcode import parse  # noqa: E402
from tokens5_from_blocks import tokens5_from_documents  # noqa: E402
from tokens5_from_html import CUSTOMIZER, stylesheet_links, tokens5_from_html  # noqa: E402
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


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _merge_html(parts) -> dict:
    """One view of several pages' tokens5_from_html results: first recovered value wins per id/key."""
    out = {"divi_version": "", "global": {}, "customizer": {}, "variables": {}, "fonts": {}, "loaded": [],
           "presets_css": {}, "preset_defaults": {}}
    for part in parts:
        out["divi_version"] = out["divi_version"] or part["site"]["divi_version"]
        for key, src in (("global", part["colors"]["global"]), ("customizer", part["colors"]["customizer"]),
                         ("variables", part["variables"]), ("fonts", part["fonts"]["customizer"])):
            for k, v in src.items():
                if k not in out[key] or (isinstance(v, dict) and out[key][k].get("value") is None):
                    out[key][k] = v
        out["loaded"] += [f for f in part["fonts"]["loaded"] if f not in out["loaded"]]
        for key in ("presets_css", "preset_defaults"):
            for k, css in part[key].items():
                have = out[key].setdefault(k, {**css, "declarations": {}, "rules": [], "selector": None})
                have["selector"] = have["selector"] or css["selector"]
                for d, v in css["declarations"].items():
                    have["declarations"].setdefault(d, v)
                have["rules"] += [r for r in css["rules"] if r not in have["rules"]]
    return out


def _css_of(entry):
    return {k: entry[k] for k in ("selector", "declarations", "rules")} if entry else None


def _with_refs(recovered: dict, refs: dict) -> dict:
    """Fold content references into recovered values: every id a page uses is listed (value None when the public
    HTML never shows it), every recovered id carries its usage count."""
    out = {}
    for name in list(recovered) + [n for n in refs if n not in recovered]:
        entry = dict(recovered.get(name) or {"value": None})
        ref = refs.get(name)
        if ref and "kind" in ref and "kind" not in entry:
            entry["kind"] = ref["kind"]
        entry["uses"] = ref["uses"] if ref else 0
        if ref:
            entry["roles"] = ref["roles"]
        out[name] = entry
    return out


def build_tokens5(sources, html_parts, site_url, schema5, divi_version=None) -> dict:
    """Divi 5 tokens.json: content tokens (tokens5_from_blocks) merged with public HTML/CSS tokens
    (tokens5_from_html results keyed by URL)."""
    t = tokens5_from_documents([divi5_blocks.parse(s["raw"]) for s in sources], schema5)
    html = _merge_html(html_parts.values())
    global_refs = t["colors"]["global_refs"]
    customizer = {role: dict(entry) for role, entry in html["customizer"].items()}
    for role, (cid, _default) in CUSTOMIZER.items():
        if cid in global_refs:
            customizer.setdefault(role, {"id": cid, "value": None})
            customizer[role].update(uses=global_refs[cid]["uses"], roles=global_refs[cid]["roles"])
    user_refs = {k: v for k, v in global_refs.items() if k not in {cid for cid, _ in CUSTOMIZER.values()}}
    global_colors = _with_refs(html["global"], user_refs)

    by_color = {}
    for cid, entry in list(global_colors.items()) + [(e["id"], e) for e in customizer.values()]:
        if isinstance(entry.get("value"), str):
            by_color.setdefault(normalize_color(entry["value"]), cid)
    palette = [dict(p, **({"global": by_color[p["hex"]]} if p["hex"] in by_color else {}))
               for p in t["colors"]["palette"]]

    presets = {name: [dict(p, css=_css_of(html["presets_css"].get(p["id"]))) for p in lst]
               for name, lst in t["presets"].items()}
    group_presets = {name: [dict(p, css=_css_of(html["presets_css"].get(p["id"]))) for p in lst]
                     for name, lst in t["group_presets"].items()}
    for pid, css in html["presets_css"].items():  # seen on a sampled page, not in the sampled content
        if css["kind"] == "module":
            lst = presets.setdefault(css["module"], [])
            if pid not in {p["id"] for p in lst}:
                lst.append({"id": pid, "uses": 0, "css": _css_of(css)})
        else:
            lst = group_presets.setdefault(css["group_name"], [])
            if pid not in {p["id"] for p in lst}:
                lst.append({"id": pid, "uses": 0, "module": css["module"], "group_id": None, "css": _css_of(css)})

    typography = dict(t["typography"], customizer=html["fonts"], loaded_fonts=html["loaded"])
    for key in ("heading_font", "body_font"):
        if not typography[key] and html["fonts"].get(key):
            typography[key] = html["fonts"][key]["value"]

    formats = [detect_content(s["raw"]) for s in sources]
    kinds = set(formats)
    return {
        "site": {"url": site_url, "divi_version": divi_version or html["divi_version"], "divi_major": 5,
                 "content_format": kinds.pop() if len(kinds) == 1 else "mixed",
                 "source_pages": [{"id": s["id"], "url": s["url"], "format": f} for s, f in zip(sources, formats)],
                 "extracted_at": _now()},
        "colors": {"global": global_colors, "customizer": customizer, "palette": palette},
        "variables": _with_refs(html["variables"], t["variables_refs"]),
        "typography": typography,
        "spacing": t["spacing"],
        "shapes": t["shapes"],
        "presets": presets,
        "group_presets": group_presets,
        "preset_defaults": {m: _css_of(css) for m, css in html["preset_defaults"].items()},
        "module_styles": t["module_styles"],
        "section_exemplars": t["section_exemplars"],
    }


def _origin_home(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}/" if parts.scheme and parts.netloc else ""


def _fetch_html5(urls) -> dict:
    """tokens5_from_html of each URL, following its same-origin et-cache stylesheets (fetched once each)."""
    css_cache, parts = {}, {}
    for url in urls:
        try:
            html = _get(url).decode("utf-8", "replace")
        except OSError as exc:
            print(f"warning: could not fetch {url}: {exc}", file=sys.stderr)
            continue
        links = stylesheet_links(html, url)
        for link in links:
            if link not in css_cache:
                try:
                    css_cache[link] = _get(link).decode("utf-8", "replace")
                except OSError as exc:
                    print(f"warning: could not fetch {link}: {exc}", file=sys.stderr)
                    css_cache[link] = ""
        parts[url] = tokens5_from_html(html, {k: css_cache[k] for k in links})
    return parts


def extract5(sources, site, html_files, divi_version=None) -> dict:
    for s, fmt in ((s, detect_content(s["raw"])) for s in sources):
        if fmt not in ("blocks", "mixed"):
            print(f"warning: page {s['id']} ({s['url'] or 'content file'}) is {fmt} content on a Divi 5 site: "
                  "it adds no module styles (convert it in the Visual Builder first)", file=sys.stderr)
    if html_files:
        parts = {f"file:{p}": tokens5_from_html(Path(p).read_text(encoding="utf-8")) for p in html_files}
    else:
        urls = [s["url"] for s in sources if s["url"]]
        home = _origin_home(site or (urls[0] if urls else ""))
        parts = _fetch_html5(list(dict.fromkeys(urls + ([home] if home else []))))
    return build_tokens5(sources, parts, site, load_schema5(), divi_version=divi_version)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", help="required unless --key resolves it, or a keys.json entry matches --user")
    ap.add_argument("--user", help="required unless --key resolves it, or a keys.json entry matches --site")
    ap.add_argument("--key", help="name of an entry in keys.json to use for credentials")
    ap.add_argument("--keys", help="keys.json path (default: env DIVI_KEYS_FILE, then "
                                   "~/.config/divi-page-builder/keys.json)")
    ap.add_argument("--page", type=int, action="append", default=[])
    ap.add_argument("--content-file", "--shortcode-file", dest="content_file",
                    help="offline: page content (Divi 4 shortcode or Divi 5 blocks) instead of --page")
    ap.add_argument("--url")
    ap.add_argument("--html-file", action="append", default=[], help=argparse.SUPPRESS)  # offline tests
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        detected = {}
        if a.content_file:
            sources = [{"id": 0, "url": a.url or "", "raw": Path(a.content_file).read_text(encoding="utf-8")}]
            site = a.url or ""
        else:
            if not a.page:
                ap.error("online mode needs --page")
            site, user, password = resolve_credentials(key_name=a.key, site=a.site, user=a.user, keys_path=a.keys)
            sources = [fetch_page(site, user, password, pid) for pid in a.page]
            detected = detect_site(site, fetch=lambda url: _get(url))
        blocks = any(detect_content(s["raw"]) in ("blocks", "mixed") for s in sources)
        if detected.get("divi_major") == 5 or blocks:
            if blocks and detected.get("divi_major") == 4:
                print("warning: the site looks like Divi 4 but the pages hold Divi 5 blocks: using Divi 5",
                      file=sys.stderr)
            tokens = extract5(sources, site, a.html_file, divi_version=detected.get("divi_version"))
        else:
            html = {}
            if a.html_file:
                html = {f"file:{p}": Path(p).read_text(encoding="utf-8") for p in a.html_file}
            for s in sources:
                if s["url"] and not a.html_file:
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
