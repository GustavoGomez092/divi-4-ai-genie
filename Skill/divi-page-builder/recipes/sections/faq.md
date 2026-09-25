# FAQ

**Use for:** a frequently-asked-questions section that also earns a Google rich-result FAQ
snippet, by pairing a visible `et_pb_accordion` with a `FAQPage` JSON-LD block search engines can
read. · **SEO:** one `h2` introduces the accordion (each `et_pb_accordion_item`'s own `title`
renders at the accordion's `toggle_level` — set it to one level below the section heading, `h3`
under an `h2`, because the module default `h5` would skip `h3`/`h4`); the
`FAQPage` JSON-LD's questions must match the accordion's questions **word for word** — a JSON-LD
block that advertises different or extra questions than what's visibly on the page violates
Google's structured-data guidelines and can get the rich result rejected. **Data note — never
invent FAQ content.** The three questions/answers below are illustrative placeholders for
`sample-tokens.json`'s fictional brand only. On a real client site, every question and answer must
come from the client's own brief, copied word for word into both the accordion and the JSON-LD —
never rewritten, paraphrased, or invented to pad out the list. **`wptexturize()` caveat, found by
pushing a real test page and diffing the rendered HTML against the JSON-LD.** WordPress's
`the_content` filters (which the accordion's answer text passes through, since it's an ordinary
tiny_mce module) run `wptexturize()`, which silently rewrites some plain-ASCII punctuation for
display — a double hyphen `--` becomes an em dash entity (`&#8212;`). The `et_pb_code` module's
content does **not** pass through that filter (Code.php's own comment says so: "no wptexturize"),
so the same literal `--` you typed stays a literal `--` inside the `<script>` tag. Typing `--`
identically in both places therefore still produces two *visually different* rendered strings —
not a word-for-word match a strict JSON-LD/on-page comparison would accept.
Avoid `--`, ellipses (`...`), straight quotes next to words, and other characters `wptexturize()`
touches inside FAQ answers; this recipe's own answers were adjusted for exactly this reason (see
the Checklist for how it was caught).

