# Pricing

**Use for:** a side-by-side comparison of 2-4 service tiers/plans, with one tier visually raised as
the recommended option. · **SEO:** one `h2` introduces the table; each table's own `title` renders
at `header_level` (default `h2` on the module, overridden to `h3` here so it nests under the
section's real `h2` — see Required fields). **Data note — never invent prices.** The plan names,
prices, frequencies and feature lists below are illustrative placeholders for `sample-tokens.json`'s
fictional brand only. On a real client site, every currency symbol, price, billing frequency and
feature must come from the client's own price sheet/brief — never estimated, rounded, or invented.
**Content format — verified against the real Divi module and its PHP source, not just the schema.**
A pricing table's `content` is **plain text, one feature per line, separated by a real newline** —
Divi's own `et_pb_extract_items()` (`includes/builder/functions.php`) explodes the content on `\n`,
trims each line, and wraps it in `[et_pb_pricing_item]...[/et_pb_pricing_item]` before running
`do_shortcode()` once over the whole result; that sub-shortcode is what renders the final
`<li><span>...</span></li>` (the `<li>` `bullet_color`'s own selector, `ul.et_pb_pricing li
span:before`, actually targets) inside the `<ul class="et_pb_pricing">` Divi generates for you.
**Do not** wrap the lines in your own `<ul>`/`<li>` HTML or write the `[et_pb_pricing_item]`
sub-shortcode yourself — either one gets wrapped *again* by `et_pb_extract_items()`, since it
operates on the raw line text without checking whether it already looks like a shortcode or HTML,
producing doubly-nested, broken `<li>` markup (confirmed on Divi 4.27.9 by pushing test pages and
reading the rendered HTML back with `curl`; see the Checklist). **To mark a feature excluded**,
prefix that one line with a leading `-` (a plain ASCII hyphen, trimmed off before rendering); Divi
renders it `<li class="et_pb_not_available">...</li>` instead of a plain `<li>`.
`et_pb_extract_items()` also recognizes a leading `+` as an explicit "included" marker (functionally
identical to no prefix at all) — neither symbol needs to be escaped, since it's plain content, not
an attribute.

## Structure
```text
section (Pricing, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row
   └─ column 4_4: pricing_tables
      ├─ pricing_table (Basic)
      ├─ pricing_table (Standard, featured="on")
      └─ pricing_table (Premium)
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,custom_padding=90px].attrs.background_color` (the "Why Choose Us" bundle, reused for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[2][0]` |
| heading (`h2`) `title_font`, `title_text_color`, `title_font_size` | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` |
| `et_pb_pricing_tables` `bullet_color` | no bundle exists in tokens for this module — `colors.customizer.accent` (`#f97316`) | same |
| each table's `header_level` | this pattern's own choice, not a token — `"h3"`, so per-tier titles nest under the section's `h2` | `"h3"` |
| each table's `header_font`, `header_text_color` | no bundle — `typography.heading_font` + `"\|700\|\|\|\|\|\|\|"` + `colors.customizer.heading` | same |
| each table's `body_font`, `body_text_color` (feature list) | no bundle — `typography.body_font` + `colors.customizer.body_text` | same |
| `et_pb_pricing_tables`' `featured_table_header_background_color` (styles whichever child has `featured="on"` — this attribute lives on the parent `et_pb_pricing_tables`, not the individual `et_pb_pricing_table`, since only one table is ever the featured one at a time) | no bundle — `colors.customizer.accent` (`#f97316`), so the raised tier's header reads as the brand's call-to-action color | same |
| `et_pb_pricing_tables`' `featured_table_header_text_color` | no bundle — `colors.palette[1].hex` (`#ffffff`), for contrast against the orange header | same |
| every table's button (`custom_button`, `button_bg_color`, `button_text_color`, `button_bg_color__hover`, `button_bg_color__hover_enabled`, `button_border_radius`) | `module_styles.et_pb_button[section_tone=dark,column_type=4_4].attrs` (the "Free Quote CTA" bundle — reused here purely for its brand button colors, not because this section is dark) + `_module_preset` from `presets.et_pb_button[0].uuid` | `colors.customizer.accent` for `button_bg_color`, `colors.palette[1].hex` for `button_text_color` |
| every table's button `button_font` | `colors.customizer.body_font` | `typography.body_font` (`Lato||||||||`) |
| a non-featured table's `excluded_text_color` (only needed once a feature line has a leading `-`) | no bundle — `colors.palette[6].hex` (`#cbd5e1`, the site's own light neutral), so an excluded feature reads visibly muted instead of the same color as included ones — needed because this table's own `body_text_color` cascades onto every `<li>` including excluded ones, at higher specificity than Divi's own default `.et_pb_not_available{color:#ccc}` rule; confirmed by pushing a first draft *without* `excluded_text_color` and finding the excluded item rendered in the same dark color as every other feature, indistinguishable at a glance | `colors.palette[6].hex` |
| `featured_table_price_color`/`featured_table_text_color`/`featured_table_background_color` | deliberately **left unset** — only the header band is recolored; the featured tier's price/body area keeps the same white background and dark text as every other tier, since coloring the text without also coloring its background (which needs three more attributes: `featured_table_price_background_color`, and the price/body areas don't share one background attribute) risks a white-on-white contrast bug — confirmed by pushing a first draft with `featured_table_price_color`/`featured_table_text_color` set to white without a matching background: the price and feature text became invisible against the still-white price/body area | — |
| plan names, `currency`, `sum`, `per`, feature list, `featured` (which tier) | the client's own price sheet — **never** a token, and never invented (see the note above) | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`,
`title_level="h2"`, `title_font`, `title_text_color`, `title_font_size`;
[`et_pb_pricing_tables`](../../reference/modules/et_pb_pricing_tables.md) `bullet_color`,
`featured_table_header_background_color`, `featured_table_header_text_color` (these two style
whichever child table has `featured="on"` — they belong on the parent module, not the child); one
[`et_pb_pricing_table`](../../reference/modules/et_pb_pricing_table.md) per tier with `title`,
`header_level="h3"`, `subtitle`, `currency`, `sum`, `per`, `content` (plain text, one feature per
line, separated by a real newline, with a leading `-` on any excluded feature — see the
content-format note above), `button_text`, `button_url`, `header_font`, `header_text_color`,
`body_font`, `body_text_color`, `button_font`, plus the shared button attributes above.

