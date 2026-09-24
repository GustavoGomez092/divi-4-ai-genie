# How Divi AI Builds Pages (Divi 4.27.9)

Research spike, 2026-09-24. Sources: theme source in `~/Local Sites/divi-test` plus live API replays saved in `divi-ai-api/`.

## TL;DR

- **Nothing is extractable client-side.** Prompts, model and provider all live on `https://ai.elegantthemes.com/api/v1`. The theme ships only a React client (`Divi/ai-app/`) with no prompts, model names or provider references.
- **Divi AI is a premade-section library plus slot filling, not a layout designer.** It picks premade sections, injects 6 design values into their attributes, then an LLM rewrites only the text slots and a stock-photo search fills the image slots.
- **The output is plain Divi 4 shortcode.** Pushing that shortcode into `post_content` (with `_et_pb_use_builder=on`) renders a fully styled Divi page. Verified on the local site.

## The API

Base: `https://ai.elegantthemes.com/api/v1/`. Headers: `Authorization: Bearer <ET username>:<ET API key>` and `X-Product-Version: <Divi version>`.

| Endpoint | Purpose |
|---|---|
| `GET user` | Subscription status (`{"remainingRequests":-69,"subscription":"active"}`) |
| `POST generate-layout/{shortcode,content,images}` | Full page, 3 stages |
| `POST generate-section/{shortcode,content,images}` | Single section, 3 stages |
| `POST generate-text`, `refine-text` | Module text fields |
| `POST generate-module`, `refine-module` | Whole-module content |
| `POST generate-code`, `refine-code` | Custom CSS/code |
| `POST generate-image`, `refine-image`, `upscale-image`, `autogenerate-image`, `inpainting/*`, `outpainting`, `enhance` | Image generation and editing |

## The 3-stage page pipeline (`useAIRequest` in `ai-app/build/et-ai-app.bundle.js`)

| Stage | Request fields | Response | Time |
|---|---|---|---|
| 1. `…/shortcode` | `prompt`, `site_name`, `site_description`, `additional_description`, `page_name`, `post_type`, `theme_builder_area`, `has_woocommerce`, `primary_color`, `secondary_color`, `heading_font`, `body_font`, `heading_font_color`, `body_font_color` | `content` (shortcode with placeholder text), `page_outline` (layout only), `design` (echo of the 6 design values) | 2s section / 7s page |
| 2. `…/content` | stage-1 `shortcode` + `page_outline` + `page_content` (existing page text) + brief | `content` (same shortcode, text slots filled), `imageCount` | 4s / 11s |
| 3. `…/images` | filled shortcode + outline + brand colors + `images_type` (`stock_images` / `ai_images` / `placeholder_images`) | `content` (image URLs + icons swapped), `images`, `upscale`, `attributions`, `eta` | 3s / 5s |

The client then downloads every returned image URL into the Media Library (`et_ai_upload_image` AJAX, which re-encodes to JPEG at 80% quality) and swaps the local URLs in. The builder wraps the final shortcode as Divi portability JSON `{"context":"et_builder","data":{"1":"<shortcode>"}}` and runs the standard **Import Layout** flow (`onUseAILayout` in `frontend-builder/build/bundle.js`). Sections instead go through `et_ai_shortcode_string_to_object` (which calls `et_fb_process_shortcode`) and `insertSavedModule`.

### What each stage actually changes (diffed from the live responses)

- **Stage 1 (full page) runs an LLM planner.** It writes a `page_outline` choosing from a fixed vocabulary of section types: `hero`, `services`, `features`, `statistics`, `listings`, `testimonials`, `frequently_asked_questions`, `call_to_action`. Each type gets a `section_description` explaining what the copy should say. One premade section is retrieved per type (image URLs point to `premadesections.divi.support`). Fonts and colors are injected straight into module attributes (e.g. `title_font="Poppins|Poppins_weight|||||||"`, `title_text_color="#0B2A3C"`). Text is placeholder copy: "Services Heading", "Service Name", "Service Short Description".
- **Stage 2 only touches text slots.** It changes `title=`, `admin_label=` and the inner HTML of text-bearing modules. Module count, order and every style attribute stay identical.
- **Stage 3 only touches image and icon slots.** It sets `background_image` / `src` to Unsplash URLs found by search, and picks a relevant `font_icon` per blurb (e.g. `&#xf62f;||fa||900`).

### Design inputs are coarse

Divi AI only knows **6 values**: primary color, secondary color, heading font, body font, heading color and body color. It never reads the existing site's spacing, section or row styles, button styles or module presets, which is why its output often doesn't match a site's look. Our skill should derive a far richer token set from a site's existing pages.

## How Divi stores a page

- `post_content` holds the whole page as nested shortcodes: `[et_pb_section][et_pb_row][et_pb_column type="…"][et_pb_<module> …]inner[/et_pb_<module>]…`.
- Post meta: `_et_pb_use_builder=on` (required), `_et_pb_built_for_post_type=page`, `_et_pb_page_layout` (e.g. `et_no_sidebar`, `et_full_width_page`), and `_et_pb_old_content` (the pre-Divi content).
- The builder's own save (`et_fb_ajax_save` in `includes/builder/functions.php`) converts builder state to shortcode with `et_fb_process_to_shortcode()` and then calls `wp_update_post()`. There is no hidden format: **writing the shortcode is equivalent to saving from the builder.**
- Per-page CSS is generated on first view into `wp-content/et-cache/<post_id>/`. The very first request after a change can render unstyled (dynamic CSS deferred), so a push should warm or clear that cache. `wp_update_post` fires `save_post`, which Divi hooks to clear it.

## Push test (local)

Page 11 on `divi-test.local` ("Probe: Divi AI Emergency Plumber") was created with WP-CLI from the stage-3 shortcode plus the meta above. It renders with correct fonts, colors and layout across all 8 sections, **even though its 23 `_module_preset` UUIDs don't exist on the site**. The premade templates inline every style, so presets were never needed.

## Implications for our skill

1. **Copy the architecture, not the service.** Our version would be a section library, then slot filling, then a push, with one key difference: the library comes from **the client site's own existing sections** (or sections restyled with that site's tokens) instead of Elegant Themes' generic premades.
2. **Inline all styles and avoid preset UUIDs.** That keeps generated pages portable and immune to missing presets, exactly like Divi AI's templates.
3. **Keep structure and copy separate.** Pick or compose the structure first, then fill text slots, then image slots. Each step is independently verifiable, and diffs show only intended changes.
4. **Pushing is trivial**: `post_content` = shortcode, `_et_pb_use_builder=on`, then trigger `save_post` so the CSS cache refreshes. The builder's Import Layout JSON format is an alternative for manual imports.
5. **Images need a sideload step**, as Divi AI does: download the image, upload it to the Media Library and use the local URL. Never hotlink.

## Files

- `divi-ai-api/00-user.json`: subscription check
- `divi-ai-api/10-section-{1-shortcode,2-content,3-images}.json`: dental services section
- `divi-ai-api/20-layout-{1-shortcode,2-content,3-images}.json`: emergency plumber landing page

Credentials are scrubbed to `<ET_USERNAME>` / `<API_KEY>`.
