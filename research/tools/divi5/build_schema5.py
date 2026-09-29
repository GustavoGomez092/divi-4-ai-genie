#!/usr/bin/env python3
"""Compile the raw Divi 5 schema dump plus the curated families5.json into scripts/schema5/.

Usage: build_schema5.py <research/divi5-schema> <families5.json> <out_dir> [--report]

Path model (the "union" model of research/divi5/schema.md §3, ported from schema_coverage.py): a module's
attribute paths are Divi's own group expander leaves (`leaves`), plus the D4->D5 conversion targets, plus the
block-level attrs, with option groups widened across modules by their `<decoration|meta|group advanced>.<key>`
root. Group-rooted attrs point at a family table in families5.json; module-specific attrs get an inline leaf
table typed from families5.json (module overrides, the module.json component map, or the Divi 4 field type via
the conversion map).

Coverage gate: exit 1 and list the offenders when an attr path of an in-scope module has a leaf that no
families5.json rule types. --report lists every untyped leaf (in and out of scope) and exits 0. Out-of-scope
leaves without evidence compile as opaque objects.

Also reads the Divi 4 dump next to the Divi 5 one (<dump>/../divi-schema/modules) for D4 field types. Writes
<out_dir>/<short>.json per module, families5.json and _meta.json (sorted keys, indent 1, trailing newline) and
removes any other *.json in out_dir.
"""
import json
import re
import sys
from fnmatch import fnmatchcase
from collections import defaultdict
from pathlib import Path

BREAKPOINTS_ALL = ["desktop", "tablet", "phone", "phoneWide", "tabletWide", "widescreen", "ultraWide"]
BREAKPOINTS_DEFAULT = ["desktop", "tablet", "phone"]
DEFAULT_STATES = ["value", "hover", "sticky"]
# Pseudo-states Divi's style renderer maps to :focus/:checked/:active; the VB exposes them on form fields.
FORM_STATES = ["focus", "checked", "active"]
# Leaf types that describe a whole structured value, so a deeper key under them belongs to that value.
STRUCTURED = {"object", "json", "icon", "spacing", "radius", "gradient"}
SCOPES_IN = ["core", "d5-extra"]

# Block-level attributes the converter writes outside any module attribute (Conversion::getAttrMap).
GLOBAL_RESPONSIVE = ("adminLabel", "themeBuilderArea", "globalColorsInfo", "on", "locked", "open")
# Option-group roots (schema_coverage.GROUP_ROOT): every `decoration.*` / `meta.*` key and the `advanced.*` keys
# that are groups. Other `advanced.*` keys are module-specific and never widened across modules.
GROUP_ROOT = re.compile(r"^(.*?)\.(decoration\.[A-Za-z0-9]+|meta\.[A-Za-z0-9]+|advanced\.(?:elements|gutter|html"
                        r"|htmlAttributes|link|loop|text|dividers|spamProtection|emailService))((?:\..*)?)$")

# ---- scope (research/divi5/schema.md §5 "Scope classification") ----------------------------------------------
CORE = {"accordion", "audio", "blurb", "button", "circle-counter", "code", "contact-form", "countdown-timer",
        "counters", "cta", "divider", "gallery", "heading", "icon", "image", "map", "number-counter",
        "pricing-tables", "signup", "slider", "social-media-follow", "tabs", "team-member", "testimonial", "text",
        "toggle", "video", "video-slider", "fullwidth-code", "fullwidth-header", "fullwidth-image",
        "fullwidth-map", "fullwidth-slider", "section", "row", "column", "row-inner", "column-inner"}
INTEGRATION = {"contact-form-7", "gravity-forms", "imagely-gallery", "instagram-feed"}
THEME_BUILDER = {"post-content", "fullwidth-post-content", "post-title", "fullwidth-post-title", "post-nav",
                 "comments", "breadcrumbs", "blog", "portfolio", "filterable-portfolio", "fullwidth-portfolio",
                 "post-slider", "fullwidth-post-slider", "post-filter", "post-filter-item", "menu",
                 "fullwidth-menu", "sidebar", "search", "login"}