Optional: `featured="on"` on exactly one `et_pb_pricing_table` child (the recommended plan — Divi
styles it larger and raised automatically once any table on the page is featured); a leading `+` on
a feature line to mark it explicitly included (identical in effect to no prefix); `excluded_font`/
`excluded_text_color` (a non-featured table's excluded-item styling) or, on a featured table,
`featured_table_excluded_text_color`; on `et_pb_pricing_tables`,
`featured_table_background_color`/`featured_table_price_color`/`featured_table_text_color`/
`featured_table_bullet_color`/`featured_table_subheader_text_color`/
`featured_table_currency_frequency_text_color` for more complete control over the featured tier's
look — if you set any of the price/body-text ones, also set a matching background
(`featured_table_price_background_color`) so the text stays legible, per the note above;
`show_bullet="off"` on `et_pb_pricing_tables` to hide the bullet dots entirely, for a plainer
feature list.

## Responsive rules

`title_font_size` on the section's `h2` needs `_tablet`/`_phone` (40px → 32px → 28px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs its usual
`_tablet`/`_phone` pair. `et_pb_pricing_tables` needs no responsive attributes of its own: Divi
stacks the tiers to one full-width column per row on phone automatically, in the order they're
authored (put the recommended/featured tier first or center if stacking order matters to the
client).

## Variations

- **Two-tier variant:** drop one `et_pb_pricing_table` — the module accepts any number of tiers,
  no structural change needed.
- **No-featured variant:** omit `featured="on"` entirely for a client that doesn't want to steer
  customers toward one plan; all tiers render at equal size.
- **Dark-tone variant:** swap the section to the dark navy bundle and re-pick `header_text_color`/
  `body_text_color` (light) so plain (non-featured) tiers stay legible against the dark background.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Pricing" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Simple, Transparent Pricing" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][et_pb_pricing_tables bullet_color="#f97316" featured_table_header_background_color="#f97316" featured_table_header_text_color="#ffffff" _builder_version="4.27.9" _module_preset="default"][et_pb_pricing_table title="Basic Check-Up" header_level="h3" subtitle="For a single fixture" currency="$" sum="89" per="visit" button_text="Book Basic" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" body_font="Lato||||||||" body_text_color="#475569" button_font="Lato||||||||" excluded_text_color="#cbd5e1" custom_button="on" button_bg_color="#f97316" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover" button_border_radius="6px" button_text_color="#0b2a3c"]One fixture inspected
Written estimate
No obligation to book
-Weekend appointments[/et_pb_pricing_table][et_pb_pricing_table title="Standard Service Call" header_level="h3" subtitle="Most homeowners choose this" currency="$" sum="149" per="visit" featured="on" button_text="Book Standard" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="11111111-2222-3333-4444-555555555555" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" body_font="Lato||||||||" body_text_color="#475569" button_font="Lato||||||||" custom_button="on" button_bg_color="#f97316" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover" button_border_radius="6px" button_text_color="#0b2a3c"]Full fixture inspection
Same-day repair
90-day workmanship warranty[/et_pb_pricing_table][et_pb_pricing_table title="Whole-Home Plan" header_level="h3" subtitle="Annual maintenance" currency="$" sum="399" per="year" button_text="Book Whole-Home" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" body_font="Lato||||||||" body_text_color="#475569" button_font="Lato||||||||" custom_button="on" button_bg_color="#f97316" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover" button_border_radius="6px" button_text_color="#0b2a3c"]Two seasonal inspections
Priority emergency dispatch
15% off any additional repair[/et_pb_pricing_table][/et_pb_pricing_tables][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `python3 scripts/validate.py section.txt --tokens tokens.json --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — show the user `preview.html` (or `preview.py serve`) and **stop until they approve it**; fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] Only after the user approves the local preview: `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] in `preview.html` and the draft preview, each feature line renders as a single, non-nested `<li><span>...</span></li>` (not a doubled/broken one), and the `-`-prefixed line renders as `<li class="et_pb_not_available">` with no leading `-` left in its visible text
- [ ] exactly one `h2` — no `h1` on this section; every table title is `h3`
- [ ] the featured tier is visually distinct and legible; every price/frequency on a real page traces back to the client's brief — none invented
