#!/usr/bin/env python3
"""R6 probe: what Divi 5 design data an outside party can recover (public HTML + optional REST).

  SSL_CERT_FILE=/etc/ssl/cert.pem python3 research/tools/divi5/d5_tokens_probe.py --url http://divi-5-test.local/r6-tokens-trace/
  WP_APP_PASSWORD=... python3 research/tools/divi5/d5_tokens_probe.py --url URL --site http://divi-5-test.local \
      --user user --page 23 [--probe-rest]

Prints JSON with:
  public.root_vars      -- :root custom properties by family (--gcid-*, --gvid-*, --et_global_*)
  public.presets        -- CSS rules whose selector names a preset class (preset--module--… / preset--group--…)
  public.stylesheets    -- same-origin et-cache <link> stylesheets that were followed
  content (with creds)  -- per-block modulePreset / groupPreset ids and $variable(...)$ references from content.raw
  rest_probe            -- result of trying Divi's divi/v1 settings-data endpoints with the Application Password
Research helper only (stdlib); not part of the skill.
"""
from __future__ import annotations

import argparse
import base64
import collections
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
ROOT_RE = re.compile(r":root\s*\{([^{}]*)\}")
DECL_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;]+)")
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
PRESET_CLASS_RE = re.compile(r"preset--(?:module|group)--[\w-]+")
BLOCK_RE = re.compile(r"<!--\s+wp:([a-z0-9-]+/[a-z0-9-]+)\s+(\{.*?\})\s+/?-->", re.S)
VARIABLE_RE = re.compile(r"\$variable\((\{.*?\})\)\$")
CUSTOMIZER_GCIDS = {"gcid-primary-color", "gcid-secondary-color", "gcid-heading-color", "gcid-body-color", "gcid-link-color"}


def get(url: str, auth: str = "", headers: dict | None = None) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": "divi-genie-r6-probe/1.0", **(headers or {})})
    if auth:
        req.add_header("Authorization", "Basic " + base64.b64encode(auth.encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def collect_css(html: str, page_url: str) -> tuple[str, list[str]]:
    css = [m for m in re.findall(r"<style[^>]*>(.*?)</style>", html, re.S)]
    followed = []
    origin = urllib.parse.urlsplit(page_url).netloc
    for href in re.findall(r"<link[^>]+href=['\"]([^'\"]+\.css[^'\"]*)['\"]", html):
        u = urllib.parse.urljoin(page_url, href.replace("&#038;", "&"))
        if urllib.parse.urlsplit(u).netloc == origin and "/et-cache/" in u:
            status, body = get(u)
            if status == 200:
                css.append(body.decode("utf-8", "replace"))
                followed.append(u)
    return COMMENT_RE.sub("", "\n".join(css)), followed


def classify_gvid(value: str) -> str:
    v = value.strip()
    if v.lower().startswith("url("):
        return "images"
    if v.startswith(("'", '"')):
        return "fonts"
    if "gradient(" in v:
        return "gradients"
    return "numbers"


def root_vars(css: str) -> dict:
    out = {"colors_customizer": {}, "colors_global": {}, "variables": collections.defaultdict(dict), "customizer_fonts": {}}
    for block in ROOT_RE.findall(css):
        for name, value in DECL_RE.findall(block):
            key, value = name[2:], value.strip()
            if key.startswith("gcid-"):
                (out["colors_customizer"] if key in CUSTOMIZER_GCIDS else out["colors_global"])[key] = value
            elif key.startswith("gvid-"):
                out["variables"][classify_gvid(value)][key] = value
            elif key.startswith("et_global_"):
                out["customizer_fonts"][key] = value
    out["variables"] = dict(out["variables"])
    return out


def preset_rules(css: str) -> dict:
    presets: dict[str, list] = collections.defaultdict(list)
    for sel, body in RULE_RE.findall(css):
        classes = set(PRESET_CLASS_RE.findall(sel))
        for cls in classes:
            decls = [d.strip() for d in body.split(";") if d.strip()]
            presets[cls].append({"selector": " ".join(sel.split())[:300], "declarations": decls})
    return dict(presets)


def content_refs(raw: str) -> dict:
    blocks = collections.Counter()
    module_presets, group_presets, variables = collections.Counter(), collections.Counter(), collections.Counter()
    for name, attrs_json in BLOCK_RE.findall(raw):
        blocks[name] += 1
        try:
            attrs = json.loads(attrs_json)
        except json.JSONDecodeError:
            continue
        for pid in attrs.get("modulePreset", []) or []:
            module_presets[f"{name}:{pid}"] += 1
        for gid, ref in (attrs.get("groupPreset") or {}).items():
            for pid in ref.get("presetId", []) or []:
                group_presets[f"{name}:{gid}:{ref.get('groupName', '')}:{pid}"] += 1
        # json.loads already turned " back into '"', so $variable({...})$ payloads are plain JSON now.
        for payload in VARIABLE_RE.findall(json.dumps(attrs, ensure_ascii=False).replace('\\"', '"')):
            try:
                v = json.loads(payload)
                variables[f"{v.get('type')}:{v.get('value', {}).get('name')}"] += 1
            except json.JSONDecodeError:
                variables[payload[:80]] += 1
    return {"blocks": dict(blocks), "module_presets": dict(module_presets),
            "group_presets": dict(group_presets), "variable_refs": dict(variables),
            "d4_shortcodes": len(re.findall(r"\[et_pb_\w+", raw))}


def rest_probe(site: str, auth: str, page_id: int) -> dict:
    base = site.rstrip("/") + "/wp-json/divi/v1"
    result = {}
    status, body = get(base + "/settings-data/nonces", auth)
    result["nonces_status"] = status
    nonce = ""
    try:
        nonce = json.loads(body)["nonces"]["/divi/v1/settings-data/after-app-load"]["GET"]
    except Exception:  # noqa: BLE001
        pass
    for label, hdrs in (("after_app_load_no_nonce", {}), ("after_app_load_with_nonce", {"X-ET-Nonce": nonce})):
        s, b = get(f"{base}/settings-data/after-app-load?et_post_id={page_id}", auth, hdrs)
        result[label] = {"status": s, "body": b[:160].decode("utf-8", "replace")}
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--site")
    ap.add_argument("--user")
    ap.add_argument("--page", type=int)
    ap.add_argument("--probe-rest", action="store_true")
    a = ap.parse_args()
    status, html_b = get(a.url)
    html = html_b.decode("utf-8", "replace")
    css, followed = collect_css(html, a.url)
    out = {"url": a.url, "http_status": status,
           "public": {"root_vars": root_vars(css), "presets": preset_rules(css), "stylesheets": followed}}
    pw = os.environ.get("WP_APP_PASSWORD", "")
    if a.site and a.user and pw and a.page:
        auth = f"{a.user}:{pw}"
        s, b = get(f"{a.site.rstrip('/')}/wp-json/wp/v2/pages/{a.page}?context=edit", auth)
        if s == 200:
            out["content"] = content_refs(json.loads(b)["content"]["raw"])
        else:
            out["content"] = {"error": s}
        if a.probe_rest:
            out["rest_probe"] = rest_probe(a.site, auth, a.page)
    json.dump(out, sys.stdout, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
