# What Divi AI produces on Divi 5 (R4)

Research spike, 2026-09-28. Theme: Divi 5.13.1 on `divi-5-test.local`. Live captures are in `../divi-ai-api/divi5/`. Fixtures are in `../../tests/fixtures/divi5/divi-ai/`.

## TL;DR

- **Divi 5 has two AI layout clients.**
  1. **Legacy Divi AI** (`ai-app/`, API **v1**) still powers "Build with AI" in page creation and "Generate section with AI" in the Add Module modal. It uses **the same request bodies as Divi 4** and returns **Divi 4 shortcode**. There is no D5 format flag. The only difference on the wire is `X-Product-Version: 5.13.1`.
  2. **The new AI Agent** (`ai-agent.js`, API **v2**) has a `generate_layout` tool that streams **native D5 block HTML** (`blocksHtml`) from `POST /api/v2/agent/generate-layout`. It authenticates with a **JWT from an interactive elegantthemes.com sign-in popup**, not the username and API key. A probe with `username:api_key` returned `401 Invalid credentials.`, so this path **cannot be replayed headlessly** with the credentials in keys.json.
- **The legacy output is converted on the server.** D5's `root.js` catches the `ai_prompt_use_layout` / `ai_prompt_use_section` events and calls `divi.conversion.convertContent()`, which POSTs to **`/divi/v1/content-conversion`**. There is no TS-only conversion of AI output.
- **That route does more than `convert.php`.** It runs `wp_kses_post` on the D4 input, then `Conversion::maybeConvertContent()`, then the `divi_framework_portability_import_migrated_post_content` filter (D5-to-D5 migrations). It also wraps the result in `<!-- wp:divi/placeholder -->`. `research/tools/divi5/convert.php` skips the kses step, the filter and the wrapper, so its output differs (details below).
- **The fixtures render.** Both fixtures render on D5 with every module accounted for: section 16/16 and layout 89/89 (`et_pb_*` classes, no `et_d4_element` fallbacks, no PHP notices).

## How the D5 AI clients work

### 1. Legacy Divi AI (v1), used by the D5 builder's layout and section generation

| Piece | Where |
|---|---|
| Server URLs, `product_version`, `et_account` | `Divi/ai-app/ai-app.php`: `ET_AI_SERVER_URL = https://ai.elegantthemes.com/api/v1`, `ET_AI_SERVER_URL_V2 = …/api/v2`, `get_ai_app_helpers()` → `window.EtAiAppData` (`product_version => ET_BUILDER_PRODUCT_VERSION` = `5.13.1`) |
| RTK Query API (`generateLayoutShortcode/Content/Images`, `generateSection…`) | `Divi/ai-app/build/et-ai-app.bundle.js` (search `generate-layout/shortcode`). Header `Authorization: Bearer <username>:<apiKey>`, `X-Product-Version`, `maxRetries: 3` |
| 3-stage request builder | same bundle, search `theme_builder_area`. **Byte-for-byte the same body shape as the D4 bundle** (`divi-test` 4.27.9). Only the global rename `et_ai_data` → `EtAiAppData` differs |
| Entry points in D5 | `includes/builder-5/visual-builder/build/app-ui.js` (`pageCreationFlowOnStart === "buildWithAi"` → triggers `et_ai_container_ready` with `{aiMode:"layout", type:"layout_with_ai", contextData:{module:""}}`); `modal-library.js` `loadAISectionModal` → `{aiMode:"section", type:"section_with_ai", contextData:{page: stripHTML(getPageHTML()), ownerId}}` |
| Result handoff | the bundle dispatches `window` event `ai_prompt_use_${layout|section}` with `{layout: <D4 shortcode, image URLs already swapped for local uploads>, design, imageAttributions, ownerId}` |
| D5 consumer | `visual-builder/build/root.js`: layout → `await divi.conversion.convertContent(shortcode)` → `dispatch('divi/edit-post').importContent({content, importOptionsValues:{replaceLayout:'on', …}})`. Section → `convertContent` → wrap as library item `{content, layout_type:'section'}` → `copyModuleFromLibrary(item, 'after', ownerId)` |
| Converter | `visual-builder/build/conversion.js` `convertContent()`: if content starts with a shortcode, `POST /divi/v1/content-conversion {content}`; if it's D5 JSON, `/divi/v1/content-migration` |
| Server route | `includes/builder-5/server/VisualBuilder/REST/ContentConversion/ContentConversionController.php::convert_content` (registered in `RESTRegistration.php`, needs `edit_posts` + `X-ET-Nonce`) |

The D4 AJAX helper `et_ai_shortcode_string_to_object` is still registered, but the D5 section flow never calls it.

