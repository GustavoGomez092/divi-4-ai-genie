# Tabs

**Use for:** grouping related content — service categories ("Residential" / "Commercial" /
"Emergency"), plan tiers, or FAQ categories — behind clickable tabs so the page doesn't scroll
through all of it at once. · **SEO:** every `et_pb_tab`'s content renders in the page HTML at load
time (Divi just toggles visibility with CSS/JS), so search engines index all of it — write each
tab's content as if it will be read on its own, and give the section an `h2` above the tabs module
itself (the tabs module has no heading of its own).

## Structure
```text
section (Tabs, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row (tabs)
   └─ column 4_4: tabs
      ├─ tab "Residential"
      ├─ tab "Commercial"
      └─ tab "Emergency"
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,custom_padding=90px].attrs.background_color` (reusing the "Why Choose Us" bundle for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[2][0]` |
| heading (`h2`) `title_font`, `title_text_color`, `title_font_size` | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` |
| tab title `tab_font` | `colors.customizer.body_font` | `typography.body_font` (`Lato||||||||`) |
| tab title `tab_text_color` (inactive) | no `et_pb_tabs` bundle exists in tokens — `colors.customizer.heading` | same |
| `active_tab_background_color` | no bundle — use `colors.customizer.accent` (`#f97316`) | same |
| `active_tab_text_color` | no bundle — use a color that contrasts with the active background; `colors.palette` has `#ffffff` for exactly this reason | `colors.palette[1].hex` |
| `inactive_tab_background_color` | no bundle — use `colors.customizer.background`-equivalent; the site has no dedicated token for it, so use `#ffffff` (the section's own background, palette-verified) | `colors.palette[1].hex` |
| tab body `body_font`, `body_text_color` | no bundle — build from `typography.body_font` + `colors.customizer.body_text` | same |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_heading`](../../reference/modules/et_pb_heading.md)
`title`, `title_level="h2"`, `title_font`, `title_text_color`, `title_font_size`;
[`et_pb_tabs`](../../reference/modules/et_pb_tabs.md) `active_tab_background_color`,
`active_tab_text_color`, `inactive_tab_background_color`, `tab_font`, `tab_text_color`; one
[`et_pb_tab`](../../reference/modules/et_pb_tab.md) per category, each with `title`, `content`,
`body_font`, `body_text_color`.

Optional: `admin_label` on the section and on each tab; `body_font_size` if the default body size
needs to match the rest of the page more closely than Divi's own default.

## Responsive rules

`title_font_size` on the `h2` needs `_tablet`/`_phone` (40px → 32px → 28px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs its usual
`_tablet`/`_phone` pair. The tabs module itself needs no responsive attributes: Divi already
switches the tab control row to a stacked accordion-like list on phone automatically, and the
active/inactive colors apply the same way at every width.

## Variations

- **Two-tab variant:** drop one `et_pb_tab` — the module accepts any number of tabs, no structural
  change needed.
- **FAQ-by-category variant:** put a short `et_pb_text` (or nested `et_pb_accordion`) inside each
  tab instead of a single paragraph, so each category can hold several question/answer pairs.
- **Dark-tone variant:** swap the section to the dark navy bundle and re-pick
  `inactive_tab_background_color` (e.g. a lighter navy tint) and `tab_text_color` (light gray) so
  inactive tabs still read against the dark background.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Tabs" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Plumbing Services By Property Type" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][et_pb_tabs _builder_version="4.27.9" _module_preset="default" active_tab_background_color="#f97316" active_tab_text_color="#ffffff" inactive_tab_background_color="#ffffff" tab_font="Lato||||||||" tab_text_color="#0b2a3c"][et_pb_tab title="Residential" _builder_version="4.27.9" _module_preset="default" body_font="Lato||||||||" body_text_color="#475569"]<p>Repairs, repipes and fixture installs for single-family homes and condos across Miami-Dade.</p>[/et_pb_tab][et_pb_tab title="Commercial" _builder_version="4.27.9" _module_preset="default" body_font="Lato||||||||" body_text_color="#475569"]<p>Scheduled maintenance and emergency response for restaurants, offices and multi-family buildings.</p>[/et_pb_tab][et_pb_tab title="Emergency" _builder_version="4.27.9" _module_preset="default" body_font="Lato||||||||" body_text_color="#475569"]<p>24/7 dispatch for burst pipes, active leaks and sewage backups — on site within 60 minutes.</p>[/et_pb_tab][/et_pb_tabs][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `python3 scripts/validate.py section.txt --tokens tokens.json --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] exactly one `h2` above the tabs — no `h1` on this section
- [ ] the active tab's background/text colors are legible against the inactive tabs around it
