#!/usr/bin/env python3
"""Download + unpack a specific Divi 4 version from the Elegant Themes API into a local cache.

  ET_USERNAME=... ET_API_KEY=... python3 fetch_divi.py [version|latest]

A stdlib port of scripts/preview/fetch-divi.mjs, sharing the identical cache layout so Node and
Python fetch/reuse the same download:

  PP_CACHE_DIR/divi/Divi-<version>/Divi   unpacked theme (+ the .zip alongside it)

Endpoints (from Divi core/components/api/ElegantThemes.php + core/components/Updates.php):
  version check : GET https://www.elegantthemes.com/api/api.php?api_update=1&action=check_version_status&product=Divi&version=V&username=U&api_key=K
                  -> PHP-serialized a:1:{s:6:"status";s:9:"available"|"not_available"|"blocklisted"}
  latest        : POST https://www.elegantthemes.com/api/api.php  action=check_theme_updates installed_themes[Divi]=4.0.0 automatic_updates=on username api_key
                  -> serialized array; ['Divi']['new_version'].
  download      : GET https://www.elegantthemes.com/api/api_downloads.php?api_update=1&theme=Divi&version=V&username=U&api_key=K
                  -> 200 application/zip (top-level dir "Divi/"); omit `version` for latest.
                  bad api key -> 200 text/html "API key is not valid"; bad user -> "Subscription is not active";
                  unknown version -> 403 XML AccessDenied (S3). Too many calls (~15 in a few minutes) -> 429 HTML page.

Credentials are only ever held in memory; nothing here prints or writes them. Errors are always
raised with credentials redacted (see _redact / _redacted_url below) - including from response
bodies, and from URLs, which are rebuilt from the params with placeholders substituted *before*
encoding (never by string-matching the raw credentials against an already-encoded URL: encoding
can transform a credential, e.g. '@' -> '%40', so a raw-substring redaction can miss it).

Env:
  PP_CACHE_DIR   - cache root (default ~/.cache/divi-page-builder, %LOCALAPPDATA%\\divi-page-builder).
  PP_DIVI_CACHE  - internal override for the Divi cache dir specifically (default PP_CACHE_DIR/divi).
  PP_ET_ENDPOINT - internal/test-only override for the API base URL (never set for real use); lets
                   tests point at a local stand-in instead of the real Elegant Themes API.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

UA = "WordPress/6.8; Elegant Themes/4.27.9; https://localhost/"


def _api_base() -> str:
    # Read lazily (not as a module-level constant) so PP_ET_ENDPOINT can be set per-test, after import.
    return os.environ.get("PP_ET_ENDPOINT") or "https://www.elegantthemes.com/api/"


class FetchError(Exception):
    pass


def cache_root() -> Path:
    if os.environ.get("PP_CACHE_DIR"):
        return Path(os.environ["PP_CACHE_DIR"])
    if sys.platform == "win32" and os.environ.get("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "divi-page-builder"
    return Path(os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")) / "divi-page-builder"


def default_cache_dir() -> Path:
    if os.environ.get("PP_DIVI_CACHE"):
        return Path(os.environ["PP_DIVI_CACHE"])
    return cache_root() / "divi"


def theme_dir(version: str, cache_dir: Optional[Path] = None) -> Optional[Path]:
    """Returns the unpacked Divi theme dir (.../Divi-<version>/Divi) for `version`, or None if
    it isn't cached (no readable style.css)."""
    cache_dir = Path(cache_dir) if cache_dir is not None else default_cache_dir()
    d = cache_dir / f"Divi-{version}" / "Divi"
    return d if (d / "style.css").is_file() else None


def list_cached(cache_dir: Optional[Path] = None) -> list:
    """All cached Divi versions (those with a readable style.css), oldest first."""
    cache_dir = Path(cache_dir) if cache_dir is not None else default_cache_dir()
    if not cache_dir.exists():
        return []
    out = []
    for entry in cache_dir.iterdir():
        m = re.match(r"^Divi-(\d+(?:\.\d+)*)$", entry.name)
        if m and (entry / "Divi" / "style.css").is_file():
            out.append(m.group(1))
    out.sort(key=lambda v: tuple(int(x) for x in v.split(".")))
    return out


def newest_cached(cache_dir: Optional[Path] = None) -> Optional[str]:
    versions = list_cached(cache_dir)
    return versions[-1] if versions else None


def _creds():
    username, api_key = os.environ.get("ET_USERNAME"), os.environ.get("ET_API_KEY")
    if not username or not api_key:
        raise FetchError(
            "Divi is not cached for this version: set ET_USERNAME and ET_API_KEY "
            "(Elegant Themes account > API Key) to download it."
        )
    return {"username": username, "api_key": api_key}


def _redact(s: str, creds: dict) -> str:
    """For response BODY text, which is never URL-encoded, so a raw substring match is correct here."""
    return s.replace(creds["api_key"], "<API_KEY>").replace(creds["username"], "<ET_USERNAME>")