Request-shape detail worth knowing: the "Build with AI" flow passes `contextData: {module: ""}`. `page_content: o.page` is therefore `undefined`, and **`page_content` is dropped from the stage-2 body**. The section flow sends the stripped page text (`""` on an empty page). The captures follow both rules.

### 2. AI Agent (v2), native D5

- `includes/builder-5/visual-builder/build/ai-agent.js`, tool `generate_layout` (search `name:"generate_layout"`):
  - `fetch(\`${ai_server_url_v2}/agent/generate-layout\`, {Authorization: Bearer <access_token>, X-Product-Version})`
  - Body: `{prompt, scope: page|section|sections, placement: replace|append, sectionCount:{min,max}, streamProgress:true, model (default "recommended_value"), designContext?, referenceImages?, pageContextImage?, pageContextHtml?}`.
  - Response: an SSE stream of `data:` frames. `generate_layout.progress` frames carry the stages `creating_creative_brief`, `creating_visual_inspiration`, `resolving_stock_photos`, `generating_html_structure` and `fixing_html_structure`. The stream ends with `generate_layout.completed {blocksHtml, ir?, meta?, visualInspirationImageUrl?, stockImages?}` or `generate_layout.error`.
  - `blocksHtml` goes **straight into `importContent`**, with no conversion. After that, `promote_layout_to_global_variables` rebinds literals to the site's global colors and variables.
- Auth: `SU()` returns `lU.access_token`, obtained through `includes/builder-5/server/VisualBuilder/REST/DiviAIAuth/DiviAIAuthService.php`. The broker is `https://www.elegantthemes.com/api_v2/divi-ai/auth` and the sign-in popup is `https://www.elegantthemes.com/members-area/divi-ai/auth/`. The token is a JWT with a `username` claim and a split refresh token, stored per user in user meta. `QU()` sends the old `username:api_key` only to non-`/agent/` v2 paths. The local site has no Divi AI session, and the probe (`00-v2-agent-models-probe.json`, `GET /api/v2/agent/models/text` with API-key auth) got **401 `Invalid credentials.`**.

## What the API returned (v1, replayed as the D5 client sends it)

Brief: "Octavio Lawn and Landscape", primary `#2E7D32`, secondary `#F9A825`, Poppins / Open Sans, heading `#1B2E1C`, body `#4A5A4C`, `images_type: stock_images`.

| Capture | Status | Time | Result |
|---|---|---|---|
| `10-section-1-shortcode` | 200 | 1.3s | 15.9 KB shortcode, `design` echo |
| `10-section-2-content` | 200 | 3.5s | text filled, `imageCount: 1` |
| `10-section-3-images` | 200 | 2.9s | 1 Unsplash image, `images: []`, `eta: 0` |
| `20-layout-1-shortcode` | 200 | 5.8s | 65 KB, 7-section `page_outline` |
| `20-layout-2-content` | 200 | 7.4s | text filled, `imageCount: 10` |
| `20-layout-3-images` | 200 | 3.4s | 7 Unsplash images and 7 attributions. 2 blurbs keep `premadesections.divi.support` images, and the video module keeps the ET placeholder YouTube URL |

The first layout stage-1 attempt timed out at 60s and was retried once. In total 8 API calls were used: 1 v2 probe, 3 section calls, 1 timed-out call and 3 layout calls.

Findings beyond the D4 spike:
- **The outline vocabulary has grown.** It now includes `steps` and `about`: hero, services, features, steps, testimonials, about, call_to_action. The D4 note listed 8 fixed types without these two.
- **The shortcode is still D4 premade templates** (`_builder_version` 4.18–4.25, `_module_preset="default"`). The templates contain AI marker classes `ai_ignore_all` / `ai_ignore_font_icon`, which survive into D5 as `module.decoration.attributes` class rows.
- **Module mix:** section, row, column, heading, text, button, blurb, image, icon, video and cta. The section is 1 section, 2 rows, 3 blurbs and 4 buttons. The layout is 7 sections, 12 rows and 89 blocks.

## Conversion path and the `convert.php` gap

`tests/fixtures/divi5/divi-ai/{section,layout}.html` were produced by the **real route**: `rest_do_request(POST /divi/v1/content-conversion)` as user 1 with a valid `X-ET-Nonce`. That is exactly what `convertContent()` does. The scratch script `convert_rest.php` was not kept in the repo; the recipe is in "Reproduce" below.

