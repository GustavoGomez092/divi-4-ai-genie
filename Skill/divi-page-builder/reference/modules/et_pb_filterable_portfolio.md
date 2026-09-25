# Filterable Portfolio — et_pb_filterable_portfolio

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%.et_pb_filterable_portfolio`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_filterable_portfolio _builder_version="4.27.9" _module_preset="default"][/et_pb_filterable_portfolio][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Content — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| include_categories | categories |  |  | · | Included Categories |
| posts_number | text |  | 10 | · | Post Count |

### Elements — `elements`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| show_categories | yes_no_button | `on`, `off` | on | R H | Show Categories |
| show_pagination | yes_no_button | `on`, `off` | on | R H | Show Pagination |
| show_title | yes_no_button | `on`, `off` | on | R H | Show Title |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __project_terms | computed |  |  | · |  |
| __projects | computed |  |  | · |  |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |

## Design tab

### Layout — `layout`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| fullwidth | select | `on`, `off` | on | · | Layout |

### Overlay — `overlay`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| hover_icon | select_icon | icon string |  | S | Hover Icon Picker |
| hover_overlay_color | color-alpha | color | rgba(255,255,255,0.9) | S | Hover Overlay Color |
| zoom_icon_color | color-alpha | color |  | S | Zoom Icon Color |

### Title Text — `title`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| title_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | h2 | · | Title Heading Level |

### Image — `image`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| border_color_all_image | color-alpha | color |  | R H S | Image Border Color |
| border_color_bottom_image | color-alpha | color |  | R H S | Image Bottom Border Color |
| border_color_left_image | color-alpha | color |  | R H S | Image Left Border Color |
| border_color_right_image | color-alpha | color |  | R H S | Image Right Border Color |
| border_color_top_image | color-alpha | color |  | R H S | Image Top Border Color |
| border_radii_image | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Image Rounded Corners |
| border_style_all_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Border Style |
| border_style_bottom_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Bottom Border Style |
| border_style_left_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Left Border Style |
| border_style_right_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Right Border Style |
| border_style_top_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Top Border Style |
| border_styles_image | composite |  |  | · | Image Border Styles |
| border_width_all_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Border Width |
| border_width_bottom_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Bottom Border Width |
| border_width_left_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Left Border Width |
| border_width_right_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Right Border Width |
| border_width_top_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Top Border Width |
| box_shadow_blur_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Blur Strength |
| box_shadow_color_image | color-alpha | color | rgba(0,0,0,0.3) | R H S | Shadow Color |
| box_shadow_horizontal_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Horizontal Position |
| box_shadow_position_image | select | `outer`, `inner` | depends on `box_shadow_style_image` | R | Box Shadow Position |
| box_shadow_spread_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Spread Strength |
| box_shadow_style_image | select_box_shadow |  | none | · | Image Box Shadow |
| box_shadow_vertical_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Vertical Position |
| child_filter_blur | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Image Blur |
| child_filter_brightness | range |  | 100% | R H S | Image Brightness |
| child_filter_contrast | range |  | 100% | R H S | Image Contrast |
| child_filter_hue_rotate | range |  | 0deg | R H S | Image Hue |
| child_filter_invert | range |  | 0% | R H S | Image Invert |
| child_filter_opacity | range |  | 100% | R H S | Image Opacity |
| child_filter_saturate | range |  | 100% | R H S | Image Saturation |
| child_filter_sepia | range |  | 0% | R H S | Image Sepia |
| child_mix_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema/et_pb_filterable_portfolio.json) | normal | R H | Image Blend Mode |

## Advanced tab

### Scroll Effects — `scroll_effects`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| enable_grid_motion | yes_no_button | `off`, `on` | off | · | Apply Motion Effects To Child Elements |

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_active_portfolio_filter | custom_css |  |  | · | Active Portfolio Filter:<span>.et_pb_filterable_portfolio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_filterable_portfolio.et_pb_filterable_portfolio .et_pb_portfolio_filters li a.active</span> |
| custom_css_overlay | custom_css |  |  | · | Overlay:<span>.et_pb_filterable_portfolio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_filterable_portfolio .et_overlay</span> |
| custom_css_overlay_icon | custom_css |  |  | · | Overlay Icon:<span>.et_pb_filterable_portfolio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_filterable_portfolio .et_overlay:before</span> |
| custom_css_portfolio_filters | custom_css |  |  | · | Portfolio Filters:<span>.et_pb_filterable_portfolio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_filterable_portfolio.et_pb_filterable_portfolio .et_pb_portfolio_filters</span> |
| custom_css_portfolio_image | custom_css |  |  | · | Portfolio Image:<span>.et_pb_filterable_portfolio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_filterable_portfolio .et_portfolio_image</span> |
| custom_css_portfolio_pagination | custom_css |  |  | · | Portfolio Pagination:<span>.et_pb_filterable_portfolio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_filterable_portfolio .et_pb_portofolio_pagination</span> |
| custom_css_portfolio_pagination_active | custom_css |  |  | · | Pagination Active Page:<span>.et_pb_filterable_portfolio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_filterable_portfolio .et_pb_portofolio_pagination a.active</span> |
| custom_css_portfolio_post_meta | custom_css |  |  | · | Portfolio Post Meta:<span>.et_pb_filterable_portfolio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_filterable_portfolio .et_pb_portfolio_item .post-meta</span> |
| custom_css_portfolio_title | custom_css |  |  | · | Portfolio Title:<span>.et_pb_filterable_portfolio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_filterable_portfolio .et_pb_portfolio_item h2</span> |

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
| Font | `caption_`, `filter_`, `pagination_`, `title_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Font (`filter_`): `filter_text_align`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
