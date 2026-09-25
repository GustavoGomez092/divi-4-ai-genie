# Trust bar

**Use for:** a compact strip of partner/certification logos (BBB, trade associations, review
platforms) between two content sections, signaling credibility without a heading of its own. ·
**SEO:** every `et_pb_image` needs `alt` text naming the organization the logo represents (e.g.
"Better Business Bureau A+ Rating"), never the filename or a generic "logo"; this section carries
no heading, so it never introduces an `h1`/`h2`.

## Structure
```text
section (Trust bar, light tone, compact padding)
└─ row column_structure="1_5,1_5,1_5,1_5,1_5"
   ├─ column 1_5: image (logo 1, grayscale → color on hover)
   ├─ column 1_5: image (logo 2, grayscale → color on hover)
   ├─ column 1_5: image (logo 3, grayscale → color on hover)
   ├─ column 1_5: image (logo 4, grayscale → color on hover)
   └─ column 1_5: image (logo 5, grayscale → color on hover)
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#f1f5f9].attrs.background_color` (the light-gray band also used by "By The Numbers") | `colors.palette[5].hex` (the palette entry whose `roles` includes `background_color` and isn't the primary navy/white) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` — `"70px\|\|70px\|\|true\|false"`, the site's most-used value (`spacing.section_padding[0]` has count `2`), which is why it reads as "compact" next to the 90/96px hero and full-content paddings | `spacing.section_padding[0][0]` |
| row `width`, `max_width` | no bundle matches a 5-column row; read `spacing.row.width[0][0]` / `spacing.row.max_width[0][0]` directly | same (there is no thinner fallback below this) |
| image `filter_saturate` (default) / `filter_saturate__hover` / `filter_saturate__hover_enabled` | no bundle in tokens covers a grayscale-hover filter — **fixed design choice**: `0%` at rest, `100%` on hover, `on\|hover` to enable the hover state. This is a standard grayscale-to-color trust-bar convention, not a brand color, so there is nothing to look up in `tokens.json` | same (always fixed) |
| image `max_width`, `module_alignment` | **fixed design choice**: `140px` / `center`, so five differently-shaped partner logos share a common visual size | same |
| image `src`, `alt` | the site's own Media Library and the represented organization's real name — never a token | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_row`](../../reference/modules/et_pb_row.md)
`column_structure="1_5,1_5,1_5,1_5,1_5"`, `width`, `max_width`;
[`et_pb_column`](../../reference/modules/et_pb_column.md) `type="1_5"` (one per logo);
[`et_pb_image`](../../reference/modules/et_pb_image.md) `src`, `alt`, `filter_saturate`,
`filter_saturate__hover`, `filter_saturate__hover_enabled`.

Optional: `admin_label` on the section; `max_width`/`module_alignment` on each image for uniform
logo sizing; `url`/`url_new_window` on an image to link a logo to the awarding organization's site.

## Responsive rules

`custom_padding` needs `_tablet`/`_phone` (70px → 50px → 40px) plus
`custom_padding_last_edited="on|phone"`, matching the same compact-band rhythm as the rest of the
page. `max_width="140px"` on each logo needs no responsive variant — being a maximum, it already
shrinks to fit a full-width phone column once the row stacks to one logo per line. The row's
`column_structure="1_5,1_5,1_5,1_5,1_5"` needs no phone-specific value either: Divi always stacks
every column to full width on phone regardless of the desktop split.

## Variations

- **Four-logo variant:** `column_structure="1_4,1_4,1_4,1_4"` with four `1_4` columns instead of
  five `1_5` columns — nothing else changes.
- **Linked variant:** add `url` (the organization's own site or review page) and
  `url_new_window="on"` to each `et_pb_image`.
- **Dark-tone variant:** swap the section to the dark navy bundle
  (`module_styles.et_pb_section[background=#0b2a3c]`) and use light/white-on-transparent logo
  files, since the grayscale-to-color filter reads the same way regardless of section tone.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Trust Bar" _builder_version="4.27.9" _module_preset="default" background_color="#f1f5f9" custom_padding="70px||70px||true|false" custom_padding_tablet="50px||50px||true|false" custom_padding_phone="40px||40px||true|false" custom_padding_last_edited="on|phone"][et_pb_row column_structure="1_5,1_5,1_5,1_5,1_5" _builder_version="4.27.9" _module_preset="default" width="90%" max_width="1200px"][et_pb_column type="1_5" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-bbb.png" alt="Better Business Bureau A+ Rating" _builder_version="4.27.9" _module_preset="default" max_width="140px" module_alignment="center" filter_saturate="0%" filter_saturate__hover="100%" filter_saturate__hover_enabled="on|hover"][/et_pb_image][/et_pb_column][et_pb_column type="1_5" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-angi.png" alt="Angi Super Service Award" _builder_version="4.27.9" _module_preset="default" max_width="140px" module_alignment="center" filter_saturate="0%" filter_saturate__hover="100%" filter_saturate__hover_enabled="on|hover"][/et_pb_image][/et_pb_column][et_pb_column type="1_5" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-google-guaranteed.png" alt="Google Guaranteed" _builder_version="4.27.9" _module_preset="default" max_width="140px" module_alignment="center" filter_saturate="0%" filter_saturate__hover="100%" filter_saturate__hover_enabled="on|hover"][/et_pb_image][/et_pb_column][et_pb_column type="1_5" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-nexstar.png" alt="Nexstar Network Member" _builder_version="4.27.9" _module_preset="default" max_width="140px" module_alignment="center" filter_saturate="0%" filter_saturate__hover="100%" filter_saturate__hover_enabled="on|hover"][/et_pb_image][/et_pb_column][et_pb_column type="1_5" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-florida-licensed.png" alt="State of Florida Licensed Contractor" _builder_version="4.27.9" _module_preset="default" max_width="140px" module_alignment="center" filter_saturate="0%" filter_saturate__hover="100%" filter_saturate__hover_enabled="on|hover"][/et_pb_image][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `section.txt --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] no heading module on this page (a trust bar carries no `h1`/`h2`/`h3`)
- [ ] every image has alt text naming the organization, and a Media Library URL