A structural diff against `research/tools/divi5/convert.php` on the same input found these differences in the route's output:
- An outer `<!-- wp:divi/placeholder -->` wrapper.
- `builderVersion` is bumped (e.g. `4.24.3` → `5.0.0-public-beta.1`, blurbs and cta → `5.1.1`, structure `alpha.18.2` → `alpha.23`).
- Blurb migrations: `imageIcon.advanced.{alignment,width}` → `imageIcon.decoration.sizing.{alignSelf,width,iconFontSize}`, plus animation defaults. CTA: `button.decoration.button.alignment` → `button.decoration.sizing.alignment`.
- `htmlAttributes.class/id` → `module.decoration.attributes` rows. Image `titleText` → a `title` attribute row.
- `layout.display: block` is added to every module.
- **kses side effects:** `&` → `&amp;` in text innerContent (renders correctly as a single `&amp;`, with no double escape) and in image URLs.

**Recommendation:** to match the builder, `convert.php` should also apply `apply_filters('divi_framework_portability_import_migrated_post_content', …)`, and ideally `wp_kses_post` on the input. Otherwise its fixtures carry pre-migration attribute shapes.

The builder then runs `importContent` and later saves through its TS serializer, which may normalize further. That step can't be observed headlessly, so the fixtures are **"what the builder receives from the server"**, not "what ends up in post_content after Save".

## Render verification

Each fixture was created as a draft page ("R4 Divi AI section" / "R4 Divi AI layout", `_et_pb_use_builder=on`) with `wp post create --user=1`, then briefly published, curled twice, and **deleted** (ids 53 and 55).

| Fixture | HTTP | Blocks | Rendered `et_pb_*` modules | `et_d4_element` | debug.log |
|---|---|---|---|---|---|
| section | 200 | 16 | 16 (5 column, 4 button, 3 blurb, 2 row, 1 section, 1 heading) | 0 | 0 new lines |
| layout | 200 | 89 | 89 (20 column, 16 heading, 12 row, 11 text, 9 button, 7 section, 5 image, 5 blurb, 2 icon, 1 video, 1 cta) | 0 | 0 new lines |

Fonts and colors reach the page: Poppins appears 34 times and `#2E7D32` is present in the layout CSS. Headings read e.g. "A Better-Looking Property Starts Here" and "Complete Lawn &amp; Landscape Services". The theme sidebar (Archives / Categories) also rendered, so page-layout meta matters on D5 pages as well.

## Implications for Divi Genie on D5

1. **Divi AI output isn't a D5-native design reference** unless it comes from the v2 agent. The v1 path is D4 premades run through the same converter we already use, so fixtures from it test our converter parity, not "how D5 wants layouts authored".
2. **Match the builder's conversion pipeline**, not bare `maybeConvertContent`: kses on the input, then convert, then the migration filter, then the placeholder wrapper. Otherwise attributes like the blurb icon alignment and width sit in pre-5.1 locations that D5 migrates on import anyway.
3. **The v2 agent is the real D5-native generator.** It emits block HTML directly, takes a `designContext` (tokens, presets, global colors and variables) and rebinds literals to globals after import. That validates the skill's direction of using site tokens and globals rather than inline literals. Capturing its output needs an interactive ET sign-in in the browser; recording the SSE stream from the VB's network panel would be the way to get a v2 fixture.
4. **The 6 design inputs are still all v1 knows**, same as on D4. Images still need sideloading, and the v1 client does it before handing off, so production content has local URLs. Our fixtures keep the Unsplash URLs.

## Files

- `research/divi-ai-api/divi5/00-v2-agent-models-probe.json`: the v2 auth probe (401).
- `research/divi-ai-api/divi5/10-section-{1-shortcode,2-content,3-images}.json` and `20-layout-{…}.json`: request (headers shown with placeholders) and response per stage. Scrubbed to `<ET_USERNAME>` / `<API_KEY>`, and a scan confirmed neither value appears.
- `tests/fixtures/divi5/divi-ai/section.txt`, `layout.txt`: raw final D4 shortcode (stage 3).
- `tests/fixtures/divi5/divi-ai/section.html`, `layout.html`: D5 content as returned by `/divi/v1/content-conversion`.

## Reproduce

The replay script lived in the session scratchpad, so rewrite it from this doc. It loads credentials via `wp_keys.resolve_et_credentials` and posts the bodies shown in the captures to `https://ai.elegantthemes.com/api/v1/generate-{section,layout}/{shortcode,content,images}` with `X-Product-Version: 5.13.1`. Convert with the route: `rest_do_request` on `POST /divi/v1/content-conversion` with header `X-ET-Nonce: wp_create_nonce(RESTController::get_nonce_name('divi/v1','/content-conversion','POST'))`, run as `--user=1`.
