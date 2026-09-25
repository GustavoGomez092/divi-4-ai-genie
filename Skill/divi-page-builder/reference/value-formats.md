# Value formats

Every field type a Divi 4 attribute can have, with its grammar, a valid example, a common mistake,
and which field types use it (see each module's own page, or
[design-families.md](design-families.md), for exactly which attributes on which module). Examples
tagged &#96;&#96;&#96;divi are complete pages that pass `validate.py` with 0 errors; examples
tagged &#96;&#96;&#96;divi-fragment are partial snippets (not full pages) and are exempt from that
check.

## Colors

Field types: `color`, `color-alpha` (the alpha-capable variant used almost everywhere — background,
text, border, icon, shadow colors).

Grammar — any of:

- `#rgb` / `#rrggbb` / `#rrggbbaa` hex (3, 6 or 8 hex digits after `#`)
- `rgba(r,g,b,a)` / `rgb(r,g,b)` / `hsla(...)` / `hsl(...)`
- the keyword `transparent`
- `var(--custom-property)`
- `gcid-<uuid>` — a reference to one of the site's Global Colors, resolved to the real color **at
  render time** by a plain substring replace wherever it appears in any attribute whose name
  contains `color` (`includes/builder/class-et-builder-element.php:13470-13499`; confirmed real
  usage in `tests/fixtures/valid/divi-ai-section.txt`:
  `button_bg_color="gcid-36fd78a7-34bc-404d-873c-dafa34efaae5"`)

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_button button_text="Call now" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default" custom_button="on" button_bg_color="gcid-36fd78a7-34bc-404d-873c-dafa34efaae5" global_colors_info="{%22gcid-36fd78a7-34bc-404d-873c-dafa34efaae5%22:%91%22button_bg_color%22%93}"][/et_pb_button][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** writing a hex color as the *key* of `global_colors_info` and expecting it to
behave like a global color. That shape is legal and appears in real Divi AI output
(`tests/fixtures/valid/divi-ai-layout-skeleton.txt`:
`global_colors_info="{%22#F97316%22:%91%22background_color%22%93}"`), but it's inert bookkeeping —
only a value that literally contains `gcid-` gets substituted at render time. If you want a color
that updates everywhere from one place, the attribute's *value* must be `gcid-…`, not a hex string.

`global_colors_info` itself: a JSON object, `{"<gcid-or-hex>": ["attr_name", ...], ...}`, escaped
like any other attribute value (`%91`→`[`, `%93`→`]`, `%22`→`"`). It's the Visual Builder's
bookkeeping for which attributes on *this module* use which color, for its bulk-recolor tooling —
not something the front end reads to decide colors. Omit it, or leave it `"{}"`, for a plain
hex/rgba color that isn't tied to a Global Color.

## Lengths and units

Field type: `range` (also embedded inside composite formats below). A length is a number
immediately followed by a unit, or a bare CSS keyword:

- units: `%`, `px`, `em`, `rem`, `vh`, `vw`, `cm`, `mm`, `in`, `pt`, `pc`, `ex`, `deg`, `ms`, `s` —
  each field only accepts a subset (its own `units` list; a value with a unit outside that field's
  list is `E_BAD_UNIT`)
- keywords: `auto`, `none`, `inherit`, `initial`, `unset`, `normal` — always legal regardless of the
  field's unit list
- `calc(...)`, `var(...)`, `clamp(...)`, `min(...)`, `max(...)` — always legal
- empty string is always legal (means "use the default")

```divi-fragment
[et_pb_image _builder_version="4.27.9" _module_preset="default" max_width="800px" min_height="0" width="auto"][/et_pb_image]
```

**Common mistake:** using a unit the field doesn't allow — e.g. `border_width_all="2vh"` (border
widths only take `em`/`rem`/`px`/`cm`/`mm`/`in`/etc., not viewport units) is `E_BAD_UNIT`, and a
value with no number at all, like `width="wide"`, is `E_VALUE_FORMAT`.

## Font string (9 parts)

Field type: `font`. Nine `|`-separated parts (missing trailing parts are treated as empty):

