# Page format (Divi 5)

How a Divi 5 page is stored and what you write for one. Use this file when the site runs Divi 5
(`tokens.json` → `site.divi_major` is 5, or `divi_format.py` detects it); the Divi 4 counterpart is
[../page-format.md](../page-format.md). Block nesting is in [structure.md](structure.md), attribute values in
[value-formats.md](value-formats.md), each block's attributes in [modules/README.md](modules/README.md).

Evidence lives in the repo only (`research/divi5/…`); section numbers point into those files. "Live check" means
the markup was pushed to a Divi 5.13.1 site (WordPress 7.1.2) and the rendered page read back
(`research/divi5/doc-experiments.md`).

## What Divi 5 stores

A Divi 5 page's `post_content` is **WordPress block markup**: nested HTML comments of the form
`<!-- wp:divi/<name> {JSON} -->`. It is not Divi 4 shortcode, and the JSON inside each comment holds everything:
text, HTML, URLs, styles (`storage-and-serialization.md` §1.1).

| what | where | does a page you write touch it? |
|---|---|---|
| the layout and all content | `post_content`: `divi/*` blocks inside one `divi/placeholder` block | **yes**, it is what you write |
| builder flags | post meta `_et_pb_use_builder` (required, see [Post meta](#post-meta)), `_et_pb_use_divi_5` | `publish.py` sets `_et_pb_use_builder` |
| page settings (custom CSS, gutter width, …) | post meta, under the Divi 4 key names (`_et_pb_custom_css`, …) | no |
| Customizer settings and **global colors** | option `et_divi`: the five Customizer colors (`accent_color`, …) and `et_divi['et_global_data']['global_colors']` | no, read only |
| **design variables** (numbers, fonts, images, strings, links, gradients) | option `et_divi_global_variables` | no, read only |
| **module and option-group presets** | option `et_divi_builder_global_presets_d5` (Divi 4 presets from `et_divi_builder_global_presets_ng` are converted into it, keeping their ids) | no, read only |
| generated CSS | files in `wp-content/et-cache/<post id>/`, inlined into the page on the first view | no, Divi writes it |

(`tokens-and-detection.md` §2 for the options; `storage-and-serialization.md` §1.2 and §2.4 for meta and CSS.)

A page refers to global colors, variables and presets **by id** (see
[value-formats.md → `$variable`](value-formats.md#variable-references-global-colors-and-design-variables) and
[→ presets](value-formats.md#presets-modulepreset-and-grouppreset)). It never defines them, and it can't: every Divi
route that writes them needs a Visual Builder nonce that an Application Password cannot get
(`tokens-and-detection.md` §3.6).

## Block grammar

- **Opener** `<!-- wp:divi/<name> {JSON} -->`, **closer** `<!-- /wp:divi/<name> -->`, **leaf** (a block with no
  child blocks) `<!-- wp:divi/<name> {JSON} /-->`. Names are lowercase: `divi/section`, `divi/text`,
  `divi/accordion-item`.
- Write exactly one space after `<!--`, one space between the name and the JSON, and one space before `-->` or `/-->`.
  WordPress's parser needs whitespace after the JSON (`wp-includes/class-wp-block-parser.php:247-253`), and Divi's
  feature detector matches `<!-- wp:` with exactly one space (`SimpleBlockParser.php:164-169`;
  `storage-and-serialization.md` §4.1).
- **Nothing sits between the comments except child blocks.** A Divi block's own inner HTML is always empty; the
  comment pair only delimits its children.
- Write leaves self-closing and put no whitespace or newlines between blocks. Divi's converter writes empty
  open/close pairs, and the Visual Builder puts `\n\n` between blocks; both parse to the same tree
  (§4.1, §6.1), but the self-closing, no-whitespace form is WordPress's canonical one (below).
- Every block you create carries `builderVersion` ([below](#builderversion)). Blocks nest
  `divi/placeholder` → `divi/section` → `divi/row` → `divi/column` → module (→ child module); see
  [structure.md](structure.md).

A complete one-section page:

```divi5
<!-- wp:divi/placeholder --><!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#0b2a3c"}}},"spacing":{"desktop":{"value":{"padding":{"top":"96px","bottom":"96px"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Emergency Plumber in Miami"}},"decoration":{"font":{"font":{"desktop":{"value":{"color":"#ffffff","size":"56px","weight":"700","headingLevel":"h1"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eLicensed \u0026amp; insured plumbers at your door in 60 minutes.\u003c/p\u003e"}}},"module":{"advanced":{"text":{"text":{"desktop":{"value":{"color":"dark"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Call now","linkUrl":"tel:+13055550100"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section --><!-- /wp:divi/placeholder -->
```

The text sets `module.advanced.text.text` → `{"color": "dark"}`: its text sits on a dark background, so Divi renders
it light (Divi 4's `background_layout="dark"`, which the conversion map sends to this key; the default is `light`).

The same `divi/heading` block, formatted for reading only (on the page it is escaped and on one line, as above):

```json
{"title": {"innerContent": {"desktop": {"value": "Emergency Plumber in Miami"}},
           "decoration": {"font": {"font": {"desktop": {"value":
             {"headingLevel": "h1", "color": "#ffffff", "size": "56px", "weight": "700"}}}}}},
 "builderVersion": "5.13.1"}
```

## The `divi/placeholder` wrapper

- The Visual Builder wraps every saved page in `<!-- wp:divi/placeholder -->` … `<!-- /wp:divi/placeholder -->`
  (`serialized-post.js`; PHP twin `ModuleUtils::wrap_placeholder_block()`, `ModuleUtils.php:2311-2352`). The Divi 5
  Migrator and portability import wrap converted pages the same way. Without it, content loaded into the builder
  can lose everything after the first row (`MigrationUtils.php:99-120`, `storage-and-serialization.md` §1.3).
- It renders nothing, and unwrapped pages render identically (verified on 35 pages), but always write it: one
  wrapper, at the top level, holding only `divi/section` blocks. An empty page is `<!-- wp:divi/placeholder /-->`.
- `validate.py` warns `W5_NO_PLACEHOLDER` when a page isn't wrapped (not with `--fragment`), reports
  `E5_TOPLEVEL` for anything but a section inside it, and `E5_BAD_PARENT` for a nested placeholder.
- `divi5_blocks.wrap_placeholder()` wraps a list of sections; `serialize()` writes it.

## All content lives in the JSON

Every module keeps its content in its attributes, under `<element>.innerContent.desktop.value` (plus other
breakpoints where the element is responsive):

| content | where | value |
|---|---|---|
| text module body | `content.innerContent` | HTML string: `"<p>…</p>"` |
| heading text | `title.innerContent` (`divi/heading`) | plain string (it is output as HTML) |
| blurb title | `title.innerContent` (`divi/blurb`) | object `{"text", "url", "target"}` |
| button label and link | `button.innerContent` | object `{"text", "linkUrl", "linkTarget"}` |
| image | `image.innerContent` | object `{"src", "alt", "titleText", "linkUrl", …}` |

Each module page in [modules/](modules/README.md) lists its content attributes. Text between the comments is not
content: `validate.py` reports it as `E5_NOT_DIVI` and Divi ignores it. The one Divi block that keeps content
between its tags is `divi/shortcode-module` (an unconvertible Divi 4 module, `Conversion.php:1646`): never write
one, and keep any you find on an existing page byte for byte (`tokens-and-detection.md` §6).

How HTML values render (`storage-and-serialization.md` §6.3):

- Text-module `content` goes through `wpautop` **and `do_shortcode`**. A `[caption]` in it vanished and
  `[et_pb_text]…[/et_pb_text]` rendered a Divi 4 module inside the Divi 5 text. See
  [Literal brackets](#literal-brackets-in-text).
- A heading title is output as raw HTML (`<b>` stays bold, `&amp;` stays an entity).
- Divi 4's attribute escapes (`%22`, `%91`, `%93`, `%92`) mean nothing in Divi 5: they render literally. Divi's
  converter decodes them (`Conversion::restoreSpecialChars()`, `Conversion.php:2522-2540`).

## Canonical JSON escaping, and why

Write the block JSON exactly as WordPress's `serialize_block_attributes()` does (`wp-includes/blocks.php:1705-1719`,
`storage-and-serialization.md` §4.2). It is ordinary JSON plus five substitutions inside strings:

| character in a value | written as | note |
|---|---|---|
| `"` | `\u0022` | never `\"` |
| `<` | `\u003c` | |
| `>` | `\u003e` | |
| `&` | `\u0026` | also inside URLs and HTML entities: `&amp;` → `\u0026amp;` |
| `--` | `\u002d\u002d` | so the value can't close the comment |
| `\` | `\u005c` | a backslash in the value (JSON `\\`) |
| non-ASCII (`ü`, `€`, `😀`) | raw UTF-8 | not `\u00fc` |
| `/` | unchanged | never `\/` |
| newline, tab | `\n`, `\t` | ordinary JSON escapes |

Also: no spaces in the JSON, keys in the order you build them, and an empty object `{}` written as `[]` (PHP's
encoder cannot tell them apart). **Build blocks with `divi5_blocks.new_block()` + `render_block()` /
`serialize()`, or `canonical_json()`: never by hand.** `validate.py` reports a block whose JSON contains a raw `<`,
`>`, `&`, `--` or `\"` as `E5_NONCANONICAL`.

Why it matters (`storage-and-serialization.md` §6.2): the same page was stored six ways and rendered.

- For an Administrator (who has `unfiltered_html`) all six store byte-for-byte and render identically.
- For an author **without `unfiltered_html`**, WordPress's kses re-parses the block comments. Plain JSON with raw
  `<` or `"` **destroyed the page** (the heading and text did not render at all); the canonical form survived.
  Even then, kses rewrote every `&` in every string attribute to `&amp;` and stripped `<script>` tags and `onclick`
  handlers.
- The canonical form is also what every WordPress and Divi PHP path writes back (kses, REST reads, migrations), so a
  page written canonically round-trips byte for byte and later edits diff cleanly (§6.1).

A text whose HTML has quotes, `&`, tags and `--`:

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eTerms \u0026 \u0022conditions\u0022 \u003cstrong\u003eapply\u003c/strong\u003e \u002d\u002d see \u003ca href=\u0022/terms/\u0022\u003eterms\u003c/a\u003e.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## `builderVersion`

- Set `"builderVersion"` on **every block you create** to the site's Divi version: `tokens.json` →
  `site.divi_version`, else the schema's version (`scripts/schema5/_meta.json` → `divi_version`, `5.13.1`).
  `validate.py` warns `W5_BUILDER_VERSION` when it is missing (and, with `--tokens`, when it differs from the site's;
  on existing blocks you edit that warning is expected: leave their version as it is).
- It is not bookkeeping. Divi upgrades content stored with an older `builderVersion` in memory on every render,
  running each migration whose release is newer (`storage-and-serialization.md` §6.4). A block with no
  `builderVersion` rendered with Divi 4's block layout (`et_block_section`), the same block with `5.13.1` with Divi 5's
  flex layout (`et_flex_section`, `FlexboxMigration.php:99,296-300`; §5). New content therefore states the layout
  it wants explicitly: see [structure.md → layout form](structure.md#the-layout-form-display-block-on-structure-blocks).
- **Blocks you don't create keep theirs.** Converter output carries `5.0.0-public-alpha.*`, `5.0.0-public-beta.1`,
  `5.1.1` or even `4.27.9` (`tokens-and-detection.md` §5), and relies on the migrations that version triggers.
  When you edit such a page, change only the blocks you mean to change, and don't change `builderVersion` on the
  blocks you edit either: Divi's render-time migrations depend on it.
  `scripts/page_edit.py set-attr` keeps it: it re-renders only the block it edits, with that block's
  `builderVersion` unchanged, while blocks you `replace`/`insert-*` go in exactly as written (it warns when one
  has no `builderVersion`, and never adds one).
- `modulePreset` sits next to it; see [value-formats.md → presets](value-formats.md#presets-modulepreset-and-grouppreset).

## Post meta

`post_content` alone is not enough (`storage-and-serialization.md` §1.2):

| meta key | value | needed? |
|---|---|---|
| `_et_pb_use_builder` | `on` | **Yes.** Without it the modules still render and are styled, but inside the theme's normal page template: an `<h1 class="entry-title">` with the page title and a sidebar. With it: body classes `et_pb_pagebuilder_layout et_no_sidebar`, no title, no sidebar. `et_pb_is_pagebuilder_used()` reads only this key (`includes/builder/core.php:4216-4234`). |
| `_et_pb_use_divi_5` | `on` | Not for rendering. The Visual Builder writes it on save and the Divi 5 Migrator skips pages that have it. REST can't set it: Divi 5.13.1 never registers it (`register_meta`) for REST, so `publish.py` doesn't send it. To set it, use WP-CLI: `wp post meta update <id> _et_pb_use_divi_5 on --user=<admin>`. |
| `_et_pb_show_page_creation` | `off` | Optional; hides the builder's "create page" prompt. |

### Why REST needs `publish.py`

On Divi 5.13.1, `POST /wp/v2/pages` with `"meta": {"_et_pb_use_builder": "on"}` returns 201 but **silently does not
store the meta**. Divi registers the key for REST only when its Divi 4 shortcode framework loads, which in a REST
request happens lazily while rendering a Divi 4 shortcode, after the meta has been handled
(`BlockEditorIntegration.php:1060-1080`, `framework.php:49-52`). Divi's own save routes need an `X-ET-Nonce` that an
Application Password cannot obtain (`storage-and-serialization.md` §2.3).

The sequence that works, verified live (`storage-and-serialization.md`, "Addendum"):

1. Create the page with a Divi 4 stub as its content: `POST /wp/v2/pages {"title": …, "status": "draft",
   "content": "[et_pb_section][/et_pb_section]"}`.
2. Send one `POST /batch/v1` with two requests for that page. The first re-saves the title; rendering its
   response loads the shortcode framework, which registers the key. The second, in the same PHP process, sends the
   real block content and `"meta": {"_et_pb_use_builder": "on"}`. Expect 207 with two 200s.
3. Check the second response's `meta._et_pb_use_builder == "on"`: it is read from the database right after the
   write, while the key is registered. A later plain `GET ?context=edit` can't show the key for a page holding Divi 5
   blocks (nothing registers it in that request, so `meta` comes back without it); it must just not say otherwise.

Without the stub, the same batch stores nothing. The cost is one extra revision holding the stub.
**Use `publish.py`**, which runs this sequence for Divi 5 sites and checks the read-back (see
[../publishing.md](../publishing.md)). Other ways to set the meta: WP-CLI
`wp post meta update <id> _et_pb_use_builder on --user=<admin>` (always pass `--user`: without it the page's cached
CSS is not invalidated and stale CSS is served, §2.4), or a small mu-plugin that registers the key on `init`. Never
swap a live page's content for the stub.

## `content.raw` on WordPress 7.0 and later

- `GET /wp/v2/pages/<id>?context=edit` returns `content.raw` **re-serialized by WordPress** (Block Hooks,
  `class-wp-rest-posts-controller.php:2173-2180`, `blocks.php:1537-1552`), not the stored bytes
  (`storage-and-serialization.md` §2.2). The block tree is the same, but converter or Visual Builder output comes back
  in canonical form (self-closing leaves, WordPress escaping). Canonical input comes back byte for byte.
- So a REST read-modify-write normalizes the page. Use the fetched `content.raw` as your baseline as-is, and compare
  pages as block trees, not as bytes.
- The stored `post_content` itself is exactly what an Administrator sent, over REST or WP-CLI (§2.1). After a REST
  update Divi regenerates the page's CSS on the next view (§2.4).

## Literal brackets in text

Text content runs through `do_shortcode`, so a `[` followed by a letter can run a shortcode (§6.3). Write literal
brackets as `&#91;` and `&#93;`, which is what Divi's converter does (`unicode.html`: `&#91;VIP&#93;`).
`validate.py` warns `W5_SHORTCODE_BRACKETS` for `[` followed by a letter in HTML or text content. The entities are
output as-is and the browser shows `[20%]` (live check):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eSave \u0026#91;20%\u0026#93; on drain cleaning this week.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Divi 4 pages on a Divi 5 site

(`tokens-and-detection.md` §0, §6, §7)

- Tell them apart per page from `content.raw`: `[et_pb_` means Divi 4 shortcode, `<!-- wp:divi/` means Divi 5
  blocks. Both kinds coexist on upgraded sites.
- Upgrading the theme converts nothing. A shortcode page keeps rendering through Divi 5's bundled Divi 4 code
  (modules carry an extra `et_d4_element` class), with visible losses: the deferred CSS file was never generated,
  1/2 and 1/3 columns collapsed into one stack, blurb icons were missing.
- A shortcode page becomes blocks only when someone opens it in the Visual Builder and saves, or runs the Divi 5
  Migrator (which wraps the result in `divi/placeholder`, backs up the original to `_et_pb_divi_4_content` and sets
  `_et_pb_use_divi_5=on`).
- **Never write Divi 4 shortcode to a Divi 5 site, and don't patch a shortcode page there.** Rebuild it as Divi 5
  blocks (the old page is still a fine style source, read with the Divi 4 references), or ask the user to migrate
  it in Divi first. `validate.py` rejects a page mixing both formats (`E5_MIXED_FORMAT`).
- When editing a Divi 5 page, keep `divi/placeholder`, `divi/shortcode-module` and `divi/global-layout` blocks
  exactly as they are.

## What never to write

- **Raw `<`, `>`, `&`, `"` or `--` inside the JSON.** Canonical escaping only (`E5_NONCANONICAL`); raw `<`/`"`
  destroys the page for authors without `unfiltered_html`.
- **Text or HTML between block comments** (`E5_NOT_DIVI`). Content goes in `innerContent`.
- **Divi 4 shortcode**, whole pages or pieces: inside a text module it runs as a Divi 4 module
  (`W5_SHORTCODE_BRACKETS`).
- **Other WordPress blocks** (`<!-- wp:paragraph -->`, …) inside the layout (`E5_NOT_DIVI`), and
  **`divi/shortcode-module`**.
- **Ids that aren't in `tokens.json`**: `gcid-…`/`gvid-…` variables and preset ids (`W5_UNKNOWN_VARIABLE`,
  `W5_UNKNOWN_PRESET`). An unknown variable renders as nothing; an unknown `modulePreset` also drops the module's
  default preset styling (`tokens-and-detection.md` §3.5).
- **Divi 4 escapes** (`%22`, `%91`, `%93`) or Divi 4 value strings (`||`-separated icons, `|`-separated spacing);
  Divi 5 values are JSON ([value-formats.md](value-formats.md)).
- **Values Divi accepts but silently ignores** (live checks, `doc-experiments.md` §1, §7, §8): a length without a
  unit where CSS needs one (`"top": 40`; `E5_UNITLESS_LENGTH`), a gradient without `"enabled": "on"`
  (`E5_GRADIENT_DISABLED`) or with stop positions like `"0%"` (`E5_GRADIENT_STOP_POSITION`), text styles on the bare
  `….decoration.font` instead of `….decoration.font.font` (`W5_BARE_FONT`), and Divi 4 conversion-only attributes such
  as a row's `columns.column-1.*` or `padding1Phone` (`W5_LEGACY_ATTR`). See [value-formats.md](value-formats.md).
- **Attribute-row ids copied from another page.** Custom attribute rows (`module.decoration.attributes`) carry a
  UUIDv4 `id`; generate a new one per row.

## Parser-level validator codes

| code | level | meaning | fix |
|---|---|---|---|
| `E5_BAD_JSON` | error | a block's attributes are not valid JSON | rebuild the block with `divi5_blocks` |
| `E5_UNCLOSED` / `E5_STRAY_CLOSE` / `E5_MISNESTED` | error | an opener without its closer, a closer without its opener, or overlapping blocks | fix the comment pairs |
| `E5_NONCANONICAL` | error | raw `<`, `>`, `&`, `--` or `\"` in the JSON | re-serialize canonically |
| `E5_NOT_DIVI` | error | text between blocks, or a non-`divi/` block | move the content into a module's `innerContent` |
| `E5_MIXED_FORMAT` | error | Divi 4 shortcode and Divi 5 blocks in one page | write blocks only |
| `W5_NO_PLACEHOLDER` | warning | the page is not wrapped in `divi/placeholder` (not reported with `--fragment`) | wrap it |
| `W5_BUILDER_VERSION` | warning | a block has no `builderVersion`, or (with `--tokens`) not the site's | add the site's version to blocks you create |
| `W5_SHORTCODE_BRACKETS` | warning | `[` followed by a letter in HTML or text content | write `&#91;` / `&#93;` |

Structure codes are in [structure.md](structure.md#structural-validator-codes), value codes in
[value-formats.md](value-formats.md#value-validator-codes).
