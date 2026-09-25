"""Shared paths for tests; importing this puts the skill scripts and tools on sys.path."""
import sys
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
