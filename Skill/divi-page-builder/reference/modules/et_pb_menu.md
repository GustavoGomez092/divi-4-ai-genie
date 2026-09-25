# Menu — et_pb_menu

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%.et_pb_menu`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_menu _builder_version="4.27.9" _module_preset="default"][/et_pb_menu][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Content — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| menu_id | select | `none` |  | · | Menu |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __menu | computed |  |  | · |  |

### Logo — `image`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| logo | upload | URL |  | R H | Logo |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |
| logo_url | text |  |  | · | Logo Link URL |
| logo_url_new_window | select | `off`, `on` | off | · | Logo Link Target |

### Elements — `elements`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| show_cart_icon | yes_no_button | `on`, `off` | off | R H S | Show Shopping Cart Icon |
| show_cart_quantity | yes_no_button | `on`, `off` | off | · | Show Cart Quantity |
| show_search_icon | yes_no_button | `on`, `off` | off | R H S | Show Search Icon |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

## Design tab

### Layout — `layout`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| menu_style | select | `left_aligned`, `centered`, `inline_centered_logo` | left_aligned | · | Style |
| submenu_direction | select | `downwards`, `upwards` |  | · | Dropdown Menu Direction |

### Menu Text — `menu`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| active_link_color | color-alpha | color |  | R H S | Active Link Color |
| background_layout | select | `dark`, `light` | light | R H S | Text Color |
| text_orientation | text_align | `left`, `center`, `right`, `justified` | left | R | Text Alignment |

### Dropdown Menu — `dropdown`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| dropdown_menu_active_link_color | color-alpha | color |  | H S | Dropdown Menu Active Link Color |
| dropdown_menu_bg_color | color-alpha | color |  | H S | Dropdown Menu Background Color |
| dropdown_menu_line_color | color-alpha | color |  | R H S | Dropdown Menu Line Color |
| dropdown_menu_text_color | color-alpha | color |  | H S | Dropdown Menu Text Color |
| mobile_menu_bg_color | color-alpha | color |  | R H S | Mobile Menu Background Color |
| mobile_menu_text_color | color-alpha | color |  | R H S | Mobile Menu Text Color |

### Sizing — `width`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| logo_height | range |  | auto | R H S | Logo Height |
| logo_max_height | range |  | none | R H S | Logo Max Height |
| logo_max_width | range |  | 100% | R H S | Logo Max Width |
| logo_width | range |  | auto | R H S | Logo Width |

### Icons — `icon_settings`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| cart_icon_color | color-alpha | color | #7EBEC5 | R H S | Shopping Cart Icon Color |
| cart_icon_font_size | range | length: %, em, rem, px, cm, mm… | 17px | R H S | Shopping Cart Icon Font Size |
| menu_icon_color | color-alpha | color | #7EBEC5 | R H S | Hamburger Menu Icon Color |
| menu_icon_font_size | range | length: %, em, rem, px, cm, mm… | 32px | R H S | Hamburger Menu Icon Font Size |
| search_icon_color | color-alpha | color | #7EBEC5 | R H S | Search Icon Color |
| search_icon_font_size | range | length: %, em, rem, px, cm, mm… | 17px | R H S | Search Icon Font Size |

### Logo — `image_settings`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| border_color_all_image | color-alpha | color |  | R H S | Logo Border Color |
| border_color_bottom_image | color-alpha | color |  | R H S | Logo Bottom Border Color |
| border_color_left_image | color-alpha | color |  | R H S | Logo Left Border Color |
| border_color_right_image | color-alpha | color |  | R H S | Logo Right Border Color |
| border_color_top_image | color-alpha | color |  | R H S | Logo Top Border Color |
| border_radii_image | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Logo Rounded Corners |
| border_style_all_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Logo Border Style |
| border_style_bottom_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Logo Bottom Border Style |
| border_style_left_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Logo Left Border Style |
| border_style_right_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Logo Right Border Style |
| border_style_top_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Logo Top Border Style |
| border_styles_image | composite |  |  | · | Logo Border Styles |
| border_width_all_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Logo Border Width |
| border_width_bottom_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Logo Bottom Border Width |
| border_width_left_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Logo Left Border Width |
| border_width_right_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Logo Right Border Width |
| border_width_top_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Logo Top Border Width |
| box_shadow_blur_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Blur Strength |
| box_shadow_color_image | color-alpha | color | rgba(0,0,0,0.3) | R H S | Shadow Color |
| box_shadow_horizontal_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Horizontal Position |
| box_shadow_position_image | select | `outer`, `inner` | depends on `box_shadow_style_image` | R | Box Shadow Position |
| box_shadow_spread_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Spread Strength |
| box_shadow_style_image | select_box_shadow |  | none | · | Logo Box Shadow |
| box_shadow_vertical_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Vertical Position |
| child_filter_blur | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Image Blur |
| child_filter_brightness | range |  | 100% | R H S | Image Brightness |
| child_filter_contrast | range |  | 100% | R H S | Image Contrast |
| child_filter_hue_rotate | range |  | 0deg | R H S | Image Hue |
| child_filter_invert | range |  | 0% | R H S | Image Invert |
| child_filter_opacity | range |  | 100% | R H S | Image Opacity |
| child_filter_saturate | range |  | 100% | R H S | Image Saturation |
| child_filter_sepia | range |  | 0% | R H S | Image Sepia |
| child_mix_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema/et_pb_menu.json) | normal | R H | Image Blend Mode |

### Animation — `animation`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| dropdown_menu_animation | select | `fade`, `expand`, `slide`, `flip` | fade | · | Dropdown Menu Animation |

## Advanced tab

### Attributes — `attributes`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| logo_alt | text |  |  | · | Logo Alt Text |

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_active_menu_link | custom_css |  |  | · | Active Menu Link:<span>.et_pb_menu_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_menu .et-menu-nav li.current-menu-item a</span> |
| custom_css_dropdown_container | custom_css |  |  | · | Dropdown Menu Container:<span>.et_pb_menu_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_menu .et-menu-nav li ul.sub-menu</span> |
| custom_css_dropdown_links | custom_css |  |  | · | Dropdown Menu Links:<span>.et_pb_menu_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_menu .et-menu-nav li ul.sub-menu a</span> |
| custom_css_menu_link | custom_css |  |  | · | Menu Link:<span>.et_pb_menu_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_menu .et-menu-nav li a</span> |
| custom_css_menu_logo | custom_css |  |  | · | Menu Logo:<span>.et_pb_menu_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_menu .et_pb_menu__logo</span> |

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
| Font | `cart_quantity_`, `menu_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
