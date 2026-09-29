#!/usr/bin/env python3
"""Ground truth: real Divi 5.13.1 renders via the shipped Playground preview (preview.py render).
  truth.py NAME=PAGE [NAME=PAGE ...] [--tokens FILE]   -> out/truth/NAME-d5.html (gitignored)"""
import subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIEW = ROOT / "Skill/divi-page-builder/scripts/preview.py"
args = sys.argv[1:]
tokens = []
if "--tokens" in args:
    i = args.index("--tokens"); tokens = ["--tokens", args[i + 1]]; del args[i:i + 2]
for a in args:
    name, page = a.split("=", 1)
    out = HERE / "out/truth" / f"{name}-d5.html"
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, str(PREVIEW), "render", page, "--out", str(out), *(tokens or ["--divi", "5.13.1"])],
                           capture_output=True, text=True, timeout=300)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = "timeout"
    print(f"{name}: rc={rc} {time.time() - t0:.1f}s {out.stat().st_size if out.exists() else 0} bytes", flush=True)
    if rc != 0:
        print(p.stderr[-2000:] if rc != "timeout" else "", flush=True)
