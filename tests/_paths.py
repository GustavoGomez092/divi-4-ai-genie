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


LIVE_SKIP_REASON = ("live test: touches the local WordPress site (divi-test.local via wp-local.sh) or reads "
                    "Elegant Themes credentials; set PP_LIVE_TESTS=1 to run it")


def live_tests_enabled() -> bool:
    return os.environ.get("PP_LIVE_TESTS") == "1"


def live_only(obj):
    """Skip a test class/method unless PP_LIVE_TESTS=1 (evaluated at import time)."""
    return unittest.skipUnless(live_tests_enabled(), LIVE_SKIP_REASON)(obj)
