# Divi 5 Support for Divi Genie: Design Spec

- **Date:** 2026-09-28
- **Status:** Approved direction (user, 2026-09-28): approach A (research first, native Divi 5 authoring), one skill
  for both formats, Playground preview first and a measured Python-renderer spike after, and the research phase
  and file layout as presented. On 2026-09-28 the user delegated all remaining decisions ("proceed on your own
  using your best judgement"). Decisions taken under that delegation are marked **[delegated]**.
- **Builds on:** `docs/superpowers/specs/2026-09-24-divi-page-builder-skill-design.md` (Divi 4 spec, "D4 spec").
- **Research:** `research/divi5/` (storage-and-serialization, schema, tokens-and-detection, divi-ai, playground),
  raw schema dump `research/divi5-schema/`, tools `research/tools/divi5/`.

## 1. Goal

Divi Genie must build and edit pages on **Divi 5** sites as well as it does on Divi 4 sites: tokens, compose,
validate, preview, draft, publish. It must also be tested the same way: Divi acts as the judge, and there are
generated docs with a coverage gate, a byte-stable parser, preview fidelity measured against real Divi, a live
publish flow, and fresh-agent skill tests. It is one skill. It detects the site's Divi major version and writes
Divi 4 shortcode or Divi 5 blocks accordingly. All Divi 4 behaviour stays byte-for-byte unchanged.

### Success criteria
1. From a brief and a Divi 5 site's `tokens.json`, an AI following the skill writes Divi 5 block content. That
   content passes `validate.py` with 0 errors and renders on the site with the site's fonts, colors, spacing and
   presets.
2. Every attribute path of every in-scope Divi 5 module is documented, on the module's page or in a linked
   design family. A generator check enforces this, and every leaf has a curated value type.
3. Edits to existing Divi 5 pages change only the intended blocks. Every other block stays byte-identical.
4. The schema and docs regenerate from Divi with documented commands when Divi 5 updates.
5. `preview.py` previews Divi 5 pages with real Divi (Playground), with fidelity numbers recorded against the
   local Divi 5 site.
6. `publish.py` creates Divi 5 drafts over REST with an Application Password, and the builder layout is in effect
   (§2.6).
7. The whole existing test suite still passes unchanged, and the Divi 5 suite passes, including the opt-in live tests.

### Non-goals
- WooCommerce modules, third-party integration modules (contact-form-7, gravity-forms, imagely-gallery,
  instagram-feed) and Theme Builder, loop and site-level modules.
- Divi 5's native flex/grid authoring for new layouts **[delegated]**. See §3.1. It is documented as a later
  extension once Visual Builder-authored ground truth exists.
- Creating global colors, variables or presets on client sites. REST cannot do it (research R6).
- The v2 "AI Agent" fixtures. They need an interactive Elegant Themes sign-in.
- Patching Divi 4 shortcode pages that live on a Divi 5 site. Those are regenerated as blocks or migrated first.

## 2. Background findings (established by research)

1. **Storage** (`storage-and-serialization.md`). `post_content` is WordPress block markup:
   `<!-- wp:divi/<name> {JSON} -->…<!-- /wp:divi/<name> -->`, and `/-->` for empty leaves. All module content,
   including HTML, lives in the JSON (`…innerContent.desktop.value`). Nothing sits between the tags. The builder
   wraps the page in `<!-- wp:divi/placeholder -->`.
   - **Canonical form.** WordPress's `serialize_block_attributes()` escaping (`\u0022 \u003c \u003e \u0026
     \u002d\u002d`, `\\` → `\u005c`), no whitespace between blocks, and self-closing empty leaves. Every PHP path
     reaches this form and leaves it unchanged.
   - **Raw `<`, `>`, `&` or `"` inside the JSON destroys the page** for authors without `unfiltered_html`.
2. **Value model.** Each attribute is nested as attrName group → `innerContent` / `decoration` / `advanced` /
   `meta` → breakpoint (`desktop`, `tablet`, `phone`) → state (`value`, `hover`, `sticky`).
   - The extra breakpoints (`phoneWide`, `tabletWide`, `widescreen`, `ultraWide`) are off by default.
   - There are no enable flags: presence means enabled.
   - Global references are written as `$variable({"type":"color","value":{"name":"gcid-…","settings":{}}})$`.
     Other variables use `"type":"content"` with `gvid-…` names.
   - Presets are referenced as `modulePreset: ["default" | id]` and as `groupPreset`.
   - `builderVersion` on each block selects flex versus legacy layout and which render-time migrations run.
3. **Schema** (`schema.md`). `module.json` and `_all_modules_metadata.php` describe module-specific fields.
   Shared option groups are only references. A runtime dump (`research/tools/divi5/dump-schema.php`) joins
   three Divi sources: the preset expander, the D4 → D5 conversion map and the block-level attributes. It
   covers **100%** of the paths in Divi-converted content (7,272 values, 529 paths) and in on-site content, and
   it rejects invented paths. Leaf **value types** for the shared groups exist only in minified JS, so a
   hand-curated `families5.json` (about 20 families) supplies them. Placement rules live in JS, so the
   structure docs are hand-written.
4. **Divi AI** (`divi-ai.md`). The v1 API still returns D4 shortcode, which the Divi 5 builder converts on the
   server through `/divi/v1/content-conversion`: kses, then `maybeConvertContent`, then the
   `divi_framework_portability_import_migrated_post_content` migrations, then the placeholder wrap.
   `research/tools/divi5/convert.php` reproduces that path, minus kses.
5. **Tokens and detection** (`tokens-and-detection.md`).
   - **Where the data lives:** global colors in `et_divi[et_global_data][global_colors]`, variables in
     `et_divi_global_variables`, presets in `et_divi_builder_global_presets_d5`.
   - **What public pages expose:** `--gcid-*`, `--gvid-*` and `--et_global_*` CSS custom properties, plus
     per-preset CSS classes (`preset--module--<m>--<id>`).
   - **What REST can't do:** read or write any of it with an Application Password (`invalid_nonce`).
   - **Detection:** the site's major version comes from `/wp-content/themes/Divi/style.css`, or from `?ver=`
     and `/includes/builder-5/` asset paths. For a page, `[et_pb_` means shortcode and `<!-- wp:divi/` means
     blocks.
   - **Divi 4 pages on Divi 5:** they render through a degraded legacy path and are never converted in the
     database.
6. **Publishing** (`storage-and-serialization.md` §2 and its addendum).
   - `POST /wp/v2/pages` stores content as sent for users with `unfiltered_html`.
   - **`meta._et_pb_use_builder` is silently dropped over REST on Divi 5.13.1.** Divi registers the key only
     once its D4 shortcode framework loads, which happens lazily while a D4 shortcode is rendered.
   - **Verified fix:** create the page with a D4 stub (`[et_pb_section][/et_pb_section]`), then send one
     `/batch/v1` request. Its first item re-saves the page, so rendering the stub registers the key. Its second
     item sets the real content and the meta. The front end then shows `et_pb_pagebuilder_layout et_no_sidebar`,
     no title and no sidebar.
   - CSS regenerates on the next view after a REST update.
   - On WordPress 7.0 and later, `content.raw` is the canonical re-serialization, not the stored bytes.
7. **Preview** (`playground.md`): see §4.8.

## 3. Decisions

1. **Layout form [delegated].** New Divi 5 content uses the "block layout" form that Divi's converter produces:
   `module.decoration.layout.desktop.value.display: "block"` on structure elements,
   `row.module.advanced.columnStructure`, and `column.module.advanced.type`. That form has Divi-authored ground
   truth (35 converted fixtures and Divi AI output), renders identically to Divi 4, and lets the Divi 4 recipes'
   layout knowledge carry over. Flex/grid authoring is out of scope until VB-authored fixtures exist.
2. **Canonical serialization.** The serializer always emits WordPress canonical form wrapped in
   `divi/placeholder`. The parser accepts any valid form: converter output, VB output and escaping variants.
3. **`builderVersion`** is the site's Divi version (`tokens.json → site.divi_version`) on every block the skill
   creates. Otherwise it defaults to the schema's dump version.
4. **Module scope [delegated].** Everything in the dump except WooCommerce, the four integrations, Theme
   Builder/loop/site modules and internal blocks (`placeholder`, `shortcode-module`, `global-layout`,
   `canvas-portal`, etc.).
   - Included: the 33 Divi 4-equivalent core and fullwidth modules, their children, the structure blocks, and
     the Divi 5 extras that are content modules. The doc generator and schema list the exact set.
   - Recipes use the core modules.
5. **References over literals.** When `tokens.json` has a global color, variable or preset id for a role, the
   skill writes the reference. Otherwise it writes the value inline.
   - Never an id that isn't in `tokens.json`. The validator warns.
   - An unknown `modulePreset` silently drops default preset styling.
   - To get the site default, omit `modulePreset` or use `["default"]`.
6. **Publishing the builder meta [delegated].** `publish.py draft` on a Divi 5 site uses the stub-and-batch
   sequence (§2.6) whenever the page's `_et_pb_use_builder` is not already `on`. It then reads the meta back
   and fails loudly if it isn't `on`. For a live page lacking the meta, `publish` refuses and explains, rather
   than briefly swapping its content.
7. **Divi 4 shortcode pages on a Divi 5 site** are not patched. `page_edit.py`/`publish.py` refuse, and the
   skill says to regenerate the page as blocks, using the D4 page as a style source, or to migrate it in Divi first.
8. **Porting recipes.** Each Divi 4 recipe's worked example is converted with `convert.php`, then cleaned: set
   `builderVersion`, drop `locked` and redundant render defaults, replace the attribute-row UUIDs. Validation and
   a live render check follow. The format-neutral recipe text stays shared.
9. **Preview.** Playground (real Divi 5) first. A Python renderer is decided by a measured spike afterwards (§4.8).

## 4. Components

File layout (approved section 2): Divi 4 files stay where they are. Divi 5 gets new modules and folders, and the
shared entry points become version-aware.

```
Skill/divi-page-builder/
├── SKILL.md                         + "Which Divi?" intake step; Divi 5 index
├── reference/  (Divi 4 files unchanged; publishing/preview/design-tokens gain Divi 5 sections)
│   └── divi5/ page-format.md, structure.md, value-formats.md, design-families.md,
│              modules/README.md + modules/<name>.md (generated)
├── recipes/    (neutral text shared) + recipes/divi5/sections|pages/<name>.md (D5 worked examples)
└── scripts/
    ├── divi_format.py        detect content format and site major version
    ├── divi5_blocks.py       parse/serialize blocks; canonical JSON escaping; tree edit helpers
    ├── divi5_schema.py       load schema5/, resolve attribute paths and leaf specs
    ├── divi5_checks_structure.py / divi5_checks_values.py / divi5_checks_tokens.py
    ├── schema5/<name>.json + families5.json + _meta.json   (generated/curated)
    ├── tokens5_from_blocks.py, tokens5_from_html.py
    └── validate.py, publish.py, page_edit.py, extract_tokens.py, preview.py   (version-aware)
research/tools/divi5/  dump-schema.php, build_schema5.py, generate_docs5.py, families5 source,
                       convert.php, judge harness, ground truth
```

### 4.1 `divi_format.py`
- `detect_content(text)` returns `"shortcode"`, `"blocks"`, `"mixed"` or `"empty"`.
- `major_from_version("5.13.1")` returns 5.
- `detect_site(url)` reads the Divi `style.css` Version, falling back to asset `?ver=` values and
  `/includes/builder-5/`.
- Every version-aware entry point uses it.

### 4.2 `divi5_blocks.py` (Divi 4 counterpart: `divi_shortcode.py`)
- `parse(text)` returns a document of blocks: `{name, attrs (dict, key order kept), raw_json, children,
  span, inner_html_chunks}`. It uses WordPress's block grammar and accepts any JSON escaping, `/-->`, whitespace,
  and freeform HTML between blocks (kept verbatim).
- `serialize(doc)` is byte-exact on unmodified input: spans are reused, and only changed blocks are
  re-emitted in canonical form.
- `to_canonical(value)` implements `serialize_block_attributes()`.
- Helpers:
  - `line_col`;
  - block paths (`section[2] > row[0] > column[1] > blurb[0]`);
  - attribute get/set by dotted path plus breakpoint and state;
  - `new_block(name, attrs, children)` in canonical form;
  - `variable_refs(value)`, which extracts `$variable(...)$`.

### 4.3 Schema: dump, `families5.json`, compile, resolve
- **Dump:** `research/tools/divi5/dump-schema.php` writes `research/divi5-schema/`, as in R2.
- **`families5.json`** is hand-curated in `research/tools/divi5/families5.json`. For each family it lists
  relative leaves `{type, options, units, bp, states}`, using the type set in `schema.md` §7.
- **Compile:** `build_schema5.py` compiles the dump plus the families into `scripts/schema5/<name>.json`.
  Each file holds name, d4 slug, category, scope, children, parents, attrs (a union path model with leaf specs
  or family refs), css slots and defaults. There is also `_meta.json` with the Divi version, breakpoints and
  families.
- **Coverage gate:** the build fails if any in-scope leaf path has no type.
- **Resolve:** `divi5_schema.py` resolves a concrete path (`title.decoration.font.font.tablet.value.size`)
  to a leaf spec plus the breakpoint and state. The result is known, unknown-attr, bad-breakpoint or bad-state.

### 4.4 Validator (Divi 5 checks)
`validate.py` detects the format.
- **Shortcode:** today's code path, unchanged.
- **Blocks:** the Divi 5 checks below, reported through the same `Finding` and `Reporter` model, the same
  output and JSON, and the same `--baseline`/`--fragment`/`--tokens`.
- **Mixed:** an error (`E5_MIXED_FORMAT`).

| Check | Level |
|---|---|
| Bad block comment, bad JSON, unbalanced or misnested open/close | error |
| Unknown block name, or an out-of-scope module | error / warning |
| Parent/child in both directions; section type rules (regular → rows; fullwidth → fullwidth modules; specialty → column rules); `columnStructure` ↔ column `type` sequence | error |
| Unknown attribute path; illegal breakpoint (a non-default one → warning); illegal state (e.g. hover on a leaf without hover) | error |
| Value type, options, units; malformed `$variable()$` | error |
| Raw `<`, `>`, `&` or `"` inside the JSON (non-canonical, breaks for non-`unfiltered_html` authors); literal `[`/`]` in HTML content | error / warning |
| Headings: exactly one H1, no skipped levels (from `headingLevel` and HTML in text) | error / warning, same codes as D4 |
| `modulePreset`/`groupPreset` ids not `default` and not in tokens; `gcid`/`gvid` ids not in tokens | warning |
| External image URLs; missing alt | warning |
| With `--tokens`: colors, fonts and spacing off the site's token set (literal values only) | warning |
| `builderVersion` missing, or differing from the site's version | warning |

### 4.5 Docs: `generate_docs5.py`
From the schema and families:
- `reference/divi5/modules/<name>.md` for each in-scope module, with a header, a minimal valid example checked
  by the validator, content fields, design families with their attrName prefixes, advanced fields, and CSS slots;
- `reference/divi5/modules/README.md`;
- the generated tables in `reference/divi5/design-families.md`.

Hand-written notes are merged from `research/tools/divi5/notes/<name>.md`. The **coverage check** fails
generation if any path is neither listed on the module page nor covered by a linked family.

### 4.6 Hand-written references (`reference/divi5/`)
- `page-format.md`: block grammar, canonical escaping, placeholder, meta, `builderVersion`, where things are
  stored.
- `structure.md`: section types, `columnStructure` values and column type sequences, inner rows,
  parent/child pairs.
- `value-formats.md`: the value model (breakpoints and states), every leaf type with its grammar and an
  example, `$variable()$`, presets, icons, images, links.
- `publishing.md`, `preview.md` and `design-tokens.md` gain Divi 5 sections.

### 4.7 Tokens
`extract_tokens.py` detects the site's major version. On Divi 5 it runs `tokens5_from_blocks.py` over
`content.raw` and `tokens5_from_html.py` over the public HTML and CSS. The output is Divi 4's `tokens.json` shape
plus:
- `site.divi_major` and `site.content_format`;
- `colors.global` entries (`id → {value, label?}`) and `colors.customizer` from the `:root` variables;
- a new `variables` section (numbers, fonts, images by `gvid`);
- Divi 5 `presets` (per module and group: `id`, uses, recovered CSS);
- `module_styles` and `section_exemplars` holding Divi 5 attribute subtrees, with `$variable()$` strings kept.

The fidelity requirement is the same as the D4 spec's §4.10.

### 4.8 Preview
`preview.py render|serve --exact` for Divi 5 content runs `scripts/preview/preview.mjs` with the Divi version
from `tokens.json`. It uses the same fetch/cache (`fetch_divi.py`) and the same blueprint and mu-plugin, made
version-aware. Content is injected as block markup. The default (non-`--exact`) path on Divi 5 is Playground
until the Python-renderer spike says otherwise (it said GO: see Addendum A), so `render`/`serve` work without `--exact`, and `doctor` checks
Node. Findings and numbers: `research/divi5/playground.md` (§7 below records the outcome).

### 4.9 `page_edit.py` and `publish.py`
- **`page_edit.py`** gets the same verbs on block documents: `outline`, `extract`, `replace`, `insert-after`,
  `insert-before`, `set-attr` (dotted path + breakpoint/state) and `delete`. Untouched bytes are preserved.
- **`publish.py`:**
  - format-aware validation;
  - image upload and rewrite in block JSON (`src`/`url` leaves);
  - the builder-meta sequence of §3.6, with read-back;
  - refuses D4 content on a Divi 5 site and D5 content on a Divi 4 site;
  - `fetch` warns that `content.raw` is canonicalized.

### 4.10 Recipes, `SKILL.md`
- **Recipes:** `recipes/divi5/sections/<name>.md` and `recipes/divi5/pages/<name>.md` hold the D5 worked
  example and field mapping for every D4 recipe. The worked examples are validated by `check_doc_examples.py`.
- **`SKILL.md`:**
  - the triggers add Divi 5;
  - intake detects the version;
  - the workflow is shared, with version-specific file pointers;
  - hard rules gain the Divi 5 ones (canonical JSON, never invent `gcid`/`gvid`/preset ids, no D4 shortcode
    on D5 sites, `builderVersion`).

## 5. Workflow (SKILL.md)
Unchanged steps: intake, tokens, plan, compose, validate, preview (then stop for approval), draft, then publish
on approval. Step 1 adds **"Which Divi?"**, taken from `tokens.json → site.divi_major`. If that's missing, run
`divi_format.py` detection. Compose reads `reference/divi5/*` and `recipes/divi5/*` for Divi 5.

## 6. Testing and verification (mirrors D4 spec §6)

| Component | Verification |
|---|---|
| `divi5_blocks.py` | Byte-exact round-trip on all 37 Divi 5 fixtures and on canonical output. Canonical escaping equals WordPress's `serialize_block_attributes()`, compared live through WP-CLI on the escape corpus |
| Schema build | Coverage gate (every in-scope leaf typed). Deterministic output. 100% of paths in all fixtures resolve. Bogus paths are rejected |
| Validator | `unittest`: all fixtures valid (0 errors). One broken fixture per error class. **Divi as judge:** Divi's `parse_blocks` and render accept every valid fixture, and the parsed attrs equal ours |
| Docs | Coverage check. Every module page example validates. Regeneration gives an empty diff |
| Tokens | A local Divi 5 page with known global colors, variables, a module preset and a group preset. The extracted tokens reproduce them (live, opt-in) |
| Publishing | Live on `divi-5-test.local`: draft via REST with an Application Password, builder meta `on`, rendered layout checked, page deleted (opt-in) |
| Preview | Each fixture renders in Playground. Markup and CSS compared with the local Divi 5 site (opt-in), numbers recorded |
| Recipes | Every D5 worked example validates, and each is pushed to the local site once and screenshotted |
| Skill | Fresh-agent test on a Divi 5 brief (baseline versus with the skill), as in D4 Task 21 |

Live tests use a separate gate: `@live5_only` and `PP_LIVE_TESTS=1`, against `divi-5-test.local` through
`LOCAL_SITE_ID=fTZ3hcgdI`.

## 7. Risks
- **`families5.json` is hand-curated.** Mitigation: coverage gate, the fixture corpus, and a Divi-judge render
  check of typed values.
- **The batch meta workaround depends on Divi internals.** Mitigation: read-back and fail loudly. The live test
  catches regressions after Divi updates.
- **Weekly Divi 5 releases.** Mitigation: regeneration commands, a deterministic dump, and `builderVersion` taken
  from tokens.
- **Converted-form layout versus native flex.** Mitigation: documented. Revisit when VB fixtures exist.

## Addendum A: Python renderer for Divi 5 previews (decided 2026-09-29)

**Evidence:** `research/divi5/python-renderer-spike.md`, measured against real Divi 5.13.1 (Playground truth).
- **Reusing the Divi 4 renderer through a D5→D4 conversion was rejected.** A perfect back-conversion still matches only 23–52 % of Divi 5's builder CSS declarations.
- **A native renderer driven by the theme's `module.json` metadata** gave, for 6 modules:
  - byte-identical markup and 343/343 declarations on the tuned page, with a 0.000 % pixel diff at 1440 px;
  - untuned held-out pages at 89.7 % and 96.7 % of declarations with 0 wrong;
  - 5–7 ms per render, against 1–5 s in Playground.

**Decision:**
- `preview.py render|serve` renders Divi 5 block pages with a stdlib Python renderer (`scripts/divi5_render/`) by default.
- `--exact` keeps the Playground preview.
- When the coverage report lists an unsupported module or option on a page, `preview.py` renders that page in Playground automatically if Node 20+ is available. Otherwise it shows the Divi 4-style banner naming what is missing.
- When the page's Divi version has not passed the Divi 5 parity corpus, the Playground path is used for that version.

**Scope:** the ~28 module types the Divi 5 recipes emit. Site-data and WooCommerce modules render fallback blocks.
Flex/grid layout, interactions, sticky/scroll and loop content are unsupported and escalate.

**Acceptance:**
- Every module has a tuned D5 fixture whose builder markup (tag and class sequence) and builder-CSS declaration set match Playground truth exactly.
- Each batch records a held-out page's pre-fix numbers in `research/divi5/render-fidelity.md`.
- Batch 1 must reach 95 % or more of declarations with no layout shift, with every other miss named by coverage. Otherwise the work stops and Playground stays the only Divi 5 preview.

**Unchanged:** Divi assets are never committed. The WordPress draft is still the authoritative visual check. The
`.seed.css`/options seeding stays for the Playground path. The Python path reads the same `tokens.json` (global
colours, variables, presets).

Outcome (2026-09-29): the batch-1 gate FAILED on the pre-fix engine. The held-out page reached 94.3 % of the builder CSS declarations (982/1041) against the 95 % bar, with 2 extra declarations that coverage did not name and a layout shift from the fourth section (disabledOn not ported). Under the pre-registered gate this is NO-GO: the engine is parked in `research/divi5/python-renderer/` (tests still run there, the gate test is an expected failure), Tasks 21-R5c..f are cancelled, and Playground remains the only Divi 5 preview. It is resumable; see `research/divi5/python-renderer/README.md`.