def _redacted_url(endpoint: str, params: dict) -> str:
    """A safe-to-print URL built from the SAME params, with credentials replaced before encoding.
    Never derive this by string-matching the raw credentials against the already-encoded URL:
    urlencode percent-encodes (e.g. '@' -> '%40', '+' -> '%2B'), so an email-style username or a
    key containing '+'/'/' would survive untouched in that encoded form and leak into a message."""
    safe = dict(params)
    if "username" in safe:
        safe["username"] = "<ET_USERNAME>"
    if "api_key" in safe:
        safe["api_key"] = "<API_KEY>"
    return _api_base() + endpoint + ".php?" + urllib.parse.urlencode(safe)


def _et_get(endpoint: str, params: dict) -> dict:
    url = _api_base() + endpoint + ".php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            status, body = resp.status, resp.read()
            ctype = resp.headers.get("Content-Type", "") if resp.headers else ""
    except urllib.error.HTTPError as exc:
        status, body = exc.code, exc.read()
        ctype = exc.headers.get("Content-Type", "") if exc.headers else ""
    except urllib.error.URLError as exc:
        raise FetchError(f"cannot reach Elegant Themes API: {exc.reason}") from None
    return {"status": status, "type": ctype, "body": body, "url": url, "redacted_url": _redacted_url(endpoint, params)}


def latest_version() -> str:
    c = _creds()
    body = urllib.parse.urlencode(
        {"action": "check_theme_updates", "installed_themes[Divi]": "4.0.0", "class_version": "1.2", "automatic_updates": "on", **c}
    ).encode()
    req = urllib.request.Request(
        _api_base() + "api.php", data=body, headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            status = resp.status
            text = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        text = exc.read().decode("utf-8", "replace")
    except urllib.error.URLError as exc:
        raise FetchError(f"cannot reach Elegant Themes API: {exc.reason}") from None
    m = re.search(r's:11:"new_version";s:\d+:"([^"]+)"', text)
    if not m:
        suffix = " rate-limited, retry later" if status == 429 else ""
        raise FetchError(f"Could not determine latest Divi version (HTTP {status}{suffix})")
    return m.group(1)


def ensure_divi(version: str = "latest", cache_dir: Optional[Path] = None, log=None) -> Path:
    """Returns the absolute path of the unpacked Divi theme dir (.../Divi-<version>/Divi) for
    `version`, downloading (and caching) it first if it isn't already cached. Raises FetchError
    with credentials redacted on any failure; never prints or writes credentials."""
    cache_dir = Path(cache_dir) if cache_dir is not None else default_cache_dir()
    log = log or (lambda msg: print(msg, file=sys.stderr))

    if version == "latest":
        version = latest_version()

    cached = theme_dir(version, cache_dir)
    if cached is not None:
        return cached

    c = _creds()
    st = _et_get("api", {"api_update": 1, "action": "check_version_status", "product": "Divi", "version": version, **c})
    m = re.search(r'"status";s:\d+:"([^"]+)"', st["body"].decode("utf-8", "replace"))
    status = m.group(1) if m else None
    if status != "available":
        if status:
            detail = status
        else:
            detail = f"unexpected response HTTP {st['status']}"
            if st["status"] == 429:
                detail += " rate-limited, retry later"
        raise FetchError(f"Divi {version} is not downloadable (status={detail}) url={st['redacted_url']}")

    t0 = time.time()
    dl = _et_get("api_downloads", {"api_update": 1, "theme": "Divi", "version": version, **c})
    if dl["status"] != 200 or dl["body"][:2] != b"PK":
        # Redact the whole body first, then truncate: truncating first could cut a credential in two,
        # and the surviving fragment would no longer match (and so escape) the redaction.
        snippet = _redact(dl["body"].decode("utf-8", "replace"), c)[:160].strip()
        raise FetchError(f"Divi download failed: HTTP {dl['status']} {dl['type']} url={dl['redacted_url']} {snippet}")

    cache_dir.mkdir(parents=True, exist_ok=True)
    zip_path = cache_dir / f"Divi-{version}.zip"
    zip_path.write_bytes(dl["body"])
    dest = cache_dir / f"Divi-{version}"
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)

    style_css = dest / "Divi" / "style.css"
    gm = re.search(r"^Version:\s*(\S+)", style_css.read_text(encoding="utf-8", errors="replace"), re.M) if style_css.is_file() else None
    got = gm.group(1) if gm else None
    if got != version:
        raise FetchError(f"Downloaded zip has Divi {got}, expected {version}")

    log(f"Fetched Divi {version} ({len(dl['body']) / 1048576:.1f} MB) in {int((time.time() - t0) * 1000)} ms -> {dest / 'Divi'}")
    return dest / "Divi"


VERSION_ARG = re.compile(r"\d+(?:\.\d+)+")


def valid_version_arg(version: str) -> bool:
    """`latest` or a dotted number such as 4.27.9 (anything else is a usage error, e.g. --help)."""
    return version == "latest" or VERSION_ARG.fullmatch(version) is not None


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    version = argv[0] if argv else "latest"
    if not valid_version_arg(version):
        print(f"fetch_divi: usage: fetch_divi.py [latest | VERSION like 4.27.9] (got {version!r})", file=sys.stderr)
        return 2
    try:
        path = ensure_divi(version)
    except FetchError as e:
        print(f"fetch_divi: {e}", file=sys.stderr)
        return 1
    print(json.dumps({"theme_dir": str(path)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
