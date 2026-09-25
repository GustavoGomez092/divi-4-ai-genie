# Gallery

**Use for:** a grid of completed-job photos ("before/after" repairs, finished installs) that builds
credibility through visible work, with a lightbox on click. · **SEO:** one `h2` introduces the
gallery; **`et_pb_gallery` has no `alt`/`image_alt` attribute of its own** (confirmed against the
module's schema): each thumbnail's `<img alt="...">` comes from the Media Library attachment's own
"Alt Text" field, not from anything set on this module — fill that field in on every upload (a real
description of the job/photo, not the filename). `gallery_ids` must be **real Media Library
attachment IDs from the target site** — they are never a token, and a gallery pointed at another
site's IDs will show that site's (or no) images.

## Structure
```text
section (Our Work, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row
   └─ column 4_4: gallery
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,custom_padding=90px].attrs.background_color` (the "Why Choose Us" bundle, reused for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[2][0]` |
| heading (`h2`) `title_font`, `title_text_color`, `title_font_size` | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` |
| gallery `title_font`, `title_text_color` (per-image caption title, if `show_title_and_caption="on"`) | no `et_pb_gallery` bundle exists in tokens — `typography.heading_font` + `"\|700\|\|\|\|\|\|\|"` + `colors.customizer.heading` | same |
| gallery `zoom_icon_color`, `hover_overlay_color` | no bundle exists in tokens for this module — both read straight off `colors.customizer.accent` (icon) and `colors.palette[0].hex` (overlay); the site's tokens don't record alpha/translucent variants of a palette color, so the overlay is the palette color at full opacity rather than a guessed `rgba()` tint (`validate.py`'s `W_OFF_PALETTE_COLOR` check only matches colors present verbatim in `tokens.json`, and a translucent color never is one) | `colors.customizer.accent` / `colors.palette[0].hex` |
| `gallery_ids` | the target site's own Media Library — a comma-separated list of that site's real attachment IDs, obtained via `wp media list`/the Media Library UI, never a token and never invented | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`,
`title_level="h2"`, `title_font`, `title_text_color`, `title_font_size`;
[`et_pb_gallery`](../../reference/modules/et_pb_gallery.md) `gallery_ids`.

Optional: `fullwidth` (`"off"` default — a boxed grid of individually-cropped thumbnails; `"on"` —
an edge-to-edge, uncropped slideshow-style layout); `posts_number` (how many images show per page,
default `4`); `orientation` (`"landscape"`/`"portrait"` thumbnail crop, `fullwidth="off"` only);
`show_pagination`/`show_title_and_caption` (both default `on`); `zoom_icon_color`,
`hover_overlay_color` for the on-hover lightbox affordance.

## Responsive rules

`title_font_size` on the section's `h2` needs `_tablet`/`_phone` (40px → 32px → 28px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs its usual
`_tablet`/`_phone` pair. `et_pb_gallery` itself needs no responsive attributes: Divi reflows the
thumbnail grid to fewer columns automatically as the viewport narrows, down to one column on phone.

## Variations

- **Fullwidth variant:** `fullwidth="on"` for an edge-to-edge slideshow-style gallery instead of a
  boxed, cropped grid — best when the photos themselves (not a uniform grid) should be the visual
  focus.
- **Portrait variant:** `orientation="portrait"` (boxed layout only) for photo sets that are mostly
  vertical (e.g. tall before/after shots of a repaired wall section).
- **Fewer-per-page variant:** lower `posts_number` (e.g. `"6"`) and rely on `show_pagination="on"`
  for a large photo set that shouldn't all load on the initial page view.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Our Work" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Our Work" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][et_pb_gallery gallery_ids="301,302,303,304,305,306" fullwidth="off" orientation="landscape" posts_number="6" show_pagination="on" show_title_and_caption="on" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" zoom_icon_color="#f97316" hover_overlay_color="#0b2a3c"][/et_pb_gallery][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `python3 scripts/validate.py section.txt --tokens tokens.json --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — fast visual check; the gallery images themselves only show up once real attachments exist — the preview's coverage summary reports gallery attachments as needing the live site's data (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] exactly one `h2` — no `h1` on this section
- [ ] every real `gallery_ids` entry is an attachment that actually exists on the target site, and every uploaded photo has its Media Library "Alt Text" filled in
