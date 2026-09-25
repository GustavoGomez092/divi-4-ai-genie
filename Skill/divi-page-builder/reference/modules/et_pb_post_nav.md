# Post Navigation — et_pb_post_nav

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `.et_pb_posts_nav%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_post_nav _builder_version="4.27.9" _module_preset="default"][/et_pb_post_nav][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Categories — `categories`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| in_same_term | yes_no_button | `off`, `on` |  | · | Navigate Within Current Category |
| taxonomy_name | text |  |  | · | Custom Taxonomy Name |

### Navigation — `navigation`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| show_next | yes_no_button | `on`, `off` | on | R H | Show Next Post Link |
| show_prev | yes_no_button | `on`, `off` | on | R H | Show Previous Post Link |

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| next_text | text |  |  | R H | Next Link |
| prev_text | text |  |  | R H | Previous Link |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __posts_navigation | computed |  |  | · |  |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_links | custom_css |  |  | · | Links:<span>.et_pb_posts_nav.et_pb_post_nav_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> span a</span> |
| custom_css_next_link | custom_css |  |  | · | Next Link:<span>.et_pb_posts_nav.et_pb_post_nav_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> span.nav-next a</span> |
| custom_css_next_link_arrow | custom_css |  |  | · | Next Link Arrow:<span>.et_pb_posts_nav.et_pb_post_nav_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> span.nav-next .meta-nav</span> |
| custom_css_prev_link | custom_css |  |  | · | Previous Link:<span>.et_pb_posts_nav.et_pb_post_nav_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> span.nav-previous a</span> |
| custom_css_prev_link_arrow | custom_css |  |  | · | Previous Link Arrow:<span>.et_pb_posts_nav.et_pb_post_nav_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> span.nav-previous .meta-nav</span> |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Animation | (none) | [design-families.md#animation](../design-families.md#animation) |
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Border | (none) | [design-families.md#border](../design-families.md#border) |
| Box shadow | (none) | [design-families.md#box-shadow](../design-families.md#box-shadow) |
| CSS ID & classes | (none) | [design-families.md#css-id-and-classes](../design-families.md#css-id-and-classes) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Font | `title_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Font (`title_`): `title_text_align`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