**Escaping — this goes in the code module's *content*, not an attribute.** `et_pb_code`'s schema
lists a field called `raw_content`, but on disk it is the shortcode's **inner content** (the text
between `[et_pb_code ...]` and `[/et_pb_code]`), exactly like a `tiny_mce` module's `content` —
confirmed by reading `divi_render/modules/basic.py`'s `Code` handler, which reads
`self.node.content` (the tag's inner text), not `self.node.attrs["raw_content"]`. That distinction
matters because `reference/page-format.md`'s escaping table has **two different rules** for `"`
and `[`/`]`, and only one applies here:

- **Inside an *attribute* value**, a raw `"` must be written `%22` and a raw `[`/`]` must be written
  `%91`/`%93` (see page-format.md's Escaping table) — otherwise WordPress's attribute parser or
  shortcode tag-matcher can misread the value.
- **Inside a text-bearing module's *content*** (the last row of that same table), none of that
  applies: content is "returned to the front end byte-for-byte" and must be written as **raw
  HTML** — so the JSON-LD's `"` and its `mainEntity` array's `[`/`]` are written **literally,
  unescaped**, exactly as valid JSON requires. Writing `%22`/`%91`/`%93` here would be wrong: it
  would leave those literal percent-sequences sitting in the rendered `<script>` tag, breaking the
  JSON (and, per the read-side note in page-format.md, `%92`/`%5c` — but not `%22`/`%91`/`%93` — get
  decoded back on the way out for *any* attribute; content isn't run through that decoder at all,
  so this only matters if it were mistakenly put in an attribute).

Both `python3 scripts/validate.py` (which only scans *attribute* values for `E_RAW_QUOTE`/
`E_RAW_BRACKET`, never module content) and the Divi judge (`tests/test_divi_judge.py`, which parses
the page with this skill's own parser and compares it against what the real Divi site's PHP parser
produces) confirm this is correct — see the Checklist below.

## Structure
```text
section (FAQ, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row
   └─ column 4_4: accordion
      ├─ accordion_item (Q1, open="on")
      ├─ accordion_item (Q2)
      ├─ accordion_item (Q3)
      └─ code (FAQPage JSON-LD, same 3 questions)
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,custom_padding=90px].attrs.background_color` (the "Why Choose Us" bundle, reused for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[2][0]` |
| heading (`h2`) `title_font`, `title_text_color`, `title_font_size` | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` |
| accordion item `open_toggle_text_color`, `icon_color` | no `et_pb_accordion` bundle exists in tokens — `colors.customizer.accent` (`#f97316`), so the open question's title and chevron read as the brand's accent color | same |
| accordion item title (`toggle_font`, `closed_toggle_font`) | `colors.customizer.heading_font` | `typography.heading_font` (`Montserrat|700|||||||`) |
| accordion item `body_font`, `body_text_color` (the answer) | no bundle — `typography.body_font` + `colors.customizer.body_text` | same |
| accordion `toggle_level` (question titles) | this pattern's own choice, not a token — one level below the section heading (`h3` under this section's `h2`); never the module default `h5`, which skips levels | `h3` |
| `et_pb_code`'s JSON-LD content | not a token at all — built programmatically from the *same* question/answer strings as the accordion items, never typed a second time by hand (to guarantee word-for-word match) | — |
| the questions and answers themselves | the client's own brief — never a token, never invented (see the note above) | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`,
`title_level="h2"`, `title_font`, `title_text_color`, `title_font_size`;
[`et_pb_accordion`](../../reference/modules/et_pb_accordion.md) `toggle_level="h3"`; one
[`et_pb_accordion_item`](../../reference/modules/et_pb_accordion_item.md) per question with
`title`, `content`, `open="on"` on exactly the first item, `toggle_font`, `closed_toggle_font`,
`body_font`, `body_text_color`; one
[`et_pb_code`](../../reference/modules/et_pb_code.md) module, placed as a sibling of the accordion
inside the same column, whose content is a `<script type="application/ld+json">` tag containing the
`FAQPage` JSON-LD.

Optional: `open_toggle_text_color`/`icon_color` on the accordion items for brand-matched styling;
`toggle_icon` to swap the default chevron for a different glyph (verify visually before using it).

## Responsive rules

`title_font_size` on the section's `h2` needs `_tablet`/`_phone` (40px → 32px → 28px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs its usual
`_tablet`/`_phone` pair. `et_pb_accordion` and `et_pb_code` need no responsive attributes of their
own: an accordion is already a single stacked list at every width, and the JSON-LD `<script>` tag
is invisible on the page regardless of viewport.

## Variations

- **More/fewer questions:** add or remove `et_pb_accordion_item`s freely — just keep the JSON-LD's
  `mainEntity` array in exact sync (same count, same order isn't required by Google, but the same
  wording is).
- **Category-grouped variant:** use the `et_pb_tabs` pattern (see
  [tabs.md](tabs.md)) with one `et_pb_accordion` per tab, for a FAQ long enough to split into
  categories (e.g. "Pricing" / "Scheduling" / "Warranty") — each tab's accordion still needs its
  own matching JSON-LD, or one combined JSON-LD block covering every question across all tabs.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="FAQ" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Frequently Asked Questions" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][et_pb_accordion toggle_level="h3" _builder_version="4.27.9" _module_preset="default"][et_pb_accordion_item title="Do you offer 24/7 emergency plumbing service?" open="on" _builder_version="4.27.9" _module_preset="default" open_toggle_text_color="#f97316" icon_color="#f97316" toggle_font="Montserrat|700|||||||" closed_toggle_font="Montserrat|700|||||||" body_font="Lato||||||||" body_text_color="#475569"]<p>Yes. We answer calls day and night, 365 days a year, with a licensed plumber typically on site within 60 minutes.</p>[/et_pb_accordion_item][et_pb_accordion_item title="Do you provide free estimates?" _builder_version="4.27.9" _module_preset="default" open_toggle_text_color="#f97316" icon_color="#f97316" toggle_font="Montserrat|700|||||||" closed_toggle_font="Montserrat|700|||||||" body_font="Lato||||||||" body_text_color="#475569"]<p>Yes. We give you an upfront, flat-rate price before any work begins, with no hidden fees.</p>[/et_pb_accordion_item][et_pb_accordion_item title="Are your plumbers licensed and insured?" _builder_version="4.27.9" _module_preset="default" open_toggle_text_color="#f97316" icon_color="#f97316" toggle_font="Montserrat|700|||||||" closed_toggle_font="Montserrat|700|||||||" body_font="Lato||||||||" body_text_color="#475569"]<p>Yes. Every technician is a licensed, insured Florida plumber.</p>[/et_pb_accordion_item][/et_pb_accordion][et_pb_code _builder_version="4.27.9" _module_preset="default"]<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Do you offer 24/7 emergency plumbing service?","acceptedAnswer":{"@type":"Answer","text":"Yes. We answer calls day and night, 365 days a year, with a licensed plumber typically on site within 60 minutes."}},{"@type":"Question","name":"Do you provide free estimates?","acceptedAnswer":{"@type":"Answer","text":"Yes. We give you an upfront, flat-rate price before any work begins, with no hidden fees."}},{"@type":"Question","name":"Are your plumbers licensed and insured?","acceptedAnswer":{"@type":"Answer","text":"Yes. Every technician is a licensed, insured Florida plumber."}}]}</script>[/et_pb_code][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 Skill/divi-page-builder/scripts/validate.py <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — 0 errors
- [ ] `python3 Skill/divi-page-builder/scripts/preview.py render <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — fast visual check
- [ ] added as `tests/fixtures/valid/faq-jsonld.txt` and to `DiviJudgeTest.FILES` in `tests/test_divi_judge.py`; `python3 -m unittest discover -s tests -p 'test_divi_judge.py' -v` passes against the local Divi site
- [ ] `research/tools/push_local.sh <file> "FAQ"` — push to divi-test.local, note the printed id/url
- [ ] `curl` the pushed page and parse the `<script type="application/ld+json">` block with Python's `json` module — must load without error and its 3 questions must match the accordion's 3 titles word for word
- [ ] `node research/python-renderer-spike/shoot.mjs <outdir> faq <url> --width 1440,390` — screenshot at desktop (1440) and phone (390)
- [ ] `research/tools/wp-local.sh post delete <id> --force` — delete the test page once the screenshots look right
- [ ] exactly one `h2` — no `h1` on this section; every accordion item title is below `h2` (default `h5`)
- [ ] only the first accordion item has `open="on"`; the JSON-LD's questions/answers match the accordion's, word for word, with none invented
