#!/usr/bin/env python3
"""Check that every attribute path in Divi 5 block content is declared by the raw schema dump.

Usage: schema_coverage.py <research/divi5-schema> <file.txt>... [--source preset|union] [--json]

For each `<!-- wp:divi/<slug> {attrs} -->` block, the attrs JSON is walked into
(attrName, breakpoint, state, subName) tuples. A responsive attribute is a dict whose keys are
all breakpoint names and whose values are dicts keyed by state names. A tuple is covered when the
module's `leaves` (research/divi5-schema/modules/<slug>.json) contain `attrName` with no subName,
or `attrName__X` where X equals the subName or is a dotted prefix of it.

--source preset  only the module's `leaves` (Divi's own group expander, Conversion::get_preset_attrs_mapping)
--source union   (default) the model proposed for the validator in research/divi5/schema.md:
                 leaves + D4->D5 conversion targets + block-level attrs, with option groups widened to
                 every leaf seen for the same `<decoration|advanced|meta>.<key>` in any module.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BREAKPOINTS = {"desktop", "tablet", "phone", "phoneWide", "tabletWide", "widescreen", "ultraWide"}
STATES = {"value", "hover", "sticky", "focus", "checked", "active"}
BLOCK = re.compile(r"<!-- wp:(divi/[a-z0-9-]+)(?: (\{.*?\}))? /?-->")
# Block-level bookkeeping attributes that are not module settings.
TOP_LEVEL = {"builderVersion", "modulePreset", "groupPreset", "globalModule", "globalParent", "nonconvertible",
             "shortcodeName"}


def is_responsive(node):
    return (isinstance(node, dict) and node and set(node) <= BREAKPOINTS
            and all(isinstance(v, dict) and v and set(v) <= STATES for v in node.values()))


def sub_paths(value, prefix=""):
    if isinstance(value, dict) and value:
        for k, v in value.items():
            yield from sub_paths(v, f"{prefix}.{k}" if prefix else k)
    else:
        yield prefix or None


def walk(attrs, path=""):
    """Yield (attrName, breakpoint, state, subName) for every leaf value."""
    for key, node in attrs.items():
        name = f"{path}.{key}" if path else key
        if not path and key in TOP_LEVEL:
            yield name, None, None, None
        elif is_responsive(node):
            for bp, states in node.items():
                for st, value in states.items():
                    for sub in sub_paths(value):
                        yield name, bp, st, sub
        elif isinstance(node, dict) and node:
            yield from walk(node, name)
        else:
            yield name, None, None, None


def covered(leaves_index, attr, sub):
    whole, subs = leaves_index.get(attr, (False, ()))
    if whole:
        return True
    if sub is None:
        return bool(subs)
    return any(sub == s or sub.startswith(s + ".") for s in subs)


# Block-level attributes the converter writes outside any module attribute (Conversion::getAttrMap,
# Conversion.php:1185-1206): responsive ones (`locked.desktop.value`) and plain ones.
GLOBAL_RESPONSIVE = {"adminLabel", "themeBuilderArea", "globalColorsInfo", "on", "locked", "open"}
# Option-group roots: every `decoration.*` and `meta.*` key, and the `advanced.*` keys that are groups
# (groups.json settingKeyToGroup plus a few group-backed ones). Other `advanced.*` keys are module-specific
# fields and are never widened across modules.
GROUP_ROOT = re.compile(r"^(.*?)\.(decoration\.[A-Za-z0-9]+|meta\.[A-Za-z0-9]+|advanced\.(?:elements|gutter|html|htmlAttributes"
                        r"|link|loop|text|dividers|spamProtection|emailService))((?:\..*)?)$")


def module_pairs(data, source):
    """(attrName, subName|None, from_expander) triples declared for one module.

    from_expander is True for Divi's own group expander (`leaves`). A whole-attribute entry from
    the expander (e.g. `icon.innerContent`, whose icon-picker value is an object) accepts any
    sub-key; a whole-attribute conversion target (e.g. `title.decoration.font.font.*`, a packed D4
    font expanded into an object) only counts when the expander knows no sub-leaves for it.
    """
    pairs = {(i["attrName"], i.get("subName") or None, True) for i in data["leaves"].values()}
    if source == "union":
        for target in ((data.get("conversion") or {}).get("attributeMap") or {}).values():
            if not isinstance(target, str) or "*" not in target:
                continue
            attr, _, sub = target.partition(".*")
            pairs.add((attr, sub.lstrip(".") or None, False))
    return pairs


def group_catalogue(schema_dir, source):
    """`decoration.background` -> {(rest-of-attrName, subName, from_expander)} across all modules."""
    cat = defaultdict(set)
    for f in sorted((Path(schema_dir) / "modules").glob("*.json")):
        for attr, sub, strong in module_pairs(json.loads(f.read_text()), source):
            m = GROUP_ROOT.match(attr)
            if m:
                cat[m.group(2)].add((m.group(3), sub, strong))
    return cat


def load_leaves(schema_dir, slug, source, cache={}):
    """attrName -> (accepts any sub-key, known subNames)."""
    if (slug, source) not in cache:
        f = Path(schema_dir) / "modules" / f"{slug}.json"
        idx = defaultdict(lambda: [False, False, set()])  # strong whole, weak whole, subs
        if f.exists():
            pairs = module_pairs(json.loads(f.read_text()), source)
            if source == "union":
                cat = cache.setdefault(("__cat__", source), group_catalogue(schema_dir, source))
                roots = {(m.group(1), m.group(2)) for m in (GROUP_ROOT.match(a) for a, _, _ in pairs) if m}
                for prefix, key in roots:
                    pairs |= {(f"{prefix}.{key}{rest}", sub, strong) for rest, sub, strong in cat[key]}
                pairs |= {(g, None, True) for g in GLOBAL_RESPONSIVE}
            for attr, sub, strong in pairs:
                if sub:
                    idx[attr][2].add(sub)
                else:
                    idx[attr][0 if strong else 1] = True
        cache[(slug, source)] = {k: (v[0] or (v[1] and not v[2]), tuple(v[2])) for k, v in idx.items()}
    return cache[(slug, source)]


def main(argv):
    as_json = "--json" in argv
    source = "union"
    if "--source" in argv:
        source = argv[argv.index("--source") + 1]
        argv = argv[:argv.index("--source")] + argv[argv.index("--source") + 2:]
    args = [a for a in argv if a != "--json"]
    schema_dir, files = args[0], args[1:]
    total = hit = 0
    distinct, distinct_hit = set(), set()
    missing = Counter()
    states, bps = Counter(), Counter()
    for f in files:
        for m in BLOCK.finditer(Path(f).read_text()):
            slug = m.group(1)[len("divi/"):]
            attrs = json.loads(m.group(2)) if m.group(2) else {}
            leaves = load_leaves(schema_dir, slug, source)
            for attr, bp, st, sub in walk(attrs):
                if bp is None and attr in TOP_LEVEL:
                    continue
                total += 1
                bps[bp] += 1
                states[st] += 1
                key = (slug, attr, sub)
                distinct.add(key)
                if covered(leaves, attr, sub):
                    hit += 1
                    distinct_hit.add(key)
                else:
                    missing[f"{slug}: {attr}" + (f" .{sub}" if sub else "") + ("" if bp else "  (non-responsive)")] += 1
    report = {
        "files": len(files),
        "values": total, "values_covered": hit,
        "distinct_paths": len(distinct), "distinct_covered": len(distinct_hit),
        "breakpoints": dict(bps), "states": dict(states),
        "missing": dict(missing.most_common()),
    }
    if as_json:
        print(json.dumps(report, indent=1, default=str))
        return
    pct = lambda a, b: f"{100 * a / b:.2f}%" if b else "n/a"
    print(f"source: {source}   files: {len(files)}")
    print(f"values: {hit}/{total} covered ({pct(hit, total)})")
    print(f"distinct (module, attrName, subName): {len(distinct_hit)}/{len(distinct)} ({pct(len(distinct_hit), len(distinct))})")
    print(f"breakpoints: {dict(bps)}")
    print(f"states: {dict(states)}")
    for k, n in missing.most_common():
        print(f"  MISSING x{n}: {k}")


if __name__ == "__main__":
    main(sys.argv[1:])