INTERNAL = {"global-layout", "layout", "shortcode-module"}


def short(name):
    return name[5:] if name.startswith("divi/") else name


# ---- union path model -------------------------------------------------------------------------------------

def module_pairs(data):
    """(attrName, subName|None, strong) declared for one module: expander leaves (strong) + conversion targets."""
    pairs = {(i["attrName"], i.get("subName") or None, True) for i in data["leaves"].values()}
    for target in ((data.get("conversion") or {}).get("attributeMap") or {}).values():
        if not isinstance(target, str) or "*" not in target:
            continue
        attr, _, sub = target.partition(".*")
        pairs.add((attr, sub.lstrip(".") or None, False))
    return pairs


def effective(entries):
    """{attr: {subs}} from (attr, sub, strong) triples; "" = the whole value. A whole-attribute conversion target
    (weak) only counts when nothing declares sub-leaves for it (schema_coverage.load_leaves)."""
    idx = defaultdict(lambda: [False, False, set()])
    for attr, sub, strong in entries:
        if sub:
            idx[attr][2].add(sub)
        else:
            idx[attr][0 if strong else 1] = True
    out = {}
    for attr, (strong, weak, subs) in idx.items():
        s = set(subs)
        if strong or (weak and not subs):
            s.add("")
        out[attr] = s
    return out


# ---- families5.json ---------------------------------------------------------------------------------------

class Families:
    def __init__(self, src):
        self.types = set(src["_types"])
        self.leaves = src.get("leaves", {})
        self.fragments = src.get("fragments", {})
        self.tables = {}   # family -> {prefix: {sub: leaf}}
        self.by_key = {}   # group root key -> family
        for name, fam in src["families"].items():
            self.by_key[fam["key"]] = name
            self.tables[name] = {p: self.table(t, f"{name}:{p}") for p, t in fam["attrs"].items()}

    def leaf(self, spec, where):
        if isinstance(spec, str):
            if spec not in self.leaves:
                raise SystemExit(f"families5.json: unknown leaf reference {spec!r} at {where}")
            spec = self.leaves[spec]
        if spec.get("type") not in self.types:
            raise SystemExit(f"families5.json: {where} has type {spec.get('type')!r}, not one of _types")
        out = {"type": spec["type"], "bp": spec.get("bp", True), "states": list(spec.get("states", DEFAULT_STATES))}
        for k in ("options", "units", "multiple", "open", "note"):
            if k in spec:
                out[k] = spec[k]
        if "add" in spec:
            out["_add"] = spec["add"]  # kept although the union does not declare it (pruning exemption)
        if out["type"] == "enum" and not out.get("options"):
            raise SystemExit(f"families5.json: enum without options at {where}")
        return out

    def table(self, spec, where, _depth=0):
        """Expand a leaf table: {sub: leaf|leaf-ref, "@": frag|[frags], "@prefix": frag|[frags]}."""
        if isinstance(spec, str):
            spec = {"@": spec}
        if _depth > 8:
            raise SystemExit(f"families5.json: fragment include loop at {where}")
        out = {}
        for key, val in spec.items():
            if key.startswith("_"):
                continue
            if key.startswith("@"):
                prefix = key[1:]
                for frag in ([val] if isinstance(val, str) else val):
                    if frag not in self.fragments:
                        raise SystemExit(f"families5.json: unknown fragment {frag!r} at {where}")
                    for sub, leaf in self.table(self.fragments[frag], f"{where}/@{frag}", _depth + 1).items():
                        out[f"{prefix}.{sub}" if prefix and sub else prefix or sub] = leaf
            else:
                out[key] = self.leaf(val, f"{where}.{key}")
        return out


def has_children(table, sub):
    return any(k.startswith(sub + ".") for k in table) if sub else any(k for k in table)


