# Value formats (Divi 5)

How a Divi 5 attribute value is shaped, and the grammar of every leaf type. The Divi 4 counterpart is
[../value-formats.md](../value-formats.md). Which attributes a block has, and each one's type, is on its page in
[modules/](modules/README.md) and in [design-families.md](design-families.md). Every ```` ```divi5 ```` example is a
complete section in canonical markup that passes `validate.py --fragment` with no findings (and renders on
Divi 5.13.1: `research/divi5/doc-experiments.md` §3). ```` ```json ```` blocks are formatted views for reading
only; on the page the same JSON is escaped and on one line ([page-format.md](page-format.md#canonical-json-escaping-and-why)).

## The value model

Every attribute is a nested path, and the value sits under a breakpoint and a state
(`storage-and-serialization.md` §5):

```
<element>.<group>.<attribute…>.<breakpoint>.<state>  =  value
  element    : module (the whole block) or a named part: title, content, button, image, imageIcon, …
  group      : innerContent (content) | decoration (design) | advanced (settings) | meta
  attribute… : the family key and sub-table, e.g. decoration.font.font, decoration.spacing
  breakpoint : desktop | tablet | phone                 (see Breakpoints)
  state      : value | hover | sticky (+ focus, checked, active on form fields)
```

The value at the bottom is either a scalar or an object whose keys the tables call **keys**. A blurb that uses all
of it:

```json
{"title": {
   "innerContent": {"desktop": {"value": {"text": "Burst pipes"}}},
   "decoration": {"font": {"font": {
     "desktop": {"value": {"headingLevel": "h3", "size": "22px", "color": "#0b2a3c"},
                 "hover": {"color": "#f97316"}},
     "phone":   {"value": {"size": "18px"}}}}}},
 "imageIcon": {"innerContent": {"desktop": {"value": {"useIcon": "on",
                 "icon": {"unicode": "&#xe03b;", "type": "divi", "weight": "400"}}}}},
 "content": {"innerContent": {"desktop": {"value": "<p>Fast shut-off and repair.</p>"}}},
 "module": {"decoration": {
   "spacing": {"desktop": {"value": {"padding": {"top": "24px", "right": "24px", "bottom": "24px", "left": "24px",
                                                  "syncVertical": "on", "syncHorizontal": "on"}}},
               "phone":   {"value": {"padding": {"top": "16px", "right": "16px", "bottom": "16px", "left": "16px",
                                                  "syncVertical": "on", "syncHorizontal": "on"}}}},
   "background": {"desktop": {"value": {"color": "#f8fafc"}}}}},
 "builderVersion": "5.13.1"}
```

On the page (after an `h2`, so the `h3` title doesn't skip a level):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Services"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/blurb {"title":{"innerContent":{"desktop":{"value":{"text":"Burst pipes"}}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","size":"22px","color":"#0b2a3c"},"hover":{"color":"#f97316"}},"phone":{"value":{"size":"18px"}}}}}},"imageIcon":{"innerContent":{"desktop":{"value":{"useIcon":"on","icon":{"unicode":"\u0026#xe03b;","type":"divi","weight":"400"}}}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eFast shut-off and repair.\u003c/p\u003e"}}},"module":{"decoration":{"spacing":{"desktop":{"value":{"padding":{"top":"24px","right":"24px","bottom":"24px","left":"24px","syncVertical":"on","syncHorizontal":"on"}}},"phone":{"value":{"padding":{"top":"16px","right":"16px","bottom":"16px","left":"16px","syncVertical":"on","syncHorizontal":"on"}}}},"background":{"desktop":{"value":{"color":"#f8fafc"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Rules:

- **Everything is wrapped** in `{"<breakpoint>": {"<state>": value}}`, even plain content: a heading's text is
  `"title": {"innerContent": {"desktop": {"value": "Our services"}}}`. A value written without the wrapper is
  `E5_BAD_BREAKPOINT`. The only unwrapped attributes are the block-level `builderVersion`, `modulePreset`,
  `groupPreset` and `locked`.
- **Only write what you change.** An object value may hold any subset of its keys (`{"size": "18px"}` is a complete
  font value); unset keys and unset attributes keep Divi's defaults, which each module page lists under "Render
  defaults" (`schema.md` §4).
- A path or key the block doesn't have is `E5_UNKNOWN_ATTR` (with a "did you mean" hint); a value that doesn't fit
  its type is `E5_BAD_VALUE`.
- Styles go under the element's family sub-table, not on the family root: a title's size is
  `title.decoration.font.font`, **not** `title.decoration.font` (Divi styles text only from `….font.font`; keys
  written on the bare `….decoration.font` validate but render nothing: `doc-experiments.md` §1).

## Breakpoints

| breakpoint | applies at | on by default? |
|---|---|---|
| `desktop` | base value, all widths | yes |
| `tablet` | ≤ 980 px | yes |
| `phone` | ≤ 767 px | yes |
| `phoneWide` | ≤ 860 px | no |
| `tabletWide` | ≤ 1024 px | no |
| `widescreen` | ≥ 1280 px | no |
| `ultraWide` | ≥ 1440 px | no |

(`Breakpoint::get_default_settings_values()`, `Breakpoint.php:72-150`; a site can change them in the option
`et_divi_builder_breakpoints`.)

- Use `desktop`, `tablet` and `phone`. A value for a switched-off breakpoint applies only if the site turns it on
  (`W5_BREAKPOINT_DISABLED`).
- Always set `desktop`; tablet and phone only vary it (`W5_HOVER_WITHOUT_DESKTOP` when a breakpoint or state is set
  without `desktop.value`). A breakpoint you leave unset inherits the next larger one: desktop values print
  with no media query, tablet values in `@media only screen and (max-width:980px)` (which phones match too), phone
  values in `(max-width:767px)` (live check).
- **There are no enable flags.** Divi 4's `_last_edited="on|phone"` is gone: a `phone` key is simply there or not
  (`Conversion::enabled()`, `Conversion.php:740-755`, drops disabled Divi 4 values on conversion).
- Leaves marked `desktop` in a table's **R** column take only a desktop value, e.g. `headingLevel`, `useIcon`, link
  URLs, `htmlAttributes` (`E5_BAD_BREAKPOINT` on tablet or phone).
- `module.decoration.disabledOn` also accepts the pseudo-breakpoints `desktopAbove` and `tabletOnly`.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Emergency Plumber"}},"decoration":{"font":{"font":{"desktop":{"value":{"size":"56px"}},"tablet":{"value":{"size":"42px"}},"phone":{"value":{"size":"34px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## States: hover, sticky and the form states

States are `value`, `hover`, `sticky`, `focus`, `checked` and `active` (`ModuleUtils::states()`,
`ModuleUtils.php:2464-2482`). A state is a sibling of `value` under the breakpoint.

- **Presence turns it on.** Divi 4's `__hover_enabled="on|hover"` / `__sticky_enabled` don't exist: writing a
  `hover` key is the whole switch. Set only the keys that change on hover; the rest carry over from `value`.
- A state is allowed only where the tables' **states** column lists it (`E5_BAD_STATE`): many layout and
  animation leaves take no hover; `focus`, `checked` and `active` exist only on form fields.
- Hover applies while the **module** is hovered. A blurb's `title.decoration.font.font` hover color rendered as
  `.et_pb_blurb_0:hover .et_pb_module_header{color:…}` (live check).

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Call now","linkUrl":"tel:+13055550100"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"background":{"desktop":{"value":{"color":"#f97316"},"hover":{"color":"#ea580c"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

- `sticky` values apply only while the block is stuck, and only if the block (or an ancestor) is made sticky with
  `module.decoration.sticky` → `{"position": "top"}` (or `bottom`, `topBottom`; the [Sticky](design-families.md#sticky)
  family). Divi prints them under the `.et_pb_sticky` class it adds while stuck (live check):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"sticky":{"desktop":{"value":{"position":"top"}}},"background":{"desktop":{"value":{"color":"#ffffff"},"sticky":{"color":"#f1f5f9"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eCall 24/7: (305) 555-0100\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Leaf types

Every `type` in the module pages and family tables is one of these (`scripts/schema5/families5.json` → `_types`,
printed in [design-families.md → Leaf types](design-families.md#leaf-types)). `""` (empty string) means "unset" for
every type and is always accepted.

### color

Grammar: `#rgb`, `#rgba`, `#rrggbb`, `#rrggbbaa`; `rgb()`/`rgba()`/`hsl()`/`hsla()` (any case); `transparent`;
`var(--name)`; or a global color reference
`$variable({"type":"color","value":{"name":"gcid-…","settings":{}}})$`
([below](#variable-references-global-colors-and-design-variables)).

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eFree estimates.\u003c/p\u003e"}}},"module":{"decoration":{"background":{"desktop":{"value":{"color":"rgba(11,42,60,0.9)"}}},"border":{"desktop":{"value":{"styles":{"all":{"width":"2px","style":"solid","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-primary-color\u0022,\u0022settings\u0022:{}}})$"}}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: a CSS color name (`"red"`, `"navy"`) or `oklch()`: `E5_BAD_VALUE`. Write hex or `rgba()`.

### length

Grammar: a number with a CSS unit (`px`, `%`, `em`, `rem`, `vw`, `vh`, `vmin`, `vmax`, `ch`, `ex`, `cm`, `mm`, `in`,
`pt`, `pc`, `deg`, `rad`, `turn`, `ms`, `s`, `fr`; restricted to the leaf's own `units` where a table lists them),
a unitless number (`lineHeight: "1.4"`), a keyword (`auto`, `none`, `inherit`, `initial`, `unset`, `normal`,
`fit-content`, `min-content`, `max-content`), a CSS function (`calc()`, `clamp()`, `min()`, `max()`, `var()`), or a
number variable (`$variable({"type":"content",…})$`). Always a **string**: `"24px"`, not `24`.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eNarrow column of copy.\u003c/p\u003e"}}},"module":{"decoration":{"sizing":{"desktop":{"value":{"maxWidth":"720px","width":"90%"}}},"spacing":{"desktop":{"value":{"margin":{"bottom":"clamp(24px, 4vw, 48px)"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: CSS shorthand in one leaf (`"padding": "20px 10px"`, `E5_BAD_VALUE`); spacing is an object, see
[spacing](#spacing). And a bare JSON number (`"top": 40`) passes the validator, but Divi prints it without a unit
(`padding-top:40`), which browsers ignore: the padding silently disappears (live check, `doc-experiments.md` §8).

### number

Grammar: a JSON number or a numeric string, no unit. Used for counts and factors: `zIndex`, `gridColumnCount`,
`columnCount`, animation intensities, map coordinates and zoom (`lat`/`lng` are JSON numbers in Divi's own
output), `specialtyColumns`.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/map {"map":{"innerContent":{"desktop":{"value":{"address":"Miami, FL","lat":25.7617,"lng":-80.1918,"zoom":11}}}},"module":{"decoration":{"zIndex":{"desktop":{"value":"2"}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/map-pin {"title":{"innerContent":{"desktop":{"value":"Downtown office"}}},"pin":{"innerContent":{"desktop":{"value":{"lat":25.7617,"lng":-80.1918}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/map --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: a unit on a number leaf (`"zIndex": "10px"`) is `E5_BAD_VALUE`.

### font-family and font-weight

`font-family`: a family name string as the site loads it (`"Montserrat"`, `"Open Sans"`), or a font variable:
`$variable({"type":"content","value":{"name":"gvid-…","settings":{}}})$`, or the Customizer fonts
`--et_global_heading_font` / `--et_global_body_font` as the `name`. Divi adds the fallback stack itself.

`font-weight`: `"100"`…`"900"` (any 1–1000 is accepted; off the hundreds warns `W_FONT_WEIGHT`), `normal`,
`bold`, `lighter`, `bolder`, `variable` (variable-font mode), a Divi global-font weight token such as
`"Open Sans_weight"`, or a variable.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Our services"}},"decoration":{"font":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"700","lineHeight":"1.2em","letterSpacing":"-0.5px","headingLevel":"h2"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"How it works"}},"decoration":{"font":{"font":{"desktop":{"value":{"family":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022\u002d\u002det_global_heading_font\u0022,\u0022settings\u0022:{}}})$","weight":"600","headingLevel":"h2"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The second heading uses the site's Customizer heading font; it rendered `font-family:var(--et_global_heading_font)`
(live check). Common mistakes: a Divi 4 font string (`"Montserrat|700|||||||"`, which is not a family name), and
putting the font on the bare `title.decoration.font` instead of `title.decoration.font.font` (renders nothing). With
`--tokens`, a family the site doesn't use warns `W_OFF_BRAND_FONT`.

### enum

Grammar: exactly one of the leaf's listed options, case-sensitive. With `multiple` (font `style`), a JSON **list** of
options: `"style": ["italic", "underline"]`.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Our services"}},"decoration":{"font":{"font":{"desktop":{"value":{"textAlign":"center","style":["italic"],"headingLevel":"h2"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: `"headingLevel": "H2"` or `"heading2"` (`E5_BAD_VALUE`, which lists the options).

### onoff

Grammar: `"on"` or `"off"`. Divi 5 keeps Divi 4's yes/no values as these strings.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/blurb {"title":{"innerContent":{"desktop":{"value":{"text":"Burst pipes"}}}},"imageIcon":{"innerContent":{"desktop":{"value":{"useIcon":"on","icon":{"unicode":"\u0026#xe03b;","type":"divi","weight":"400"}}}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eFast shut-off.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: `"yes"`, `"true"`, `true` or `1` (`E5_BAD_VALUE`).

### text

Grammar: any string: plain text (a heading title, a button label), a CSS class or id, a date, a CSS value Divi
passes through (`textWrap`, `justifyContent`). Text in `innerContent` is output as HTML, so it follows the
[html](#html) rules for `&`, `<` and brackets.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Emergency Plumber in Miami"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2"}}}}}},"module":{"advanced":{"htmlAttributes":{"desktop":{"value":{"class":"hero-title"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: a number or object where a string is expected (`"title": {"innerContent": {"desktop": {"value":
5}}}`, `E5_BAD_VALUE`), or the wrong shape for the module: a blurb's `title.innerContent` is an object
`{"text": …}`, a heading's is a plain string (the module page's **key** column tells which).

### html

Grammar: a string of HTML, in `innerContent` (text bodies, blurb and toggle content, code modules). Write normal
HTML: tags, entities (`&amp;`, `&copy;`), links. Canonical escaping turns every `<`, `>`, `&` and `"` into
`<`… in the stored JSON; `divi5_blocks` does that for you. Text content gets `wpautop` (paragraphs from line
breaks) and `do_shortcode`.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003ch2\u003eWhy us\u003c/h2\u003e\u003cp\u003eUpfront pricing \u0026amp; \u003cstrong\u003eno overtime fees\u003c/strong\u003e. \u003ca href=\u0022/pricing/\u0022\u003eSee prices\u003c/a\u003e.\u003c/p\u003e\u003cul\u003e\u003cli\u003eLicensed\u003c/li\u003e\u003cli\u003eInsured\u003c/li\u003e\u003c/ul\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistakes: a literal `[` followed by a letter (runs as a shortcode; write `&#91;`/`&#93;`,
`W5_SHORTCODE_BRACKETS`); raw `<`/`"` in the stored JSON (`E5_NONCANONICAL`); and headings inside HTML, which count
in the page outline like module headings (`E5_MULTIPLE_H1`, `W_HEADING_SKIP`).

### url

Grammar: a URL string without spaces: absolute (`https://…`), site-relative (`/contact/`), an anchor (`#quote`),
`mailto:`, `tel:`, or a link variable. It sits next to a target key: `linkTarget` (buttons, images) or `target`
(titles, `module.advanced.link`, icons), `"on"` = new tab. See [Links](#links).

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Email us","linkUrl":"mailto:office@client.example"}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Book online","linkUrl":"https://client.example/book/","linkTarget":"on"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: spaces in the URL (`"/my page/"`, `E5_BAD_VALUE`); percent-encode them. The second button above
opens in a new tab: `linkTarget: "on"` rendered `target="_blank"`.

### image

Grammar: an image URL string, in `src` (image, blurb, slide, testimonial `portrait`, video `thumbnail`) or `url`
(team member `image`, background `image.url`). Use images from the site's Media Library; `validate.py
--site-url` warns `W_EXTERNAL_IMAGE` for other hosts. See [Images](#images) for `alt` and `titleText`.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://client.example/wp-content/uploads/2026/09/plumber.jpg","alt":"Plumber repairing a kitchen sink","titleText":"Kitchen sink repair"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: forgetting `alt` (`W5_NO_ALT` on `divi/image` and `divi/fullwidth-image`).

### icon

Grammar: an object `{"unicode": "<HTML entity>", "type": "divi" | "fa", "weight": "<number>"}`, all three keys. See
[Icons](#icons) for where the values come from.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/blurb {"title":{"innerContent":{"desktop":{"value":{"text":"Call us"}}}},"imageIcon":{"innerContent":{"desktop":{"value":{"useIcon":"on","icon":{"unicode":"\u0026#xf095;","type":"fa","weight":"900"}}}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003e(305) 555-0100\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Call now","linkUrl":"tel:+13055550100"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on","icon":{"enable":"on","settings":{"unicode":"\u0026#xf095;","type":"fa","weight":"900"},"placement":"left"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: pasting the Divi 4 string (`"icon": "&#xf095;||fa||900"`) or leaving out `weight` or `type`: both
are `E5_BAD_VALUE`, and Divi renders no icon for an object that lacks a key.

### spacing

Grammar: an object with any of `top`, `right`, `bottom`, `left` (each a [length](#length) string) and
`syncVertical`, `syncHorizontal` (`"on"`/`"off"`). It is the value of `margin` and `padding` in the
[Spacing](design-families.md#spacing) family: `module.decoration.spacing` → `{"padding": {…}, "margin": {…}}`.

- Unset sides keep their defaults: `{"padding": {"top": "80px", "bottom": "80px"}}` is complete.
- The sync flags record whether the Visual Builder's UI links top/bottom (`syncVertical`) and left/right
  (`syncHorizontal`). Divi's CSS ignores them (`Spacing.php` reads only the four sides; `doc-experiments.md` §5),
  like Divi 4's `true|false` spacing parts. Set them `"on"` when the linked pair is equal and `"off"` otherwise, so
  the builder shows the page as written; Divi's converter always writes both.
- Each side is a length **string** (`"40px"`); a bare number renders no padding (see [length](#length)).

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"spacing":{"desktop":{"value":{"padding":{"top":"80px","right":"0px","bottom":"80px","left":"0px","syncVertical":"on","syncHorizontal":"on"}}},"phone":{"value":{"padding":{"top":"40px","right":"0px","bottom":"40px","left":"0px","syncVertical":"on","syncHorizontal":"on"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eSection with symmetric padding.\u003c/p\u003e"}}},"module":{"decoration":{"spacing":{"desktop":{"value":{"margin":{"top":"0px","bottom":"24px","syncVertical":"off","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: Divi 4's positional string (`"80px||80px||true|false"`) or CSS shorthand (`"80px 0"`):
`E5_BAD_VALUE`.

### radius

Grammar: an object with any of `topLeft`, `topRight`, `bottomRight`, `bottomLeft` (lengths) and `sync` (`"on"`
when the four corners are linked in the builder UI; not read by the CSS, `Border.php:70`). It is the `radius` key of
the [Border](design-families.md#border) family. Divi's converter sometimes writes a single length string; write
the object.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://client.example/wp-content/uploads/2026/09/plumber.jpg","alt":"Our van"}}},"decoration":{"border":{"desktop":{"value":{"radius":{"sync":"on","topLeft":"12px","topRight":"12px","bottomRight":"12px","bottomLeft":"12px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistake: Divi 4's `"on|8px|8px|8px|8px"` (`E5_BAD_VALUE`), or putting the radius on an element the block
doesn't style: an image's corners are `image.decoration.border`, not `module.decoration.border`.

### gradient

Grammar: a JSON **list** of stops, `[{"position": <number 0–100>, "color": <color>}, …]`, in a gradient's
`stops`; `position` is a percentage written as a plain number, as in Divi's own output. The gradient itself is an
object in the [Background](design-families.md#background) family:
`{"enabled": "on", "type": "linear", "direction": "90deg", "stops": […]}` (`direction` defaults to `180deg`).

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"gradient":{"enabled":"on","type":"linear","direction":"90deg","stops":[{"position":0,"color":"#1e3a8a"},{"position":100,"color":"#3b82f6"}]}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Spring tune-up"}},"decoration":{"font":{"font":{"desktop":{"value":{"color":"#ffffff","headingLevel":"h2"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Common mistakes (live check, `doc-experiments.md` §8): Divi 4's `"#fff 0%|#000 100%"` string (`E5_BAD_VALUE`);
leaving out `"enabled": "on"` (no gradient renders); and positions with a unit (`"position": "0%"`), which the
validator accepts but which rendered no gradient at all. `0` and `"0"` both work.

### object

Grammar: a JSON object whose keys aren't typed individually (the table notes say what goes in it). Examples:
`transform` `rotate`/`scale`/`translate`/`skew` (`{"x": …, "y": …, "z": …}`), a gradient container, variable-font
`variationSettings`. Where a table also lists dotted keys under it (`gradient.stops`, `styles.all.width`), those
keys are typed and checked.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://client.example/wp-content/uploads/2026/09/plumber.jpg","alt":"Sale badge"}}}},"module":{"decoration":{"transform":{"desktop":{"value":{"rotate":{"x":"0deg","y":"0deg","z":"-3deg"},"scale":{"x":"105%","y":"105%"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

It rendered `transform:scaleX(1.05) scaleY(1.05) rotateX(0deg) rotateY(0deg) rotateZ(-3deg)` (live check). Common
mistake: a string (`"rotate": "-3deg"`, `E5_BAD_VALUE`).

### json

Grammar: any JSON value; the validator does not look inside. The one you are likely to write is
`module.decoration.attributes`: custom HTML attributes as rows
`{"attributes": [{"id": "<new UUIDv4>", "name": "…", "value": "…", "adminLabel": "…"}]}`, plus
`"targetElement": "image"` for an image's attributes. Divi's converter writes CSS classes (`"name": "class"`),
image `alt` and `title` this way (`storage-and-serialization.md` §5).

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eTracked lead copy.\u003c/p\u003e"}}},"module":{"decoration":{"attributes":{"desktop":{"value":{"attributes":[{"id":"4f1c2b7e-9a53-4d2e-8f61-0c7b5e2a9d14","name":"data-track","value":"hero-lead","adminLabel":"Tracking"}]}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

It rendered `data-track="hero-lead"` on the module (live check). Common mistake: reusing an `id` copied from
another row or page; generate a fresh UUIDv4 for every row.

## `$variable` references: global colors and design variables

A value can point at a site-wide global instead of holding a literal (`tokens-and-detection.md` §1, §2). The
reference is a string: `$variable(` + a JSON object + `)$`.

| global | reference | resolved at render to |
|---|---|---|
| global color, or a Customizer color | `$variable({"type":"color","value":{"name":"gcid-…","settings":{}}})$` | `var(--gcid-…)` |
| number, font, image or gradient variable | `$variable({"type":"content","value":{"name":"gvid-…","settings":{}}})$` | `var(--gvid-…)` |
| string or link variable | same, `"type":"content"` | the text or URL, inline |
| Customizer heading/body font | `"name":"--et_global_heading_font"` / `"--et_global_body_font"`, `"type":"content"` | `var(--et_global_heading_font)` |

- **Use only ids from `tokens.json`.** The five Customizer colors always exist: `gcid-primary-color`,
  `gcid-secondary-color`, `gcid-heading-color`, `gcid-body-color`, `gcid-link-color`. An unknown id renders as
  nothing (`W5_UNKNOWN_VARIABLE` with `--tokens`). Neither REST nor the skill can create new globals.
- The type must suit the leaf: `color` references in color leaves (and gradient stop colors), `content` in length,
  number, font, text, URL and image leaves (`E5_BAD_VALUE` otherwise). A malformed reference is `E5_BAD_VARIABLE`.
- `settings` can adjust a color: `{"hue": …, "saturation": …, "lightness": …, "opacity": …}` renders an
  `hsl(from var(--gcid-…) …)` derived color. Leave it `{}` unless the site's tokens use one.
- The reference is JSON inside a JSON string, so its quotes are escaped: in canonical markup every `"` in it is
  `"` (`divi5_blocks` handles this).
- When `tokens.json` maps a role to a global (the site's buttons all use `gcid-…`), write the reference, not the hex:
  the page then follows the client's palette.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Book a visit","linkUrl":"/contact/"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-primary-color\u0022,\u0022settings\u0022:{}}})$"},"hover":{"color":"#ea580c"}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Trusted since 2009"}},"decoration":{"font":{"font":{"desktop":{"value":{"family":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022\u002d\u002det_global_heading_font\u0022,\u0022settings\u0022:{}}})$","headingLevel":"h2"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Rendered `background-color:var(--gcid-primary-color)` and `font-family:var(--et_global_heading_font)` (live check).

## Presets: `modulePreset` and `groupPreset`

Presets are stored in the option `et_divi_builder_global_presets_d5` and referenced by id (`tokens-and-detection.md`
§2, §3.5):

- **`modulePreset`**: a block-level list (not wrapped in a breakpoint), `["<id>"]`. The list is a stack; one id is
  the normal case. **Omit it** to get the site's default preset for that module; `["default"]` means the same and is
  what the converter writes.
- **`groupPreset`**: an option-group preset for one group of the module, keyed by the group's id, with the group's
  component name:

```json
"groupPreset": {"designTitleText": {"presetId": ["<id from tokens.json>"], "groupName": "divi/font"}}
```

- **Never write an id that isn't in `tokens.json`.** An unknown `modulePreset` id silently drops the module's
  default preset styling: the block renders with class `preset--module--divi-button--<id>` and no preset CSS
  (§3.5). `validate.py` warns `W5_UNKNOWN_PRESET` for any id other than `default` that the tokens don't list.
- A preset supplies the look; don't also set conflicting inline attributes. Inline attributes win over the preset
  (render defaults, then presets, then the block's own attributes: `schema.md` §4).

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Call now","linkUrl":"tel:+13055550100"}}}},"modulePreset":["default"],"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Icons

An icon is an object `{"unicode", "type", "weight"}` wherever it appears: `imageIcon.innerContent` → `icon` (blurb),
`icon.innerContent` (icon module), `button.decoration.button` → `icon.settings` (buttons), and the icon families.

**Where the values come from:** [../icons.md](../icons.md) lists every icon of the picker with its Divi 4 value,
`<entity>||<type>||<weight>`. Split that string on `||`:

| Divi 4 value (icons.md) | Divi 5 icon object |
|---|---|
| `&#xf095;` `\|\|fa\|\|900` | `{"unicode": "&#xf095;", "type": "fa", "weight": "900"}` |
| `&#xe03b;` `\|\|divi\|\|400` | `{"unicode": "&#xe03b;", "type": "divi", "weight": "400"}` |
| `&#xf0a9;` `\|\|fa\|\|900` | `{"unicode": "&#xf0a9;", "type": "fa", "weight": "900"}` |

- This is exactly Divi's converter (`ValueExpansion::convertFontIcon()`, `ValueExpansion.php:31-49`), and all 45 icon
  values in the 35 converted fixtures follow it (`&#xf0a9;||fa||900` → `"unicode":"&#xf0a9;","type":"fa","weight":"900"`).
- The 1,989 values in icons.md are exactly the entries of Divi 5.13.1's own icon list (`iconList.json`), so every
  icon there works on Divi 5 (`doc-experiments.md` §4).
- Divi looks the icon up by all three keys and renders nothing if one is missing or doesn't match
  (`IconFont/Utils.php:60-81`). Keep the weight from icons.md: Divi icons are `400`; Font Awesome solid `900`,
  regular and brands `400`.
- `unicode` is the HTML entity text (`&#xf095;`), not the glyph. Canonical escaping stores it as
  `&#xf095;`.
- A blurb shows its icon only with `useIcon: "on"`; a button shows a styled icon with
  `button.decoration.button` → `{"enable": "on", "icon": {"enable": "on", "settings": {…}}}`.

The example under [icon](#icon) above rendered the phone glyph on both the blurb and the button (live check).

## Images

Image leaves hold the URL; the other image facts are sibling keys in the same `innerContent` object:

| key | meaning | notes |
|---|---|---|
| `src` (or `url`) | the image URL | a Media Library URL on the site |
| `alt` | alt text | desktop only; always set it (`W5_NO_ALT`) |
| `titleText` | the `title` attribute | desktop only, optional |
| `linkUrl`, `linkTarget` | make the image a link | `divi/image`, `divi/fullwidth-image` |

- `image.innerContent` `{"src", "alt", "titleText"}` rendered `<img src="…" alt="…" title="…">` on Divi 5.13.1
  (`ModuleElements.php:1403-1416`; live check). Divi's converter moves `alt`/`titleText` into attribute rows
  (`module.decoration.attributes` with `"targetElement": "image"`) when it migrates old content; both forms render,
  and `validate.py` accepts either for `alt`. Write the `innerContent` keys.
- There is no attachment `id` key in Divi 5.13.1's image values (`E5_UNKNOWN_ATTR`); the URL is the reference.
- Blurbs have `imageIcon.innerContent` → `src` and `alt` (with `useIcon` `"off"`, the default); backgrounds use
  `….decoration.background` → `image.url` (with `image.enabled: "on"` in converted content).

## Links

| where | keys | example value |
|---|---|---|
| buttons (`button.innerContent`, `buttonOne`/`buttonTwo` on the fullwidth header) | `text`, `linkUrl`, `linkTarget` (`"on"` = new tab), `rel` (a list) | `{"text": "Call now", "linkUrl": "tel:+13055550100"}` |
| image modules (`image.innerContent`) | `linkUrl`, `linkTarget` | |
| blurb title (`title.innerContent`) | `text`, `url`, `target` | `{"text": "Drain cleaning", "url": "/services/drains/"}` |
| the whole block (`module.advanced.link`, [Link](design-families.md#link) family) | `url`, `target`, `lightbox` | makes the block clickable (`et_clickable`) |
| icon module (`icon.innerContent`) | `url`, `target` next to the icon keys | |

Links in HTML content are ordinary `<a href>` tags. All link values are desktop only.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/blurb {"title":{"innerContent":{"desktop":{"value":{"text":"Drain cleaning","url":"/services/drains/","target":"off"}}}},"imageIcon":{"innerContent":{"desktop":{"value":{"useIcon":"on","icon":{"unicode":"\u0026#xe03b;","type":"divi","weight":"400"}}}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eSame-day.\u003c/p\u003e"}}},"module":{"advanced":{"link":{"desktop":{"value":{"url":"/services/drains/","target":"off"}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/icon {"icon":{"innerContent":{"desktop":{"value":{"unicode":"\u0026#xf095;","type":"fa","weight":"900","url":"tel:+13055550100","target":"off"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Rendered: the blurb's title and icon wrapped in `<a href="/services/drains/">`, the blurb with `et_clickable`, and the
icon module as an `<a href="tel:…">` (live check).

## Value validator codes

| code | level | meaning | fix |
|---|---|---|---|
| `E5_UNKNOWN_ATTR` | error | the block has no such attribute path or key | check the module page; the hint suggests a close match |
| `E5_BAD_BREAKPOINT` | error | a value not wrapped in `{breakpoint: {state: …}}`, an unknown breakpoint, or tablet/phone on a desktop-only leaf | wrap it; use `desktop` for desktop-only leaves |
| `E5_BAD_STATE` | error | a state the leaf doesn't allow | drop it, or use a leaf that has it |
| `E5_BAD_VALUE` | error | the value doesn't fit the leaf type or options | see the type's section above |
| `E5_BAD_VARIABLE` | error | a malformed `$variable(…)$` | follow the reference grammar |
| `W5_BREAKPOINT_DISABLED` | warning | a value for `phoneWide`, `tabletWide`, `widescreen` or `ultraWide` | use `desktop`/`tablet`/`phone` |
| `W5_HOVER_WITHOUT_DESKTOP` | warning | tablet, phone, hover or sticky set without a `desktop.value` | set the desktop value too |
| `W5_UNKNOWN_VARIABLE` | warning | a `gcid-`/`gvid-` id not in `tokens.json` (with `--tokens`) | use an id from the tokens, or a literal |
| `W5_UNKNOWN_PRESET` | warning | a preset id other than `default` not in `tokens.json` | omit `modulePreset`, or use a known id |
| `W5_NO_ALT` | warning | an image module without alt text | set `alt` |
| `W_EXTERNAL_IMAGE` | warning | an image URL on another host (with `--site-url`) | upload it to the site |
| `W_FONT_WEIGHT` | warning | a font weight that isn't 100…900 in steps of 100 | use a hundred |
| `W_OFF_PALETTE_COLOR`, `W_OFF_BRAND_FONT`, `W_OFF_SCALE_SPACING` | warning | with `--tokens`: a literal color, font or spacing value the site doesn't use | use the site's value or its `$variable` |
