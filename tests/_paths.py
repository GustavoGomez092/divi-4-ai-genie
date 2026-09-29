"""Shared paths for tests; importing this puts the skill scripts and tools on sys.path."""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "Skill" / "divi-page-builder"
SCRIPTS = SKILL / "scripts"
TOOLS = ROOT / "research" / "tools"
FIXTURES = ROOT / "tests" / "fixtures"
RAW_SCHEMA = ROOT / "research" / "divi-schema"
WP_LOCAL = TOOLS / "wp-local.sh"

for p in (SCRIPTS, TOOLS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

FIXTURES5 = FIXTURES / "divi5"
SCHEMA5_RAW = ROOT / "research" / "divi5-schema"
TOOLS5 = TOOLS / "divi5"
LOCAL5_ENV = {"LOCAL_SITE_ID": "fTZ3hcgdI",
              "LOCAL_SITE_PATH": str(Path.home() / "Local Sites" / "divi-5-test" / "app" / "public")}
SITE5_URL = "http://divi-5-test.local"


def d5_fixtures():
    """All valid Divi 5 block fixtures (excludes anything under divi5/invalid/)."""
    invalid = FIXTURES5 / "invalid"
    return sorted(p for p in FIXTURES5.rglob("*.html") if invalid not in p.parents)


def d5_invalid_fixtures():
    return sorted((FIXTURES5 / "invalid").rglob("*.html"))


def wp5(*args, timeout=120):
    import subprocess
    env = dict(os.environ, **LOCAL5_ENV)
    return subprocess.run([str(WP_LOCAL), *map(str, args)], capture_output=True, text=True, env=env,
                          timeout=timeout)


def _site5_up() -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(SITE5_URL + "/", timeout=5)
        return True
    except Exception:
        return False


LIVE_SKIP_REASON = ("live test: touches the local WordPress site (divi-test.local via wp-local.sh) or reads "
                    "Elegant Themes credentials; set PP_LIVE_TESTS=1 to run it")


def live_tests_enabled() -> bool:
    return os.environ.get("PP_LIVE_TESTS") == "1"


def live_only(obj):
    """Skip a test class/method unless PP_LIVE_TESTS=1 (evaluated at import time)."""
    return unittest.skipUnless(live_tests_enabled(), LIVE_SKIP_REASON)(obj)


LIVE5_SKIP_REASON = ("live test: touches the local Divi 5 site (divi-5-test.local via wp-local.sh); "
                     "set PP_LIVE_TESTS=1 and start the site to run it")


def live5_only(obj):
    return unittest.skipUnless(live_tests_enabled() and _site5_up(), LIVE5_SKIP_REASON)(obj)
