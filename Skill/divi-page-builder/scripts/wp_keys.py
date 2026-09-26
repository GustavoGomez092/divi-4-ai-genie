"""Multi-site WordPress credentials, and optional Elegant Themes credentials, from a keys.json file.

File format (every ``keys`` entry needs name/site/user/key, each a non-empty string; other
top-level keys ignored)::

    {
      "elegant_themes": {"username": "you@example.com", "api_key": "xxxxxxxxxxxxxxxxxxxxxxxx"},
      "keys": [
        {"name": "Test Key Local site", "site": "http://divi-test.local", "user": "user",
         "key": "xxxx xxxx xxxx xxxx xxxx xxxx"},
        {"name": "Client A", "site": "https://client-a.com", "user": "seo-bot",
         "key": "xxxx xxxx xxxx xxxx xxxx xxxx"}
      ]
    }

Both top-level sections are optional; a file may hold either one or both (a missing ``keys``
means no site entries). The top level must be an object; ``keys``, if present, must be a list;
``elegant_themes``, if present, must be an object with non-empty string ``username`` and
``api_key``.

Location, in order of precedence: the ``--keys PATH`` flag, the env var ``DIVI_KEYS_FILE``, then
the default ``~/.config/divi-page-builder/keys.json``. A KeysError's message never contains a key
value or an api_key -- only names, sites, users and paths, none of which are secret.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_FIELDS = ("name", "site", "user", "key")


class KeysError(Exception):
    """A one-line, user-facing message. Never contains a key value."""


def default_keys_path() -> Path:
    return Path.home() / ".config" / "divi-page-builder" / "keys.json"


def resolve_keys_path(keys_path=None):
    """Return (Path, explicit) applying the --keys / DIVI_KEYS_FILE / default precedence."""
    if keys_path:
        return Path(keys_path), True
    env = os.environ.get("DIVI_KEYS_FILE")
    if env:
        return Path(env), True
    return default_keys_path(), False


_WARNED: set = set()


def _warn_if_insecure(path: Path) -> None:
    """Warn once per path per process (a command may read the file more than once)."""
    if os.name != "posix" or str(path) in _WARNED:
        return
    try:
        mode = path.stat().st_mode
    except OSError:
        return
    if mode & 0o077:
        _WARNED.add(str(path))
        print(f"keys.json is readable by other users; run chmod 600 {path}", file=sys.stderr)


def _entry_label(index: int, entry) -> str:
    label = f"keys[{index}]"
    if isinstance(entry, dict):
        name = entry.get("name")
        if isinstance(name, str) and name:
            label += f" ({name!r})"
    return label


def _validate_entry(index: int, entry) -> None:
    label = _entry_label(index, entry)
    if not isinstance(entry, dict):
        raise KeysError(f"{label} is not an object")
    for field in REQUIRED_FIELDS:
        value = entry.get(field)
        if not isinstance(value, str) or not value:
            raise KeysError(f"{label}: {field!r} must be a non-empty string")


def _read_keys_object(p: Path) -> dict:
    """Parse and top-level-validate the keys file at `p`, warn if insecure, and return the raw
    dict. Shape rules: the top level must be an object; "keys", if present, must be a list;
    "elegant_themes", if present, must be an object. Field-level validation happens elsewhere.
    Raises KeysError; never leaks a key value."""
    if not p.exists():
        raise KeysError(f"keys file not found: {p}")
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise KeysError(f"cannot read {p}: {exc}") from None
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        raise KeysError(f"invalid JSON in {p}: {exc}") from None
    if not isinstance(obj, dict):
        raise KeysError(f"{p}: expected a JSON object")
    if "keys" in obj and not isinstance(obj["keys"], list):
        raise KeysError(f"{p}: \"keys\" must be a list")
    if "elegant_themes" in obj and not isinstance(obj["elegant_themes"], dict):
        raise KeysError(f"{p}: \"elegant_themes\" must be an object")
    _warn_if_insecure(p)
    return obj


def load_keys(path) -> list:
    """Load and validate every `keys` entry in the keys file at `path` (a missing "keys" means no
    entries -- the file may hold only "elegant_themes"). Raises KeysError; never leaks a key value."""
    p = Path(path)
    obj = _read_keys_object(p)
    entries = obj.get("keys") or []
    for i, entry in enumerate(entries):
        _validate_entry(i, entry)
    seen = {}
    for entry in entries:
        norm = entry["name"].strip().lower()
        if norm in seen:
            raise KeysError(f"duplicate key name (case-insensitive): {seen[norm]!r} and {entry['name']!r}")
        seen[norm] = entry["name"]
    return entries


def _validate_et(et, path: Path) -> None:
    if not isinstance(et, dict):
        raise KeysError(f"{path}: \"elegant_themes\" must be an object")
    username = et.get("username")
    if not isinstance(username, str) or not username:
        raise KeysError(f"{path}: \"elegant_themes.username\" must be a non-empty string")
    api_key = et.get("api_key")
    if not isinstance(api_key, str) or not api_key:
        raise KeysError(f"{path}: \"elegant_themes.api_key\" must be a non-empty string")


def file_elegant_themes(keys_path=None) -> dict | None:
    """The `elegant_themes` section straight from the keys file (ignoring ET_* env), found by the
    same --keys / DIVI_KEYS_FILE / default precedence as everything else. None when the section is
    absent, or the default path doesn't exist. An explicit missing path is a KeysError, like
    load_keys. Never leaks the api_key."""
    path, explicit = resolve_keys_path(keys_path)
    if not path.exists():
        if explicit:
            raise KeysError(f"keys file not found: {path}")
        return None
    obj = _read_keys_object(path)
    et = obj.get("elegant_themes")
    if et is None:
        return None
    _validate_et(et, path)
    return et


def resolve_et_credentials(keys_path=None):
    """Return (username, api_key) for Elegant Themes: env ET_USERNAME + ET_API_KEY (both set) win;
    otherwise the keys file's "elegant_themes" section (same location precedence as everything
    else); otherwise None. The default path not existing is not an error; an explicit missing path
    is a KeysError, like load_keys. Never leaks the api_key."""
    env_user = os.environ.get("ET_USERNAME")
    env_key = os.environ.get("ET_API_KEY")
    if env_user and env_key:
        return env_user, env_key
    et = file_elegant_themes(keys_path)
    if et is None:
        return None
    return et["username"], et["api_key"]


def _load_entries(keys_path=None) -> list:
    """Entries for the resolved path, or [] when the default path doesn't exist (not an error)."""
    path, explicit = resolve_keys_path(keys_path)
    if not path.exists():
        if explicit:
            raise KeysError(f"keys file not found: {path}")
        return []
    return load_keys(path)