def lookup_key(table, sub):
    """(key, leaf) of the entry that types `sub` (see lookup), or None; key is the covering entry's path."""
    if sub in table:
        return sub, table[sub]
    parts = sub.split(".")
    for i in range(len(parts) - 1, -1, -1):
        key = ".".join(parts[:i])
        anc = table.get(key)
        if anc is None:
            continue
        if anc["type"] in ("object", "json"):
            return (key, anc) if (anc.get("open") or not has_children(table, key)) else None
        return (key, anc) if anc["type"] in STRUCTURED else None
    return None


def lookup(table, sub):
    """The leaf typing `sub` in a leaf table: an exact entry, or an ancestor whose value holds it (a structured
    leaf such as spacing/icon, or an opaque object/json that is whole-valued or marked open). Same rule as
    divi5_schema._covering()."""
    hit = lookup_key(table, sub)
    return hit[1] if hit else None


# ---- module-specific typing -------------------------------------------------------------------------------

def field_items(node, out, attr=None):
    """(attrName, subName) -> module.json field items (component type "field"), found anywhere in the tree."""
    if isinstance(node, dict):
        attr = node.get("attrName", attr)
        comp = node.get("component")
        if isinstance(comp, dict) and comp.get("type") == "field" and attr:
            out[(attr, node.get("subName") or "")].append(node)
        for k, v in node.items():
            if k == "component" and isinstance(v, dict) and v.get("type") == "group":
                continue  # group field overrides belong to the family tables
            field_items(v, out, attr)
    elif isinstance(node, list):
        for v in node:
            field_items(v, out, attr)


def option_keys(opts):
    if isinstance(opts, dict) and opts:
        return [str(k) for k in opts]
    if isinstance(opts, list) and opts and all(isinstance(o, (str, int)) for o in opts):
        return [str(o) for o in opts]
    return None


def states_from(features, default=True):
    hover = features.get("hover", default)
    sticky = features.get("sticky", default)
    return ["value"] + (["hover"] if hover else []) + (["sticky"] if sticky else [])


def from_component(item, rules):
    comp = item["component"]
    rule = rules.get(comp.get("name") or "")
    if rule is None:
        return None
    props = comp.get("props") or {}
    feats = item.get("features") or {}
    t = rule["type"]
    dyn = feats.get("dynamicContent")
    if t == "text" and isinstance(dyn, dict) and dyn.get("type") == "url" and "url" in rule.get("dynamic", ()):
        t = "url"
    if t == "image" and props.get("dataType") not in (None, "image"):
        t = "url"
    leaf = {"type": t, "bp": bool(feats.get("responsive", True)), "states": states_from(feats)}
    if t == "length":
        units = props.get("allowedUnits")
        if units == [""] or (props.get("defaultUnit") == "" and not units):
            leaf["type"] = "number"
        elif units:
            leaf["units"] = [u for u in units if u]
    if t == "enum":
        opts = option_keys(props.get("options"))
        if not opts:
            leaf["type"] = rule.get("no_options", "text")
        else:
            leaf["options"] = opts
    if rule.get("multiple"):
        leaf["multiple"] = True
    return leaf


def from_d4(d4names, d4fields, expanders, rules):
    for n in d4names:
        f = d4fields.get(n)
        if not f:
            continue
        rule = rules.get(f.get("type") or "")
        if rule is None:
            continue
        t = rule["type"]
        if t == "image" and f.get("data_type") not in (None, "image"):
            t = "url"
        if t == "text" and f.get("dynamic_content") == "url":
            t = "url"
        leaf = {"type": t, "bp": bool(f.get("mobile_options")),
                "states": ["value"] + (["hover"] if f.get("hover") else []) + (["sticky"] if f.get("sticky") else []),
                "note": f"typed from Divi 4 {n} ({f.get('type')})"}
        if t == "enum":
            opts = None if n in expanders else option_keys(f.get("options"))
            if not opts:
                leaf["type"] = rule.get("no_options", "text")
            else:
                leaf["options"] = opts
        if t == "length" and f.get("allowed_units"):
            leaf["units"] = list(f["allowed_units"])
        if rule.get("multiple"):
            leaf["multiple"] = True
        return leaf
    return None


