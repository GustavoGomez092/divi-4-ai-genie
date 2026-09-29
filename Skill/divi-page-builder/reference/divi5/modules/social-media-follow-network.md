# Social Network — divi/social-media-follow-network

A single social-network icon inside a Social Media Follow module.

- **Block:** `divi/social-media-follow-network` (Divi 4: `et_pb_social_media_follow_network`)
- **Category:** child-module · **scope:** core
- **Goes inside:** `divi/social-media-follow`
- **Children:** none
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `followButton` (Follow Button), `freeForm`, `mainElement`, `socialIcon` (Social Icon)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/social-media-follow {"builderVersion":"5.13.1"} --><!-- wp:divi/social-media-follow-network {"socialNetwork":{"innerContent":{"desktop":{"value":{"title":"facebook","label":"facebook","link":"https://facebook.com/example"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/social-media-follow --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/social-media-follow-network` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "socialNetwork": {
    "innerContent": {
      "desktop": {
        "value": {
          "title": "facebook",
          "label": "facebook",
          "link": "https://facebook.com/example"
        }
      }
    }
  },
  "builderVersion": "5.13.1"
}
```

**Reading the tables.** `attribute` is the dotted path to a responsive object in the block's JSON; `key` is the key inside its value (`—` = the value itself). So `title.innerContent` + key `text` is written `"title":{"innerContent":{"desktop":{"value":{"text":"…"}}}}`. **R** = responsive (a value per breakpoint: `desktop`, `tablet`, `phone`); `desktop` = desktop only. **states** = states allowed besides `value` (e.g. `hover`, `sticky`). Type grammars: [design-families.md#leaf-types](../design-families.md#leaf-types); the full value model: [value-formats.md](../value-formats.md).

## Content

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `button.innerContent` | `linkTarget` | enum | `on`, `off` | desktop | · | D4 `url_new_window` |
| `button.innerContent` | `linkUrl` | url |  | desktop | · | D4 `button_url` |
| `button.innerContent` | `rel` | enum | list of: `bookmark`, `external`, `nofollow`, `noreferrer`, `noopener` | desktop | · | D4 `button_rel` |
| `button.innerContent` | `text` | text |  | R | hover, sticky | D4 `button_text` |
| `socialNetwork.innerContent` | `label` | text |  | desktop | · | D4 `content` |
| `socialNetwork.innerContent` | `link` | url |  | desktop | · | D4 `url` |
| `socialNetwork.innerContent` | `skypeAction` | enum | `call`, `chat` | desktop | · | D4 `skype_action` |
| `socialNetwork.innerContent` | `skypeUrl` | text |  | desktop | · | D4 `skype_url` |
| `socialNetwork.innerContent` | `title` | text |  | desktop | · | D4 `social_network` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `button.decoration.background` | [Background](../design-families.md#background) |
| `button.decoration.border` | [Border](../design-families.md#border) |
| `button.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `button.decoration.button` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.background` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.border` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.boxShadow` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.button` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.font` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.textEffects` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.textShadow` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.sizing` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.spacing` | [Button](../design-families.md#button) |
| `button.decoration.button.innerContent` | [Button](../design-families.md#button) |
| `button.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `button.decoration.font.font`, not here |
| `button.decoration.font.font` | [Font](../design-families.md#font) |
| `button.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `button.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `button.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `module.decoration.animation` | [Animation](../design-families.md#animation) |
| `module.decoration.attributes` | [Attributes](../design-families.md#attributes) |
| `module.decoration.background` | [Background](../design-families.md#background) |
| `module.decoration.border` | [Border](../design-families.md#border) |
| `module.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `module.decoration.conditions` | [Conditions](../design-families.md#conditions) |
| `module.decoration.disabledOn` | [Disabled on](../design-families.md#disabled-on) |
| `module.decoration.filters` | [Filters](../design-families.md#filters) |
| `module.decoration.interactions` | [Interactions](../design-families.md#interactions) |
| `module.decoration.layout` | [Layout](../design-families.md#layout) |
| `module.decoration.overflow` | [Overflow](../design-families.md#overflow) |
| `module.decoration.position` | [Position](../design-families.md#position) |
| `module.decoration.scroll` | [Scroll](../design-families.md#scroll) |
| `module.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `module.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `module.decoration.transform` | [Transform](../design-families.md#transform) |
| `module.decoration.transition` | [Transition](../design-families.md#transition) |
| `module.decoration.zIndex` | [Z-index](../design-families.md#z-index) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `icon.advanced.color` | — | color |  | R | hover, sticky | D4 `icon_color` |
| `icon.advanced.size` | `size` | length |  | R | hover, sticky | D4 `icon_font_size` |
| `icon.advanced.size` | `useSize` | onoff |  | R | hover | D4 `use_icon_font_size` |
| `socialNetwork.advanced.followButton` | — | onoff |  | R | hover, sticky | D4 `follow_button` |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.elements.structure` | [Elements](../design-families.md#elements) |
| `module.advanced.html` | [Html](../design-families.md#html) |
| `module.advanced.loop` | [Loop](../design-families.md#loop) |
| `module.advanced.text` | [Text](../design-families.md#text) |
| `module.advanced.text.text` | [Text](../design-families.md#text) |
| `module.advanced.text.textShadow` | [Text](../design-families.md#text) |

## Meta and block-level attributes

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `adminLabel` | — | text |  | desktop | · |  |
| `css` | `after` | text |  | R | hover, sticky | D4 `custom_css_after` |
| `css` | `before` | text |  | R | hover, sticky | D4 `custom_css_before` |
| `css` | `followButton` | text |  | R | hover, sticky | D4 `custom_css_follow_button` |
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `css` | `socialIcon` | text |  | R | hover, sticky | D4 `custom_css_social_icon` |
| `globalColorsInfo` | — | json |  | desktop | · | D4 global_colors_info (Conversion::getAttrMap) |
| `locked` | — | onoff |  | desktop | · |  |
| `on` | — | json |  | desktop | · | block-level attr from Conversion::getAttrMap; value shape not documented |
| `open` | — | onoff |  | desktop | · |  |
| `themeBuilderArea` | — | json |  | desktop | · | theme-builder area marker (Conversion::getAttrMap) |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.meta.adminLabel` | [Admin label](../design-families.md#admin-label) |
| `module.meta.meta.forceVisible` | [Meta](../design-families.md#meta) |
| `module.meta.meta.tocListHeading` | [Meta](../design-families.md#meta) |

<details>
<summary>Render defaults (3): what Divi uses when an attribute is unset — don't repeat these</summary>

- `icon.advanced.size` — desktop `{"size":"16px","useSize":"off"}`
- `module.advanced.html` — desktop `{"elementType":"li"}`
- `socialNetwork.innerContent` — desktop `{"label":"Facebook","skypeAction":"call","skypeUrl":"","title":"facebook"}`

</details>