def list_keys(keys_path=None) -> list:
    """Public view of every entry: name/site/user only, never the key."""
    return [{"name": e["name"], "site": e["site"], "user": e["user"]} for e in _load_entries(keys_path)]


def normalize_site(url: str) -> str:
    """Lowercase scheme+host, strip a trailing slash from the path; the path itself is kept."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}"


def resolve_credentials(key_name=None, site=None, user=None, keys_path=None):
    """Return (site, user, password) per the precedence and matching rules in the module docstring."""
    entries = _load_entries(keys_path)

    if key_name:
        matches = [e for e in entries if e["name"].lower() == key_name.lower()]
        if not matches:
            available = ", ".join(e["name"] for e in entries) or "(none)"
            raise KeysError(f"no key named {key_name!r}; available: {available}")
        entry = matches[0]
        if site and normalize_site(site) != normalize_site(entry["site"]):
            raise KeysError(f"--site does not match key {entry['name']!r}")
        if user and user != entry["user"]:
            raise KeysError(f"--user does not match key {entry['name']!r}")
        return entry["site"], entry["user"], entry["key"]

    if site and entries:
        target = normalize_site(site)
        matches = [e for e in entries if normalize_site(e["site"]) == target]
        if user:
            matches = [e for e in matches if e["user"] == user]
        if len(matches) == 1:
            entry = matches[0]
            return entry["site"], entry["user"], entry["key"]
        if len(matches) > 1:
            names = ", ".join(e["name"] for e in matches)
            raise KeysError(f"multiple keys match {site}: {names}; pass --key or --user")

    password = os.environ.get("WP_APP_PASSWORD", "")
    if site and user and password:
        return site, user, password
    raise KeysError("no credentials: pass --key NAME (keys file) or --site, --user and env WP_APP_PASSWORD")