# ---- defaults ---------------------------------------------------------------------------------------------

def _is_responsive(d):
    return (isinstance(d, dict) and d and all(k in BREAKPOINTS_ALL for k in d)
            and all(isinstance(v, dict) and v for v in d.values()))


def flatten_defaults(node, prefix=""):
    out = {}
    if not isinstance(node, dict):
        return out
    for k, v in node.items():
        path = f"{prefix}.{k}" if prefix else k
        if _is_responsive(v):
            out[path] = v
        elif isinstance(v, dict):
            out.update(flatten_defaults(v, path))
    return out


# ---- build ------------------------------------------------------------------------------------------------

def scope_of(slug):
    if slug == "shop" or slug.startswith("woocommerce-"):
        return "woocommerce"
    if slug in INTEGRATION:
        return "integration"
    if slug in THEME_BUILDER:
        return "theme-builder"
    if slug in INTERNAL:
        return "internal"
    return "core" if slug in CORE else None  # None: decided after children are known


def form_roots(data):
    roots = set(re.findall(r'"name": "divi/form-field", "props": \{"attrName": "([^"]+)"',
                           json.dumps(data["settings"])))
    for name, attr in (data.get("attributes") or {}).items():
        if isinstance(attr, dict) and attr.get("elementType") == "field":
            roots.add(name)
    return roots


def with_form_states(leaf):
    if "hover" not in leaf["states"]:
        return leaf
    return dict(leaf, states=leaf["states"] + [s for s in FORM_STATES if s not in leaf["states"]])