| # | part | grammar |
|---|---|---|
| 1 | family | font family name, e.g. `Lato`, `Montserrat` |
| 2 | weight | a multiple of 100 from `100` to `900` (`100`, `200`, ... `900`), `on`, `off`, or empty |
| 3 | italic | `on`, `off`, or empty |
| 4 | uppercase | `on`, `off`, or empty |
| 5 | underline | `on`, `off`, or empty |
| 6 | smallcaps | `on`, `off`, or empty |
| 7 | strikethrough | `on`, `off`, or empty |
| 8 | line color | a color (see Colors above), or empty |
| 9 | line style | one of `solid`, `double`, `dotted`, `dashed`, `wavy`, or empty |

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato|700|on|off|off|off|off|#ff0000|dashed"]<p>Text.</p>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** writing fewer than 9 parts and assuming the rest default sanely, or putting
`on`/`off` in part 8 (line color) — parts 3–7 accept only `on`/`off`/empty, but part 8 must be a
color and part 9 must be a line style; `title_font="Montserrat|700|||||||"` (used in
`tests/fixtures/valid/handwritten-landing.txt`) — 7 trailing empty parts, i.e. no italic/underline/
etc. and no line color/style — is the normal "just set the family and weight" idiom. Another common
mistake: a weight that isn't a multiple of 100 — `text_font="Lato|750|||||||"` (or any other
non-hundred value, `on`/`off` aside) triggers `W_FONT_WEIGHT` (a warning, not blocking); use one of
`100`, `200`, `300`, `400`, `500`, `600`, `700`, `800`, `900`.

## Spacing (6 parts)

Field types: `custom_margin`, `custom_padding`. Six `|`-separated parts:
`top|right|bottom|left|linked_top_bottom|linked_left_right`. The first four are lengths (or
empty, meaning "unset"); the last two are `true`, `false`, or empty, and describe whether the
Visual Builder's UI currently links those pairs of values together (they don't change what
renders — Divi always renders the four explicit values — they're purely a UI-state hint for
whoever edits this module next in the builder).

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default" custom_padding="80px||80px||true|false"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default" custom_margin="0px||20px||false|false"]<p>Text.</p>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** writing only 2 parts (`custom_margin="20px|20px"`) expecting
top/bottom-and-left/right shorthand like plain CSS `margin: 20px 20px` — Divi's spacing string is
positional (`top|right|bottom|left|...`), not CSS shorthand; `custom_margin="20px|20px|20px|20px"`
is what "20px all around" actually looks like (or leave 5–6 off entirely).

## Border radius (5 parts)

Field type: `border-radius`. Five `|`-separated parts:
`on_or_off|top-left|top-right|bottom-right|bottom-left`. The first part must be `on`, `off`, or
empty; the remaining four are lengths.

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://client.example/wp-content/uploads/2026/09/plumber.jpg" _builder_version="4.27.9" _module_preset="default" border_radii="on|8px|8px|8px|8px"][/et_pb_image][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** giving only 4 parts (forgetting the leading `on`/`off` flag) — `border_radii`
needs the flag first: `"8px|8px|8px|8px"` (4 parts) is `E_VALUE_FORMAT`; `"on|8px|8px|8px|8px"` (5
parts) is correct.

## Yes/no

Field type: `yes_no_button` (also the type synthesized for `*_enable_color`/`*_enable_image`/etc.
"background enable" toggles). Exactly `on` or `off` (case-sensitive, no other spelling). Several
`yes_no_button` fields default to `off`/empty — an empty default there means the feature is off
(e.g. `parallax` default `off`), not "unset"; a field like `{p}_bg_color`'s family-table default
shown as `False` is a schema quirk from the underlying dump (Divi's own PHP default for that field
is boolean `false`, which the generator prints as the Python literal `False` — read it as "off"/
"not set", never as a legal attribute value to write).

```divi-fragment
[et_pb_blurb use_icon="on" _builder_version="4.27.9" _module_preset="default"][/et_pb_blurb]
```

