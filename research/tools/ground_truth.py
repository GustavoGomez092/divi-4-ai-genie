#!/usr/bin/env python3
"""Ground-truth cache for the fidelity harness (research/tools/fidelity.py): renders a page
fixture with the real Divi theme via the Playground CLI (Task 14, scripts/preview/preview.mjs)
and caches the resulting HTML outside the repo (it contains Divi's licensed CSS).

  ground_truth.truth_path(fixture, divi_version[, tokens])  -> PP_CACHE_DIR/truth/<ver>/<fixture-stem>[.tokens-<sha8>].html
  ground_truth.ensure_truth(fixture, divi_version[, tokens]) -> that path, rendering first if missing/stale,
                                                                or None if node/Playground is unavailable.

Divi 5 (Task 21-R5a): a 5.x version renders a Divi 5 block fixture the way `preview.py render` does (the page
staged with its local images inlined, and with `tokens` the site's recovered global colours, variables and
preset CSS seeded: preview.seed_css / seed_options). The tokens file's content hash is part of the cache name,
so one fixture can have a truth with and one without tokens.

  python3 research/tools/ground_truth.py FIXTURE --divi VER [--tokens tokens.json]   (prints the cached path)

Never raises: callers (fidelity tests, renderer comparisons) can skip gracefully in environments
without Node or a cached Divi build instead of failing.
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
PREVIEW = ROOT / "Skill" / "divi-page-builder" / "scripts" / "preview" / "preview.mjs"

sys.path.insert(0, str(ROOT / "Skill" / "divi-page-builder" / "scripts"))
from fetch_divi import cache_root  # noqa: E402


def _major(divi_version: str) -> int:
    head = str(divi_version).split(".", 1)[0]
    return int(head) if head.isdigit() else (5 if str(divi_version) == "latest5" else 4)


def truth_path(fixture, divi_version: str, tokens=None) -> Path:
    stem = Path(fixture).stem
    if tokens:
        stem += ".tokens-" + hashlib.sha1(Path(tokens).read_bytes()).hexdigest()[:8]
    return cache_root() / "truth" / divi_version / f"{stem}.html"


def _render_d5(fixture: Path, out: Path, divi_version: str, tokens, timeout: int):
    """preview.py render's Divi 5 path without its CLI: stage (local images inlined, token seed sidecars),
    then preview.mjs render on the staged page."""
    import preview  # the skill's preview.py (seed_css/seed_options/stage_block_page)
    seed, options = preview.load_seed(str(tokens) if tokens else None)
    with tempfile.TemporaryDirectory(prefix="pp-truth5-") as stage:
        staged = preview.stage_block_page(fixture, Path(stage), seed, options=options)
        return subprocess.run(["node", str(PREVIEW), "render", str(staged), "--out", str(out), "--divi", divi_version],
                              capture_output=True, text=True, timeout=timeout)


def ensure_truth(fixture, divi_version: str, timeout: int = 600, tokens=None) -> Optional[Path]:
    """Renders `fixture` with the real Divi theme via the Playground CLI and returns the cached
    HTML path. Skips the render entirely when a cached copy already exists and is at least as new
    as the fixture (and the tokens file). Returns None (never raises) when `node` isn't installed or the
    render fails. `tokens` (Divi 5 only): a tokens.json whose design data is seeded like `preview.py --tokens`."""
    fixture = Path(fixture)
    try:
        out = truth_path(fixture, divi_version, tokens)
        newest_input = max([fixture.stat().st_mtime] + ([Path(tokens).stat().st_mtime] if tokens else []))
    except OSError:
        return None
    if out.exists() and out.stat().st_mtime >= newest_input:
        return out

    if shutil.which("node") is None:
        return None

    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        if _major(divi_version) >= 5:
            proc = _render_d5(fixture, out, divi_version, tokens, timeout)
        else:
            proc = subprocess.run(
                ["node", str(PREVIEW), "render", str(fixture), "--out", str(out), "--divi", divi_version],
                capture_output=True, text=True, timeout=timeout,
            )
    except Exception:  # noqa: BLE001 (never raises: OSError, SubprocessError, a bad tokens file...)
        return None
    if proc.returncode != 0 or not out.exists():
        return None
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("fixture")
    ap.add_argument("--divi", required=True)
    ap.add_argument("--tokens")
    a = ap.parse_args()
    path = ensure_truth(a.fixture, a.divi, tokens=a.tokens)
    print(path or "unavailable (Node, Playground or the cached Divi build)")
    sys.exit(0 if path else 1)
