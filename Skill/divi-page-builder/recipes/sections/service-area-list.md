# Service area list

**Use for:** a plain-text list of the cities/neighborhoods a local business serves, split across
2-3 columns near the footer of a home or service page — the classic local-SEO section. · **SEO:**
one `h2` introduces the list (e.g. "Areas We Serve"); each city is a plain `<li>`, and any city that
already has its own dedicated location page must link to it (`<a href="...">City Name</a>`) — this
is internal linking that helps that location page rank for "[service] in [city]" searches. Never
link a city that has no page yet; list it as plain text until one exists.

## Structure
```text
section (Service Areas, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row column_structure="1_3,1_3,1_3"
   ├─ column 1_3: text (<ul> of cities)
   ├─ column 1_3: text (<ul> of cities)
   └─ column 1_3: text (<ul> of cities)
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,custom_padding=80px].attrs.background_color` (the "About" bundle, reused for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[3][0]` |
| heading (`h2`) `title_font`, `title_text_color`, `title_font_size` | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` |
| list `text_font`, `text_text_color`, `text_font_size` | no `column_type=1_3` light-tone text bundle exists — build from `typography.body_font` + `colors.customizer.body_text` + `colors.customizer.body_size` | same |
| list `link_text_color` | `colors.customizer.link` (`#f97316`) — set explicitly rather than relying on the active theme's own default anchor color, which won't match this brand on a site whose theme CSS hasn't been customized to it (confirmed by the screenshot check: the local test site's own default link color rendered blue until this attribute was set) | `colors.customizer.accent` |
| city names, city page URLs | the client's own service-area list and site map — never a token | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); the heading `et_pb_row` and the list
`et_pb_row` `column_structure="1_3,1_3,1_3"`;
[`et_pb_column`](../../reference/modules/et_pb_column.md) `type="4_4"` / `type="1_3"`;
[`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`, `title_level="h2"`,
`title_font`, `title_text_color`, `title_font_size`; one
[`et_pb_text`](../../reference/modules/et_pb_text.md) per column with `content` (a `<ul>` of
`<li>`s, some linked), `text_font`, `text_text_color`, `text_font_size`, `link_text_color`.

Optional: `admin_label` on the section; `ul_type`/`ul_position` if the site's default bullet style
doesn't match the surrounding page.

## Responsive rules

`title_font_size` on the `h2` needs `_tablet`/`_phone` (40px → 32px → 28px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs its usual
`_tablet`/`_phone` pair. The list row's `column_structure="1_3,1_3,1_3"` needs no phone-specific
value: Divi stacks the three city lists to full width, one per line, on phone, which is the
intended reading order (no reordering concern here, since all three columns hold the same kind of
content).

## Variations

- **Two-column variant:** `column_structure="1_2,1_2"` for a shorter service area (fewer than
  ~15 cities) — nothing else changes.
- **Grouped-by-county variant:** give each column its own small heading (`et_pb_heading`,
  `title_level="h3"`, e.g. "Miami-Dade" / "Broward") above its `<ul>`, for a multi-county service
  area.
- **Map-paired variant:** add an `et_pb_map` or `et_pb_image` (a static service-area map graphic) in
  a fourth column or above the list, for a business that wants a visual alongside the text list.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Service Areas" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="80px||80px||true|false" custom_padding_tablet="55px||55px||true|false" custom_padding_phone="40px||40px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Areas We Serve" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][/et_pb_column][/et_pb_row][et_pb_row column_structure="1_3,1_3,1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#475569" text_font_size="16px" link_text_color="#f97316"]<ul><li><a href="https://miamirapidplumbing.example/service-areas/miami/">Miami</a></li><li><a href="https://miamirapidplumbing.example/service-areas/miami-beach/">Miami Beach</a></li><li><a href="https://miamirapidplumbing.example/service-areas/coral-gables/">Coral Gables</a></li><li>Brickell</li></ul>[/et_pb_text][/et_pb_column][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#475569" text_font_size="16px" link_text_color="#f97316"]<ul><li><a href="https://miamirapidplumbing.example/service-areas/hialeah/">Hialeah</a></li><li>Kendall</li><li>Homestead</li><li>Cutler Bay</li></ul>[/et_pb_text][/et_pb_column][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#475569" text_font_size="16px" link_text_color="#f97316"]<ul><li><a href="https://miamirapidplumbing.example/service-areas/doral/">Doral</a></li><li>Aventura</li><li>Pinecrest</li><li>Palmetto Bay</li></ul>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `python3 scripts/validate.py section.txt --tokens tokens.json --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — show the user `preview.html` (or `preview.py serve`) and **stop until they approve it**; fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] Only after the user approves the local preview: `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] exactly one `h2` — no `h1` on this section
- [ ] every city with an existing location page is linked; no city is linked to a page that doesn't exist