**Common mistake:** `use_icon="yes"`, `use_icon="1"`, or `use_icon="true"` — none of those are `on`,
so the value fails `E_BAD_OPTION` (a `yes_no_button` field's only two legal `options` are `on` and
`off`).

## Selects

Field types: `select` and its variants (`select_animation`, `select-pattern`, `select-mask`,
`text_align`, `align`, `position`, `divider`, `select_with_option_groups`, `select_box_shadow`,
`presets_shadow`, `yes_no_button`). A select's value must be **exactly** one of that field's listed
options — no partial match, no case-insensitivity. `validate.py` reports `E_BAD_OPTION` with the
full options list (or the first 12, plus a pointer to the module's schema file, if there are more)
when the value doesn't match, and suggests a close spelling with `difflib` when the *attribute
name* itself is close to a real one but not exact (`E_UNKNOWN_ATTR`, a different check, for a typo
in the name rather than the value).

```divi-fragment
[et_pb_heading title_level="h2" _builder_version="4.27.9" _module_preset="default"][/et_pb_heading]
```

**Common mistake:** `title_level="H2"` (wrong case) or `title_level="heading2"` (not one of
`h1`…`h6`) — both are `E_BAD_OPTION`.

## `multiple_buttons`

Field type: `multiple_buttons` (e.g. `button_rel`, `background_mask_transform`,
`background_pattern_transform`). A `|`-separated **subset** of the field's options, in any order,
any count (including all or none of them) — unlike `multiple_checkboxes` below, this is a list of
*which* options are selected by name, not a fixed-position flag for every option.

```divi-fragment
[et_pb_image _builder_version="4.27.9" _module_preset="default" background_mask_transform="flip_horizontal|rotate_90_degree"][/et_pb_image]
```

**Common mistake:** including a value that isn't one of the field's options at all (e.g.
`button_rel="external|noopener|nofollowe"` — that trailing typo isn't in
`bookmark|external|nofollow|noreferrer|noopener`) — reported as `E_BAD_OPTION` listing exactly
which token(s) aren't recognized.

## `multiple_checkboxes` (positional)

Field type: `multiple_checkboxes` (e.g. `disabled_on`, whose options are `phone`, `tablet`,
`desktop`, in that order). Unlike `multiple_buttons`, this format is **positional, not
name-based**: the value must have exactly as many `|`-separated tokens as the field has options,
each token is `on`, `off`, or empty, and **token N always means "option N", regardless of what that
option's name is** — you never write the option's name itself in the value.

```divi-fragment
[et_pb_image _builder_version="4.27.9" _module_preset="default" disabled_on="on|off|off"][/et_pb_image]
```

`disabled_on="on|off|off"` means "disabled on phone, shown on tablet, shown on desktop" — because
`disabled_on`'s options are `phone, tablet, desktop`, in that fixed order.

**Common mistake:** writing `disabled_on="phone"` (a name, as if it were `multiple_buttons`) — that
has the wrong shape entirely (1 token instead of 3) and is `E_VALUE_FORMAT`; or writing the right
shape but assuming token order matches your own intuition rather than the field's actual `options`
order (check the module's own page for the exact list before assuming phone/tablet/desktop order
everywhere — always confirm against that field's `options` list).

## Icons

Field type: `select_icon`. To find an icon's value by name (phone, map marker, wrench, …), look it
up in `icons.md`: every icon Divi's picker offers, with the exact value to paste. Three real shapes:

- **Divi icon font:** `<numeric HTML entity>||divi||<weight>` — e.g. `&#xe03b;||divi||400`
- **Font Awesome:** `<numeric HTML entity>||fa||<weight>` — e.g. `&#xf095;||fa||900`
- **Legacy Divi 3 syntax:** `%%<number>%%` — e.g. `%%152%%` (still accepted; new content should
  prefer the `||divi||`/`||fa||` form)

The weight (`400`, `900`, ...) is optional in all three; the icon code before the first `||` can in
principle be any non-`|` text, but real Divi output always uses a `&#x…;`-style numeric HTML
entity.

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_blurb title="Burst Pipes" use_icon="on" font_icon="&#xe03b;||divi||400" header_level="h3" _builder_version="4.27.9" _module_preset="default"]<p>Fast shut-off.</p>[/et_pb_blurb][/et_pb_column][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_button button_text="Call" button_url="tel:+13055550100" custom_button="on" button_icon="&#xf095;||fa||900" _builder_version="4.27.9" _module_preset="default"][/et_pb_button][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** writing the raw glyph character instead of its HTML entity code (`font_icon="📞||fa||900"`), or forgetting the `use_icon="on"` toggle that some modules (like `et_pb_blurb`) need before their icon field has any visible effect at all.

## Uploads and URLs

Field types: `upload` (image/video sources — `background_image`, `src`, `logo`,
`background_video_mp4`, ...) and plain `text`/URL fields (`url`, `button_url`, `button_link`,
`redirect_url`, ...). Both are just a URL string — no special escaping beyond the general table in
[page-format.md](page-format.md#escaping), and note that page's caveat: URL-type
attributes do **not** decode `%22`/`%92`/`%5c` the way other attributes do, so don't put those
sequences in a URL value at all.

```divi-fragment
[et_pb_image src="https://client.example/wp-content/uploads/2026/09/plumber.jpg" alt="Plumber" _builder_version="4.27.9" _module_preset="default"][/et_pb_image]
```

**Common mistake:** pointing an image attribute at a URL on a different host than the site
(`validate.py --site-url ...` warns `W_EXTERNAL_IMAGE` for every image field: an upload field
whose media type is an image — `et_pb_image` `src`, blurb `image`, `background_image`, `logo`,
`image_url`, `portrait_url`, a video's `image_src` poster, … — and button `*_bg_image`s; video and
audio fields such as `et_pb_video` `src` are not image fields and are never flagged) — upload the image to the site's own Media Library first and use that URL, so it survives
the site being moved/renamed and benefits from the site's own image optimization.

## Gradient stops

Field type: `gradient-stops` (`background_color_gradient_stops`, only meaningful when
`use_background_color_gradient="on"`). A `|`-separated list of two or more stops, each stop being
`<color> <position>%` (color and position separated by a space):
`"#rrggbb xx%|rgba(r,g,b,a) yy%"` (confirmed grammar,
`includes/builder/module/settings/migration/BackgroundGradientStops.php:1-16`; default value
`#2b87da 0%|#29c4a9 100%`).

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default" use_background_color_gradient="on" background_color_gradient_stops="#0b2a3c 0%|#0e7c86 100%" background_color_gradient_direction="180deg"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default"]<p>Text.</p>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** setting `background_color_gradient_stops` without also setting
`use_background_color_gradient="on"` — the gradient fields are inert until that toggle is on
(this validator doesn't currently flag that specific omission, unlike the `__hover_enabled`/
`_last_edited` toggles below, so double-check it by eye).

## Box-shadow presets

Field types: `select_box_shadow` (the module-level `box_shadow_style`) and `presets_shadow` (the
per-text-element shadow styles, e.g. `text_shadow_style`, `header_text_shadow_style`,
`button_text_shadow_style`). Legal values, confirmed from Divi's own preset table
(`includes/builder/module/field/BoxShadow.php`): `none`, `preset1`, `preset2`, `preset3`,
`preset4`, `preset5`, `preset6`, `preset7`. Choosing a preset (anything but `none`) fills in that
preset's own `horizontal`/`vertical`/`blur`/`spread`/`position` values — which is why those
sibling fields' defaults show as "depends on `box_shadow_style`" in the family tables — but you can
still override any of them individually with the matching `box_shadow_horizontal`/`_vertical`/
`_blur`/`_spread`/`_position` (or `{p}_text_shadow_horizontal_length`/etc. for text shadows)
attribute.

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://client.example/wp-content/uploads/2026/09/plumber.jpg" _builder_version="4.27.9" _module_preset="default" box_shadow_style="preset1" box_shadow_color="rgba(0,0,0,0.4)"][/et_pb_image][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** `box_shadow_style="1"` or `box_shadow_style="shadow1"` — the value is the
literal word `preset1` (not a bare number, not a different name); this field type isn't currently
option-checked by `validate.py` (its schema entry has no `options` list), so a wrong value won't
error, it will just silently render no shadow.

## Animation

Fields: `animation_style` (the switch — `none`, `fade`, `slide`, `bounce`, `zoom`, `flip`, `fold`,
`roll`), plus `animation_direction`, `animation_duration`, `animation_delay`,
`animation_starting_opacity`, `animation_speed_curve`, `animation_repeat`, and one
`animation_intensity_<effect>` field **per effect** (`animation_intensity_slide`, `_fold`, `_roll`,
`_zoom`, `_flip`) — only the intensity field matching the chosen `animation_style` has any effect.

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://client.example/wp-content/uploads/2026/09/plumber.jpg" _builder_version="4.27.9" _module_preset="default" animation_style="fade" animation_direction="bottom" animation_duration="800ms" animation_delay="100ms"][/et_pb_image][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** setting `animation_intensity_zoom` while `animation_style="fade"` — the
`fade` effect never reads the `_zoom` intensity field, so the value has no effect; set the
intensity field whose suffix matches `animation_style`.

## Transform (composite sub-attributes)

`transform_styles` itself is a `composite` type — a UI grouping label, not a real attribute; the
actual attributes you write are its members, each its own `transform`-typed, `|`-separated value:

| attribute | parts |
|---|---|
| `transform_scale` | `x%\|y%` |
| `transform_translate` | `x-length\|y-length` |
| `transform_rotate` | `x-deg\|y-deg\|z-deg` |
| `transform_skew` | `x-deg\|y-deg` |
| `transform_origin` | `x%\|y%` (or keyword positions) |

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://client.example/wp-content/uploads/2026/09/plumber.jpg" _builder_version="4.27.9" _module_preset="default" transform_scale="110%|110%" transform_translate="0px|-10px" transform_origin="50%|50%"][/et_pb_image][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** writing `transform_scale="110%"` (one part) expecting it to apply uniformly —
Divi's scale is always `x%|y%` (2 parts); a single value there is treated as "x, no y" rather than
"both".

## Scroll effects

Fields: `scroll_<effect>_enable` (`yes_no_button`, must be `on` before the effect field has any
effect at all — this mirrors the hover/responsive "enabled" toggle pattern below) plus
`scroll_<effect>` itself (type `motion`), for `vertical_motion`, `horizontal_motion`, `fade`,
`scaling`, `rotating`, `blur`. Each `motion` value is a `|`-separated numeric string (7 parts in
every default, e.g. `scroll_vertical_motion`'s default `0|50|50|100|4|0|-4`) — not currently
format-checked by `validate.py` (free-form), so copy a working default and adjust its numbers
rather than composing one from scratch. Separately, `sticky_position`
(`none`/`top`/`bottom`/`top_bottom`) turns on CSS `position: sticky` for the module itself; that's
independent of the `__sticky` style-override mechanism documented under Sticky below.

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://client.example/wp-content/uploads/2026/09/plumber.jpg" _builder_version="4.27.9" _module_preset="default" scroll_vertical_motion_enable="on" scroll_vertical_motion="0|50|50|100|4|0|-4"][/et_pb_image][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** setting `scroll_vertical_motion` without `scroll_vertical_motion_enable="on"`
— the effect field is inert until its own `_enable` toggle is on.

## Display conditions

Field type: `display_conditions` (`tab_slug: custom_css`, default empty string — empty means "no
conditions, always display"). Stored as a JSON structure, escaped like other JSON-shaped attributes
(`%91`/`%93`/`%22`), when conditions exist; the exact per-condition schema isn't format-checked by
`validate.py` (any string is accepted, including empty) and wasn't independently reverse-engineered
for this skill. Recommendation: leave this attribute unset unless you specifically need
conditional display, and if you do, base the value on a condition exported from a real page in the
Visual Builder rather than hand-composing the JSON.

```divi-fragment
[et_pb_text _builder_version="4.27.9" _module_preset="default"]<p>Always visible; no display_conditions set.</p>[/et_pb_text]
```

## Responsive (`_tablet`, `_phone`, `_last_edited`)

Any field with `mobile_options` (marked **R** in the family tables) can take `_tablet` and `_phone`
suffixed variants (e.g. `title_font_size_tablet`, `title_font_size_phone`) that override the base
value at that breakpoint, cascading desktop → tablet → phone (an unset breakpoint inherits the
next-larger one). Setting a `_tablet`/`_phone` value has no effect until the base field's
`_last_edited` attribute is set to `"on|<breakpoint>"` (`W_RESPONSIVE_DISABLED` otherwise) — this
records which breakpoint the Visual Builder's UI last showed as active; it does not gate *which*
breakpoint's override renders (all set breakpoints always render at their own width), it only has
to be present and start with `on`.

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Emergency Plumber" _builder_version="4.27.9" _module_preset="default" title_font_size="56px" title_font_size_tablet="42px" title_font_size_phone="34px" title_font_size_last_edited="on|phone"][/et_pb_heading][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** setting `title_font_size_phone` without `title_font_size_last_edited="on|..."`
— the phone override is written correctly but `validate.py` warns `W_RESPONSIVE_DISABLED`, and in
practice a page saved this way through the Visual Builder wouldn't happen (the builder always sets
`_last_edited` itself), so this usually means the shortcode was hand-edited incompletely.

## Hover (`__hover` + `__hover_enabled`, and the background group key)

Any field with `hover: true` (marked **H**) can take a `__hover` suffixed variant
(`button_bg_color__hover`) that applies while the element is hovered. It's inert until the
matching `__hover_enabled` attribute is set to `"on|hover"` (`W_HOVER_DISABLED` otherwise;
`validate.py` accepts `on`/`off` optionally followed by `|word`, but real Divi output always writes
`on|hover`). **The background group key**: for `background_color` and `background_image`
specifically, the enable attribute's name is not `background_color__hover_enabled` /
`background_image__hover_enabled` — both share one shared key, `background__hover_enabled`,
because the Background family treats color/image/gradient/video/pattern/mask as one group for
hover purposes (`scripts/divi_checks_values.py`: `key = "background" if
base in ("background_color", "background_image") else base`). Every other hover-capable field uses
its own name as the key.

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_button button_text="Call now" button_url="tel:+13055550100" custom_button="on" button_bg_color="#f97316" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover" _builder_version="4.27.9" _module_preset="default"][/et_pb_button][et_pb_text _builder_version="4.27.9" _module_preset="default" background_color="#0b2a3c" background_color__hover="#0e7c86" background__hover_enabled="on|hover"]<p>Hover me.</p>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** writing `background_color__hover_enabled="on|hover"` (following the
"attribute name + `__hover_enabled`" pattern that works for every other field) — for background
color/image specifically, that's the wrong key; it must be `background__hover_enabled`.

## Sticky (`__sticky` + `__sticky_enabled`)

Structurally identical to hover: any field with `sticky: true` (marked **S**) can take a `__sticky`
suffixed variant, gated by `<key>__sticky_enabled="on|sticky"` (`W_STICKY_DISABLED` otherwise),
with the same `background` group key for `background_color`/`background_image`. This only overrides
*style* while the module is stuck — it does nothing unless the module (or an ancestor) is actually
sticky, which is a separate, module-level setting: `sticky_position`
(`none`/`top`/`bottom`/`top_bottom`, from the Scroll effects family) turns sticky positioning on in
the first place; `sticky_limit_top`/`sticky_limit_bottom`, `sticky_offset_top`/
`sticky_offset_bottom`, `sticky_offset_surrounding` and `sticky_transition` further tune it.

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default" sticky_position="top" background_color="#ffffff" background_color__sticky="#f1f5f9" background__sticky_enabled="on|sticky"]<p>Sticky bar.</p>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Common mistake:** setting `background_color__sticky`/`background__sticky_enabled` on a module
that never sets `sticky_position` to anything but `none` — the sticky style override is defined
correctly but never has a chance to apply, because the module never actually becomes sticky.
