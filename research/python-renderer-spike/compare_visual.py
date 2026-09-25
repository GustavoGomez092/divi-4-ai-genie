#!/usr/bin/env python3
"""Evaluation tooling: pixel-diff the builder-area screenshots from shoot.mjs and compare the
geometry/computed-style signatures. Uses Pillow (evaluation only; the renderer is stdlib-only).

  compare_visual.py <shotsdir> <truth-name> <python-name> [--side-by-side out.png]
"""
import hashlib
import json
import sys

from PIL import Image, ImageChops


def main():
    d, a, b = sys.argv[1:4]
    sbs = sys.argv[sys.argv.index("--side-by-side") + 1] if "--side-by-side" in sys.argv else None
    ga = json.load(open(f"{d}/{a}-geo.json"))
    gb = json.load(open(f"{d}/{b}-geo.json"))
    out = {}
    for w in ga:
        ia = Image.open(f"{d}/{a}-{w}.png").convert("RGB")
        ib = Image.open(f"{d}/{b}-{w}.png").convert("RGB")
        res = {"truth_size": ia.size, "python_size": ib.size}
        h = min(ia.size[1], ib.size[1])
        ca, cb = ia.crop((0, 0, ia.size[0], h)), ib.crop((0, 0, ib.size[0], h))
        mask = ImageChops.difference(ca, cb).convert("L").point(lambda x: 255 if x > 16 else 0)
        px = mask.histogram()[255]
        res["diff_pixels"] = px
        res["diff_pct"] = round(100 * px / (ca.size[0] * h), 4)
        res["diff_bbox"] = mask.getbbox()
        if px:
            mask.save(f"{d}/diff-{b}-{w}.png")
        ra, rb = ga[w]["rows"], gb[w]["rows"]
        res["elements"] = [len(ra), len(rb)]
        geo_a = [r[:6] for r in ra]
        geo_b = [r[:6] for r in rb]
        res["geometry_identical_elements"] = sum(1 for x, y in zip(geo_a, geo_b) if x == y)
        res["style_identical_elements"] = sum(1 for x, y in zip(ra, rb) if x == y)
        res["signature_equal"] = hashlib.sha1(json.dumps(ra).encode()).hexdigest() == hashlib.sha1(json.dumps(rb).encode()).hexdigest()
        res["first_mismatch"] = next(([x, y] for x, y in zip(ra, rb) if x != y), None)
        out[w] = res
        if sbs:
            scale = 0.35 if int(w) > 1000 else 0.6
            ta = ia.resize((int(ia.size[0] * scale), int(ia.size[1] * scale)))
            tb = ib.resize((int(ib.size[0] * scale), int(ib.size[1] * scale)))
            canvas = Image.new("RGB", (ta.size[0] + tb.size[0] + 20, max(ta.size[1], tb.size[1])), "white")
            canvas.paste(ta, (0, 0))
            canvas.paste(tb, (ta.size[0] + 20, 0))
            canvas.save(sbs.replace(".png", f"-{w}.png"), optimize=True)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
