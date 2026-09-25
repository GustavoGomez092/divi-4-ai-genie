#!/usr/bin/env python3
"""Ground-truth cache for the fidelity harness (research/tools/fidelity.py): renders a page
fixture with the real Divi theme via the Playground CLI (Task 14, scripts/preview/preview.mjs)
and caches the resulting HTML outside the repo (it contains Divi's licensed CSS).

  ground_truth.truth_path(fixture, divi_version)  -> PP_CACHE_DIR/truth/<ver>/<fixture-stem>.html
  ground_truth.ensure_truth(fixture, divi_version) -> that path, rendering first if missing/stale,
                                                       or None if node/Playground is unavailable.

Never raises: callers (fidelity tests, renderer comparisons) can skip gracefully in environments
without Node or a cached Divi build instead of failing.
"""
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
PREVIEW = ROOT / "Skill" / "divi-page-builder" / "scripts" / "preview" / "preview.mjs"

sys.path.insert(0, str(ROOT / "Skill" / "divi-page-builder" / "scripts"))
from fetch_divi import cache_root  # noqa: E402


def truth_path(fixture, divi_version: str) -> Path:
    return cache_root() / "truth" / divi_version / f"{Path(fixture).stem}.html"


def ensure_truth(fixture, divi_version: str, timeout: int = 600) -> Optional[Path]:
    """Renders `fixture` with the real Divi theme via the Playground CLI and returns the cached
    HTML path. Skips the render entirely when a cached copy already exists and is at least as new
    as the fixture. Returns None (never raises) when `node` isn't installed or the render fails."""
    fixture = Path(fixture)
    out = truth_path(fixture, divi_version)
    if out.exists() and out.stat().st_mtime >= fixture.stat().st_mtime:
        return out

    if shutil.which("node") is None:
        return None

    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(
            ["node", str(PREVIEW), "render", str(fixture), "--out", str(out), "--divi", divi_version],
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0 or not out.exists():
        return None
    return out