def build(dump_dir, families_path, out_dir, report=False):
    dump_dir, out_dir = Path(dump_dir), Path(out_dir)
    src = json.loads(Path(families_path).read_text())
    fam = Families(src)
    index = json.loads((dump_dir / "index.json").read_text())
    raw = {slug: json.loads((dump_dir / "modules" / f"{slug}.json").read_text()) for slug in sorted(index["modules"])}
    d4_dir = dump_dir.parent / "divi-schema" / "modules"

    # widened group catalogue: key -> {(rest, sub, strong)}
    pairs = {slug: module_pairs(data) for slug, data in raw.items()}
    catalogue = defaultdict(set)
    for slug in raw:
        for attr, sub, strong in pairs[slug]:
            m = GROUP_ROOT.match(attr)
            if m:
                catalogue[m.group(2)].add((m.group(3).lstrip("."), sub, strong))

    offenders, report_lines = [], []

    # compiled family tables: only the paths the union declares (or entries marked "add"), so that fragments can be
    # supersets without widening the allow-list
    pruned = {}
    for name, fdef in src["families"].items():
        eff = effective(catalogue.get(fdef["key"], ()))
        pruned[name] = {}
        for rest, table in fam.tables[name].items():
            subs = eff.get(rest, set())
            kept = {s: {k: v for k, v in leaf.items() if k != "_add"} for s, leaf in table.items()
                    if s in subs or "_add" in leaf}
            if kept:
                pruned[name][rest] = kept

    # family coverage (one check per group key, shared by every module that has the root)
    family_gaps = defaultdict(list)
    for key, entries in sorted(catalogue.items()):
        name = fam.by_key.get(key)
        for rest, subs in sorted(effective(entries).items()):
            table = pruned.get(name, {}).get(rest) if name else None
            for sub in sorted(subs):
                if table is None or lookup(table, sub) is None:
                    family_gaps[key].append(f"{key}{'.' + rest if rest else ''} :: {sub or '<whole>'}")
    used_keys_in_scope = set()

    children = {}
    for slug, data in raw.items():
        m = data["module"]
        kids = list(m.get("childrenName") or [])
        if m.get("childModuleName") and m["childModuleName"] not in kids:
            kids.append(m["childModuleName"])
        children[slug] = kids
    cat = {slug: raw[slug]["module"].get("category") for slug in raw}
    content_modules = sorted(f"divi/{s}" for s in raw if cat[s] in ("module", "unsupported"))
    fullwidth = sorted(f"divi/{s}" for s in raw if cat[s] == "fullwidth-module")
    rules = {  # structure rules (placement is enforced in JS; see schema.md §5)
        "section": ["divi/row", "divi/column", "divi/row-inner"] + fullwidth,
        "row": ["divi/column"],
        "column": content_modules + ["divi/row-inner", "divi/group"],
        "row-inner": ["divi/column-inner"],
        "column-inner": content_modules + ["divi/group"],
        "group": content_modules,
    }
    for slug, extra in rules.items():
        children[slug] = sorted(set(children[slug]) | set(extra))
    parents = defaultdict(set)
    for slug, kids in children.items():
        for k in kids:
            parents[short(k)].add(f"divi/{slug}")

    scopes = {slug: scope_of(slug) for slug in raw}
    for slug in raw:  # children of core parents are core
        if scopes[slug] is None and any(scopes.get(short(p)) == "core" and cat[slug] == "child-module"
                                        for p in parents[slug]):
            scopes[slug] = "core"
    for slug in raw:
        if scopes[slug] is None:
            scopes[slug] = "d5-extra"

    comp_rules, d4_rules = src["components"], src["d4_types"]
    block_attrs = src["block"]
    css_leaf = fam.leaf(src["css"], "css")
    overrides = src.get("modules", {})
    aliases = src.get("attr_aliases", {})
    common_over = [(pat, fam.table(spec, f"modules.*.{pat}")) for pat, spec in overrides.get("*", {}).items()
                   if not pat.startswith("_")]

    modules_out = {}
    for slug, data in raw.items():
        m = data["module"]
        in_scope = scopes[slug] in SCOPES_IN
        eff = effective(pairs[slug] | {(g, None, True) for g in GLOBAL_RESPONSIVE})
        alias_of = {}  # attr -> the declared attr it mirrors (families5.json "attr_aliases")
        for dst, src_prefix in sorted(aliases.get(slug, {}).items()):
            if dst.startswith("_"):
                continue
            for attr in [a for a in sorted(eff) if a.startswith(src_prefix)]:
                new = dst + attr[len(src_prefix):]
                if new not in eff:
                    eff[new] = set(eff[attr])
                    alias_of[new] = attr
        roots = {(mm.group(1), mm.group(2)) for mm in (GROUP_ROOT.match(a) for a in eff) if mm}
        forms = form_roots(data)
        attrs = {}
        for prefix, key in sorted(roots):
            name = fam.by_key.get(key)
            if in_scope:
                used_keys_in_scope.add(key)
            for rest in sorted({r for r, _, _ in catalogue[key]}):
                attr = f"{prefix}.{key}{'.' + rest if rest else ''}"
                if name is None or rest not in pruned[name]:
                    continue  # reported through family_gaps
                ref = {"family": name, "prefix": rest}
                if prefix.split(".")[0] in forms:
                    ref["states_extra"] = FORM_STATES
                attrs[attr] = ref
        fi = defaultdict(list)
        field_items(data["attributes"], fi)
        field_items(data["settings"], fi)
        am = (data.get("conversion") or {}).get("attributeMap") or {}
        expanders = set(((data.get("conversion") or {}).get("valueExpansionFunctionMap") or {}))
        rev = defaultdict(list)
        for d4, target in am.items():
            if isinstance(target, str) and "*" in target:
                a, _, s = target.partition(".*")
                rev[(a, s.lstrip("."))].append(d4)
        d4file = d4_dir / f"{m.get('d4Shortcode')}.json"
        d4fields = json.loads(d4file.read_text())["fields"] if m.get("d4Shortcode") and d4file.exists() else {}
        own_over = [(pat, fam.table(spec, f"modules.{slug}.{pat}")) for pat, spec in overrides.get(slug, {}).items()
                    if not pat.startswith("_")]
        for attr, subs in sorted(eff.items()):
            if GROUP_ROOT.match(attr):
                continue
            table = {}
            src_attr = alias_of.get(attr, attr)
            own = [t for pat, t in own_over if fnmatchcase(src_attr, pat)]
            common = [t for pat, t in common_over if fnmatchcase(src_attr, pat)]
            # override entries marked "add" extend the declared sub-leaves (evidence in their "add" text)
            subs = set(subs) | {k for t in own + common for k, leaf in t.items() if "_add" in leaf}
            for sub in sorted(subs):
                hit, why = None, ""
                for t in own:
                    hit = hit or lookup_key(t, sub)
                if hit is None and attr in block_attrs:
                    hit = sub, fam.leaf(block_attrs[attr], f"block.{attr}")
                if hit is None and attr == "css":
                    hit = sub, css_leaf
                if hit is None and fi.get((src_attr, sub)):
                    leaf = from_component(fi[(src_attr, sub)][0], comp_rules)
                    why = f"component {fi[(src_attr, sub)][0]['component'].get('name')}"
                    hit = (sub, leaf) if leaf else None
                if hit is None:
                    leaf = from_d4(rev.get((src_attr, sub), []), d4fields, expanders, d4_rules)
                    hit = (sub, leaf) if leaf else None
                for t in common:
                    hit = hit or lookup_key(t, sub)
                if hit is None:
                    line = f"{slug}: {attr} :: {sub or '<whole>'}" + (f"  ({why})" if why else "") + \
                           (f"  d4={rev[(src_attr, sub)]}" if rev.get((src_attr, sub)) else "")
                    report_lines.append(("IN " if in_scope else "out ") + line)
                    if in_scope:
                        offenders.append(line)
                        continue
                    hit = sub, {"type": "object", "bp": True, "states": ["value", "hover", "sticky"],
                                "note": "untyped: out-of-scope module, no evidence"}
                key, leaf = hit
                leaf = {k: v for k, v in leaf.items() if k != "_add"}
                if attr.split(".")[0] in forms:
                    leaf = with_form_states(leaf)
                table[key] = leaf
            if not table:
                continue
            attrs[attr] = table[""] if set(table) == {""} else {"sub": table}
        css = sorted(eff.get("css", ()))
        modules_out[slug] = {
            "name": m["name"], "d4": m.get("d4Shortcode"), "category": m.get("category"), "scope": scopes[slug],
            "children": children[slug] or None, "parents": sorted(parents[slug]), "attrs": attrs,
            "css": [c for c in css if c], "defaults": flatten_defaults((data.get("defaults") or {}).get("render")),
        }

    for key in sorted(used_keys_in_scope):
        if key not in fam.by_key:
            offenders.append(f"family for group root {key}: missing in families5.json")
        offenders.extend(f"family gap {g}" for g in family_gaps.get(key, []))
    for key, gaps in sorted(family_gaps.items()):
        report_lines.extend(("IN " if key in used_keys_in_scope else "out ") + f"family gap {g}" for g in gaps)

    if report:
        print("\n".join(report_lines) or "no untyped leaves")
        return 0
    if offenders:
        print(f"coverage gate: {len(offenders)} untyped leaves in in-scope modules:")
        print("\n".join("  " + o for o in offenders))
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    written = set()

    def write(name, obj):
        (out_dir / name).write_text(json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False) + "\n")
        written.add(name)

    for slug, mod in modules_out.items():
        write(f"{slug}.json", mod)
    write("families5.json", {"_notes": src.get("_notes", ""), "_types": src["_types"],
                             "families": {n: {"key": f["key"], "_notes": f.get("_notes", ""), "attrs": pruned[n]}
                                          for n, f in src["families"].items()}})
    write("_meta.json", {"divi_version": index["divi_version"], "breakpoints_default": BREAKPOINTS_DEFAULT,
                         "breakpoints_all": BREAKPOINTS_ALL, "states": index["states"], "scopes_in": SCOPES_IN,
                         "generated_by": "build_schema5.py"})
    for stale in out_dir.glob("*.json"):
        if stale.name not in written:
            stale.unlink()
    return 0


def main(argv):
    args = [a for a in argv if a != "--report"]
    if len(args) != 3:
        print(__doc__)
        return 2
    return build(*args, report="--report" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
