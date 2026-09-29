# Publishing over REST

**Before any command here writes to a site** (`media`, `draft`, `publish`), the user must have approved
the page in the local preview (`preview.py`, SKILL.md step 7). Images and drafts are changes to the
client's site, so nothing is uploaded just to look at a page.

## Credentials: keys.json

`publish.py` and `extract_tokens.py` (online mode) can read credentials for any number of sites
from a `keys.json` file instead of separate `--site`/`--user`/`WP_APP_PASSWORD` per site:

```json
{
  "keys": [
    {"name": "Test Key Local site", "site": "http://divi-test.local", "user": "user",
     "key": "xxxx xxxx xxxx xxxx xxxx xxxx"},
    {"name": "Client A", "site": "https://client-a.com", "user": "seo-bot",
     "key": "xxxx xxxx xxxx xxxx xxxx xxxx"}
  ]
}
```

Every entry needs `name`, `site`, `user` and `key` (each a non-empty string; `key` is the
Application Password). **Location**, in order of precedence: the `--keys PATH` flag, the env var
`DIVI_KEYS_FILE`, then the default `~/.config/divi-page-builder/keys.json`. Whichever path is
used, `chmod 600` it and **never commit it, and never put it inside this skill or any repo** —
it lives only in that one file on disk, outside version control.

**Selecting a key:**
- `--key "Client A"` picks that entry by name (case-insensitive).
- Without `--key`, passing `--site` alone matches it (normalized: scheme+host lowercased, a
  trailing slash stripped) against every entry's `site`; add `--user` to disambiguate when more
  than one entry matches the same site (a client and a local test copy, say).
- **Env fallback (backward compatible):** with no `--key` and no site match, `--site`/`--user`
  plus env `WP_APP_PASSWORD` still work exactly as before — no `keys.json` required.
- `python3 scripts/publish.py keys [--keys PATH]` lists every entry's `name`/`site`/`user` (never
  the key) — use it to see what's already configured before asking the user for a new one.

When you're done with a key, revoke it on the site's own profile screen: **Users → Profile →
Application Passwords**.

The same `keys.json` may also hold an optional top-level `elegant_themes` section (`{"username":
"...", "api_key": "..."}`), used for the local preview's Divi download — see `reference/preview.md`.
`publish.py keys` reports it too: `{"username": "...", "configured": true}`, or `{"configured":
false}` when the section is absent, and never the `api_key`.

## Using publish.py

`scripts/publish.py` wraps the REST flow below into five commands. It handles Divi 5 (block) pages
too, with a different save sequence and extra refusals: see "Divi 5" below. Credentials come from either
a `keys.json` file (`--key NAME`) or, for backward compatibility, `--site`/`--user` plus env
`WP_APP_PASSWORD` — see "Credentials: keys.json" below. Never a flag, never printed.

```bash
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

# 0. List the sites this skill has credentials for (never prints a key value)
python3 scripts/publish.py keys

# 1. Fetch the current content.raw before editing an existing page
python3 scripts/publish.py fetch --key "Client A" --page-id 15 --out original.txt

# 2. Upload one image directly (rarely needed — draft uploads local images automatically)
python3 scripts/publish.py media --key "Client A" hero.jpg --alt "Plumber repairing a burst pipe"

# 3. Draft-first: validates the page, uploads any local images, and creates/updates a draft
python3 scripts/publish.py draft page.txt --key "Client A" --title "Emergency Plumber in Miami"

# updating an existing page keeps it a draft (does not publish)
python3 scripts/publish.py draft page.txt --key "Client A" --title "..." --page-id 15

# full-bleed landing page: strip header/nav/footer via the one REST-settable layout field
python3 scripts/publish.py draft page.txt --key "Client A" --title "..." \
  --page-fields '{"template":"page-template-blank.php"}'

# 4. Publish only after the user has reviewed the draft's preview_url and approved it
python3 scripts/publish.py publish --key "Client A" --page-id 15 --yes

# 5. Editing a page that is ALREADY published/scheduled/private: see "Editing a live page" below —
#    draft --page-id refuses this case, so review a copy first, then apply with publish --content
#    (keeps the page's visibility: private stays private, scheduled stays scheduled)
python3 scripts/publish.py publish --key "Client A" --page-id 15 --content page.txt --yes

# 6. Only when the user explicitly wants a private/scheduled page's status changed to publish
python3 scripts/publish.py publish --key "Client A" --page-id 15 --status publish --yes

# Without a keys.json entry, --site/--user plus WP_APP_PASSWORD still work exactly as before:
python3 scripts/publish.py fetch --site "$SITE" --user "$WP_USER" --page-id 15 --out original.txt
```

**Draft-first, always.** `draft` never publishes — the page is created or updated with
`status: draft` regardless of whether it's new or existing. `publish` is a separate,
explicit step that flips `status` to `publish`, and it refuses (exit 1, no HTTP call) unless
`--yes` is given. Only pass `--yes` after the user has looked at the draft's `preview_url`
(from `draft`'s JSON output) and approved it — never as a default or automatic follow-up to
`draft`.

**Visibility is never changed by accident.** `publish --page-id ID` first reads the page
(`GET /pages/ID?context=edit`). If it is `private` or `future` (scheduled), `publish --content`
sends only `content` and `meta`, so the page stays private or keeps its scheduled date, and
`publish` without `--content` refuses (exit 1) because the only thing it could do is change
the visibility. Pass `--status publish` only when the user explicitly asks to make that page
public (a scheduled page whose date is still in the future stays scheduled in WordPress until
that date, or until its date is changed). A `draft`/`pending` page is published (`status: "publish"`), and a `publish` page
stays `publish`.

**Editing a live page.** `draft --page-id ID` first fetches the page's current `status`
(`GET /pages/ID?context=edit`) and refuses (exit 1, no update) if it is `publish`, `future`,
or `private` — forcing a live page back to `draft` would take it offline for site visitors
while it's being reviewed. It proceeds normally for a page whose status is `draft` or
`pending`. To edit a page that's already live:

1. Create a **review copy** as a new draft (no `--page-id`), and share its `preview_url` for
   approval: `publish.py draft page.txt --baseline original.txt --site "$SITE" --user "$WP_USER" --title "..."`
   (`--baseline` = the live page's content you fetched in step 1 of the workflow, so errors
   already on a legacy page don't block the review copy)
2. Once approved, apply the edit to the live page **and** publish it in one request with
   `publish`'s optional `--content`:
   ```bash
   python3 scripts/publish.py publish --site "$SITE" --user "$WP_USER" --page-id 15 \
     --content page.txt --yes
   ```
   This reads the page, validates `page.txt` against the page's current content as the
   baseline (refusing on new errors, exit 1, nothing written), uploads any local images the
   same way `draft` does, then sends `content` and `meta._et_pb_use_builder: "on"` to
   `/pages/15` in a single `POST` — plus `status: "publish"` unless the page is `private` or
   `future`, whose visibility is kept. The page is never left in a `draft` state in between.
   `--yes` is still required.
3. **Delete the review copy** once the edit is live, so a stale duplicate draft doesn't linger
   in Pages → Drafts: `curl -s -X DELETE -u "$WP_USER:$WP_APP_PASSWORD"
   "$SITE/wp-json/wp/v2/pages/REVIEW_ID?force=true"` (`REVIEW_ID` is the `id` that step 1's
   `draft` printed; `force=true` deletes it permanently). Without `?force=true` the REST DELETE
   moves it to Trash instead, which is also fine — WordPress empties Trash after 30 days.

**Local images.** Reference images in the page source as `./images/hero.jpg`, `../hero.jpg`,
or `file:///abs/path.jpg` (paths resolved relative to the page file's own folder, or absolute
for `file://`) instead of a live URL. `draft` finds every image attribute
(`divi_checks_values.IMAGE_ATTRS`, plus anything ending `_image`) with such a value, uploads
the file to the Media Library, sets `alt_text` from the module's `alt`/`title_text` attribute,
and rewrites the attribute to the returned `source_url` before creating/updating the page.
Each distinct local file is uploaded once even if referenced by multiple modules; the JSON
output's `uploaded` array lists every file that was uploaded (`id`, `url`, `file`). Preview these
first with `preview.py` (render embeds them, serve routes them — see `reference/preview.md`'s
"Local images") so you can check the page before anything is uploaded.

**`--page-fields`** takes a JSON object merged into the page body, for fields not covered by
the standard flags — most commonly the layout template found in Task 10's REST experiments:
`--page-fields '{"template":"page-template-blank.php"}'` removes the site's header, primary
nav, and footer chrome for a true full-bleed landing page. No sidebar is Divi's own default
for any builder-active page (`meta._et_pb_use_builder: "on"`) — nothing needs to be set for
that. `--page-fields` must be a JSON object and may not set `status`, `content`, or `meta` —
those are owned by `draft`/`publish` themselves (setting `status` there, for example, would
silently bypass the `--yes` approval gate); such a value is a usage error (exit 2, no HTTP
calls), not a validation error.

**Validation.** `draft` (and `publish --content`) run `validate_source` before uploading or
writing anything and refuse (exit 1 — no uploads, no draft/publish) if there are any blocking
errors, printing each finding to stderr the same way `validate.py` does. Like
`validate.py --baseline`, they validate against a **baseline**: `--baseline original.txt` if
given, otherwise — whenever `--page-id` is given — the page's current `content.raw` (read with
`GET /pages/ID?context=edit`, the only REST call made before validation; the Divi version check
also fetches the theme's public `style.css`, see "Divi 5"). Errors already present
in the baseline (for example a Divi 3 `use_border_color` on a legacy page, `E_UNKNOWN_ATTR`)
are pre-existing and don't block; any new error still does. A brand-new page (`draft` without
`--page-id` or `--baseline`) has no baseline, so every error blocks. Local image
paths are all resolved and checked for existence up front, before any is uploaded, so one
missing image never leaves an earlier one uploaded as an orphan (exit 2, zero media uploads).

**Exit codes:** `0` success · `1` validation errors, `publish` without `--yes`, `draft
--page-id` refusing to unpublish a live page, or `publish` without `--content` refusing to
change a private/scheduled page's visibility · `2` usage error (including a missing
`WP_APP_PASSWORD`, a malformed `--page-fields`, or a missing local image), HTTP error, or I/O
error. HTTP error messages include only the method/path and WordPress's own `code`/`message`
— never the password or a full URL with credentials.

## Divi 5

Everything above describes Divi 4 pages. `publish.py` handles Divi 5 pages with the same commands and the same
approval rules (preview first, draft first, `publish --yes` only after approval). What differs is below. Evidence:
`storage-and-serialization.md` §2.2-2.4 and its "Addendum" (research, repo only), re-verified on the local Divi 5
site (WordPress 7.1.2, Divi 5.13.1) by `tests/test_divi5_publish_live.py`.

### Detection and refusals

`draft` and `publish --content` look at two things before any REST request:

- **The page file's format** (`divi_format.detect_content`): `[et_pb_…` shortcode is Divi 4, `<!-- wp:divi/…`
  blocks are Divi 5. Mixed content fails validation.
- **The site's Divi major version**: `tokens.json` `site.divi_major` (or `site.divi_version`) when `draft --tokens`
  is given, otherwise `divi_format.detect_site` (the theme's `style.css` version, else `?ver=` asset versions and
  Divi 5 markers on the home page). Detection runs once per command and fetches public files only.

| page file | site | result |
|---|---|---|
| Divi 4 shortcode | Divi 5 | **refused**, exit 1: "this is Divi 4 shortcode; the site runs Divi 5 — write Divi 5 blocks (reference/divi5/page-format.md)". A shortcode page on a Divi 5 site renders through a degraded legacy path and is never converted. |
| Divi 5 blocks | Divi 4 | **refused**, exit 1: "this is Divi 5 block content; the site runs Divi 4 — write Divi 4 shortcode (reference/page-format.md)". |
| either | unknown | a warning ("could not detect the site's Divi version"), then the request for the file's own format. |
| Divi 5 blocks with parse problems (bad JSON, unclosed or stray block comments) | any | **refused**, exit 1, each problem listed. Rewriting a block whose JSON doesn't parse would drop its attributes, so nothing is sent. |

The rest of the checks (validation with a baseline, local-image preflight, `--page-fields` rules, live-page
protection) are the same as for Divi 4. Block page files are read and written byte for byte (CRLF line ends
survive).

### Divi 5 builder meta

A Divi 5 page needs the post meta `_et_pb_use_builder = "on"`. Without it the modules still render, but inside the
theme's normal page template: an `<h1 class="entry-title">` with the page title and a sidebar (body class
`et_right_sidebar`). With it the body has `et_pb_pagebuilder_layout et_no_sidebar` and no title or sidebar.

**A plain REST save can't set it on Divi 5.** Divi registers the key for REST only when its Divi 4 shortcode
framework loads, and in a REST request that happens while `content.rendered` renders a Divi 4 shortcode, after the
request's meta was handled (`BlockEditorIntegration.php:1060-1080`). `POST /wp/v2/pages {"meta":
{"_et_pb_use_builder": "on"}}` returns 201 and stores nothing. Divi's own save routes need an `X-ET-Nonce` that an
Application Password can't get.

**What works** is `/batch/v1`, which runs several REST requests in one PHP process:

1. The page holds a Divi 4 stub, `[et_pb_section][/et_pb_section]`: a new page is created with it
   (`POST /wp/v2/pages {title, slug?, status: "draft", content: stub, …page-fields}`), an existing draft is
   overwritten with it (`POST /wp/v2/pages/ID {content: stub, status: "draft"}`).
2. One `POST /wp-json/batch/v1` with two requests for the page. The first re-saves the title; rendering its
   response renders the stub, which loads the framework and registers the key. The second sets the real content
   and `"meta": {"_et_pb_use_builder": "on"}`. Expect HTTP 207 with two 200s.
3. The check. The second request's own response lists the meta as read back from the database right after the write
   (the key is registered in that process). `publish.py` requires `"on"` there, then reads the page with
   `GET /wp/v2/pages/ID?context=edit`, which must not disagree.

Without the stub the same batch stores nothing, and its second response doesn't list the key at all, which is why
the check fails loudly instead of passing silently. The cost is one extra revision holding the stub.

**A plain `GET ?context=edit` can't show the key for a Divi 5 page.** It renders Divi 5 blocks, not a Divi 4
shortcode, so the key isn't registered in that request and `meta` comes back without it (verified: `meta` was
`{"footnotes": ""}` while `wp post meta get` said `on`). The key shows only while a page still holds Divi 4 content,
for example the stub. `publish.py` therefore treats a missing key as unknown, not as off.

What `publish.py` does with the meta:

| command | page | builder meta | requests |
|---|---|---|---|
| `draft` (new page) | — | — | stub create, batch, read-back |
| `draft --page-id` | draft or pending | shown as `on` | one `POST /pages/ID {title, content, status: "draft"}` |
| `draft --page-id` | draft or pending | off, or not shown (the usual case for a Divi 5 page) | stub overwrite, batch, read-back |
| `draft --page-id` | live (publish, future, private) | — | refused, exit 1, as for Divi 4 (never swap a live page's content) |
| `publish --content` | any | shown as `on`, or (for a published page) the public page's body has `et_pb_pagebuilder_layout` | one `POST /pages/ID {content}` plus `status: "publish"` unless the page is private or scheduled. No `meta`: a content update leaves it as it is. |
| `publish --content` | draft or pending | off, or not shown | stub overwrite `{content: stub}`, batch (the new content + meta), check, and only then `POST /pages/ID {status: "publish"}`. If the meta didn't stick: exit 2 and the page is still unpublished. |
| `publish` without `--content` | draft or pending holding Divi 5 blocks | off, or not shown | the same, re-sending the page's current `content.raw` with the meta, then the status change |
| `publish --content` | live | off (shown off, or the public page lacks `et_pb_pagebuilder_layout`) | **refused**, exit 1: set the meta in WordPress (open the page once in the Divi builder and save, or `wp post meta update ID _et_pb_use_builder on --user=<admin>`), or publish a reviewed draft copy instead. |
| `publish --content` | live | unknown, and the page holds Divi 5 blocks | proceeds with a note |
| `publish --content` | live | unknown, and the page holds no Divi 5 blocks | **refused**, exit 1 (it never had the builder meta) |
| `publish` without `--content` | live, or a page without Divi 5 blocks | — | unchanged from Divi 4 (status only) |

**Backstop.** Whenever `publish` leaves a Divi 5 page published, it reads the public page. If the body lacks
`et_pb_pagebuilder_layout` (and carries the page's own `page-id-ID`), it exits 2 and says how to fix it ("is now
published" for a page this command made public, "is published" for one that already was). The page is live at that
point, so fix it at once: set the meta or switch the page back to draft.

**Before the stub is written** (an existing page, in `draft --page-id` or `publish`), `publish.py` saves the page's
current `content.raw` to `page-<ID>-before-stub-<timestamp>.txt`, next to the input page file (the current
directory when `publish` has no `--content`), and prints the path. The stub is the only copy on the site otherwise,
and revisions may be disabled.

**When the meta doesn't stick** `draft` (and `publish`, before any status change) exits 2 with "WordPress did not
store _et_pb_use_builder=on; the page will render inside the theme's title+sidebar template. See
reference/publishing.md → Divi 5 builder meta." The page is still unpublished and holds the real content. A failed
batch (exit 2) leaves the page unpublished and possibly holding only the stub. Both messages name the backup and the
exact commands to finish: `publish.py draft PAGE --page-id ID --title "…"` (stays a draft) or, once approved,
`publish.py publish --page-id ID --content PAGE --yes`, where PAGE is your page file or the backup. Or set the meta
with WP-CLI (`wp post meta update ID _et_pb_use_builder on --user=<admin>`; always pass `--user`, see CSS below).
If Divi changes how it registers the key, the live test catches it.

**A page holding only the stub is never published as it is.** `publish --page-id ID --yes` without `--content`
refuses (exit 1) when the page's `content.raw` is exactly `[et_pb_section][/et_pb_section]` (ignoring surrounding
whitespace). With `--content` the new content replaces the stub through the verified stub + batch path.

### Local images in blocks

`draft` and `publish --content` upload local images (`./…`, `../…`, `file://…`) in block content too. An image is
any leaf the Divi 5 schema types `image`: `image.innerContent` `src` (image, fullwidth image, slide, fullwidth
header), blurb `imageIcon.innerContent` `src`, team member `image.innerContent` `url`, and every background
`image.url`. Each distinct file is uploaded once, and only that one key is rewritten to the uploaded `source_url`.
The block is re-serialized in canonical form with its `builderVersion` unchanged; every other block keeps its
bytes.

- **No `id`.** Divi 5's image value has no attachment id key (the validator rejects one). Divi finds the attachment
  from the URL: the rendered `<img>` gets `class="wp-image-<id>"`, `srcset` and size attributes.
- **Alt text lives in the block.** Divi renders `alt` from the image value's own `alt` key and `title` from
  `titleText`. It does **not** fall back to the Media Library's alt text (verified: an image module without `alt`
  rendered no `alt` attribute although the attachment had one). Write `alt` in the block. The upload's `alt_text`
  comes from that `alt`, else `titleText`, else the converter's `module.decoration.attributes` alt, else the file
  name; `publish.py` never adds an `alt` key to the block.

### `content.raw` and CSS

- On WordPress 7.0 and later, `content.raw` is WordPress's canonical re-serialization of the stored blocks, not
  the stored bytes (`divi5/page-format.md`). `fetch` says so on stderr for block content. Use the fetched file as
  the baseline as-is. After a draft, `publish.py` prints a note if the stored `content.raw` differs from the file it
  sent (expected for converter or builder output, which isn't canonical).
- **CSS:** a REST update marks the page's files in `wp-content/et-cache/<id>/` stale (`*.stale` markers; Divi 4
  deleted the directory instead), and the next front-end view regenerates them. Nothing to purge. A WP-CLI update
  without `--user` skips that and the next view serves the old CSS, so always pass `--user=<admin>`.

### The sequence with curl

For a manual run (`publish.py` does all of this, with the checks). `page.html` is the Divi 5 page file.

```bash
# 1. create the draft holding the Divi 4 stub
ID=$(curl -s -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d '{"title": "Emergency Plumber in Miami", "status": "draft", "content": "[et_pb_section][/et_pb_section]"}' \
  "$SITE/wp-json/wp/v2/pages" | python3 -c 'import json, sys; print(json.load(sys.stdin)["id"])')

# 2. one batch: re-save the title (renders the stub, registers the key), then content + meta
python3 - "$ID" > batch.json <<'PY'
import json, sys
pid = sys.argv[1]
content = open("page.html", encoding="utf-8", newline="").read()
print(json.dumps({"requests": [
    {"method": "POST", "path": f"/wp/v2/pages/{pid}", "body": {"title": "Emergency Plumber in Miami"}},
    {"method": "POST", "path": f"/wp/v2/pages/{pid}",
     "body": {"content": content, "meta": {"_et_pb_use_builder": "on"}}}]}))
PY
curl -s -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' -d @batch.json \
  "$SITE/wp-json/batch/v1" | python3 -c '
import json, sys
r = json.load(sys.stdin)["responses"]
print([x["status"] for x in r], r[1]["body"].get("meta", {}).get("_et_pb_use_builder"))'
# expect: [200, 200] on
```

Anything else (`None`, or a non-200) means the meta wasn't stored: the page renders in the theme's template.

## Raw REST reference

Everything below was verified live against a real WordPress + Divi 4.27.9 install
(a LocalWP test site) using the WordPress REST API and Application
Passwords. (The exact commands and raw results are in the repo only:
`research/tools/notes/rest-experiments.md`; nothing here depends on them.)

## 1. Auth

Use a WordPress **Application Password**, not the account's login password:

1. On the client site: **Users → Profile → Application Passwords**, or (for scripted setup on
   a site you control) WP-CLI: `wp user application-password create <user> <name> --porcelain`.
2. Requests use HTTP Basic auth: `-u "$WP_USER:$WP_APP_PASSWORD"`.
3. **HTTPS is required on live sites.** Application Passwords are transmitted as Basic auth
   (base64, not encrypted) on every request; WordPress core disables the feature entirely over
   plain HTTP unless `wp_is_application_passwords_available()` is forced true (e.g. by setting
   `WP_ENVIRONMENT_TYPE` to `local` — only appropriate for local development, never for a
   client's real site).
4. Store credentials as environment variables, never in code or config files. Every `curl`
   example on this page also uses `$SITE` for the site's base URL (no trailing slash):
   ```bash
   export SITE="https://client-site.example"
   export WP_USER="editor@client.example"
   export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
   ```
5. **Never** paste `$WP_APP_PASSWORD`'s value into chat, logs, commit messages, or any file.
   Every example on this page writes the literal string `$WP_APP_PASSWORD` — substitute the
   real value only in your shell, and unset it when you're done:
   ```bash
   unset WP_APP_PASSWORD
   ```

Verified: `wp_is_application_passwords_available()` returned `true` on the local test site
without any config changes (LocalWP already reports `WP_ENVIRONMENT_TYPE=local`). If it
returns `false` on a site you control (never on a client's live site), the local-only escape
hatch is `wp config set WP_ENVIRONMENT_TYPE local --type=constant`.

## 2. Upload images

Two calls: upload the binary, then set `alt_text` (the REST create endpoint doesn't accept
`alt_text` in the same request body as the binary upload).

```bash
curl -s -u "$WP_USER:$WP_APP_PASSWORD" \
  -H 'Content-Disposition: attachment; filename="hero.jpg"' \
  -H 'Content-Type: image/jpeg' \
  --data-binary @hero.jpg \
  "$SITE/wp-json/wp/v2/media"
```

Response includes `id` and `source_url`:

```json
{"id": 26, "source_url": "https://client-site.example/wp-content/uploads/2026/09/hero.jpg", "mime_type": "image/jpeg", ...}
```

Then set alt text as a second call:

```bash
curl -s -X POST -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d '{"alt_text": "Plumber repairing a burst pipe"}' \
  "$SITE/wp-json/wp/v2/media/26"
```

Use the returned `source_url` verbatim as the module's `src`/`background_image` attribute
value in the shortcode:

```
[et_pb_image src="https://client-site.example/wp-content/uploads/2026/09/hero.jpg" alt="Plumber repairing a burst pipe" ...][/et_pb_image]
```

## 3. Create a draft

```bash
python3 -c 'import json; print(json.dumps({
  "title": "Emergency Plumber in Miami",
  "status": "draft",
  "content": open("page.txt").read(),
  "meta": {"_et_pb_use_builder": "on"}
}))' > body.json

curl -s -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d @body.json "$SITE/wp-json/wp/v2/pages"
```

- `content` is the raw Divi shortcode string (see `page-format.md`) — send it as plain text in
  the JSON `content` field, **not** wrapped or escaped beyond normal JSON string encoding.
  Verified byte-for-byte round trip: `content.raw` read back via `GET ?context=edit`
  matched the sent file exactly, for both a plain-ASCII fixture and one full of curly quotes,
  an em dash, and an emoji (`tests/fixtures/valid/unicode.txt`) — WordPress does not
  re-escape or texturize `post_content` on write or on the `context=edit` read.
- `meta._et_pb_use_builder: "on"` is **required** — without it Divi's PHP treats the page as
  a plain (non-builder) page (`wpautop` may run on the content, and the sidebar layout rules
  differ — see the layout note below). It round-trips as `"on"` in the response's `meta`
  object.

**Layout — no sidebar / full width.** A page created this way (`_et_pb_use_builder = "on"`,
regular `page` post type) already renders with Divi's `et_no_sidebar` body class
automatically — this is forced by Divi's own `et_divi_sidebar_class()` for any builder-active
Page, regardless of anything else. **You do not need to set anything for this.** In
particular, do **not** bother with `_et_pb_page_layout` meta — it is not a registered REST
meta field (it never appears in the REST `meta` object, and a REST `POST` targeting it is
silently ignored, no error), and even set directly in the database via WP-CLI it makes no
observable difference on a builder-active Page.

If you also want to remove the site's header, primary nav, and footer widgets entirely (a
true blank canvas, e.g. a landing page supplying its own header section), set the `template`
field — this is the one REST-settable field that actually changes the rendered layout:

```json
{"template": "page-template-blank.php"}
```

Verified: setting this dropped `et_fixed_nav`, `et_show_nav`, `et_header_style_left`, and
`et_pb_footer_columns4` from the rendered body class, alongside the pre-existing
`et_no_sidebar`. This is publish.py's `--page-fields` default recommendation for a full-bleed
landing page; omit it for a normal page that should keep the site's header/nav/footer.

(`_et_pb_page_layout` *does* affect rendering on a **non-builder** page, but there both
`et_no_sidebar` and `et_full_width_page` meta values render the identical
`et_full_width_page` body class — Divi renames `et_no_sidebar` to `et_full_width_page` for
any post type that isn't one of its own custom post types. This case shouldn't come up for a
skill-authored page, which always sets `_et_pb_use_builder`.)

## 4. Preview

The create/update response's `link` field plus `&preview=true` is the built-in WordPress
preview URL for a draft, visible only to a logged-in user with edit rights on that post (it
needs a browser session cookie — `curl` alone can't view it without also authenticating the
cookie-based session, which Application Passwords don't provide).

```
https://client-site.example/?page_id=15&preview=true
```

**The WordPress draft, opened in a real logged-in browser tab, is the final visual check**, and it comes
*after* the user has approved the local preview (`preview.py`, SKILL.md step 7); never push a draft to
skip that step. Divi's actual PHP renders the shortcode tree,
applies the theme's CSS, and reflects any real site customizations (Divi Theme Options,
active plugins, global presets) that a local preview tool cannot fully replicate.

## 5. Publish

Flip `status` to `publish`, either at creation or as an update to an existing draft:

```bash
curl -s -X POST -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d '{"status": "publish"}' \
  "$SITE/wp-json/wp/v2/pages/15"
```

The response's `link` field becomes the page's real permalink
(`https://client-site.example/plan-test-rest-create/` in testing, rather than the `?page_id=`
form used for unpublished content). Loading that permalink the first time after publish
triggers Divi to generate its `et-cache` CSS for the page (see the cache section below) —
there is no separate "build" or "compile" step to call.

## 6. Edit an existing page

Always fetch the current authoritative content before editing, so you can diff against it and
avoid clobbering changes made in the WordPress admin since your last publish:

```bash
curl -s -u "$WP_USER:$WP_APP_PASSWORD" "$SITE/wp-json/wp/v2/pages/15?context=edit" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["content"]["raw"], end="")' \
  > original.txt

# edit a copy, then validate the edit against the original as a baseline
python3 scripts/validate.py edited.txt --baseline original.txt

# push the update
python3 -c 'import json; print(json.dumps({"content": open("edited.txt").read()}))' > update.json
curl -s -X POST -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d @update.json "$SITE/wp-json/wp/v2/pages/15"
```

`--context=edit` is required to get the raw (unfiltered) `content.raw` — a plain `GET` without
it returns `content.rendered`, which has already been through `do_shortcode()` and is
**not** valid shortcode to feed back in.

**Decision point on `validate.py --baseline`'s exit status.** `--baseline original.txt` tells
`validate.py` to only fail on findings that are *new* relative to the original page — anything
already present in `original.txt` (a pre-existing warning/error on the live page, not
introduced by this edit) does not block. Concretely:
- **Exit 1** (new errors, not present in the baseline) — **stop, fix the edit, and do not
  `POST`** until it exits 0.
- **Exit 0** — safe to `POST`, even if `validate.py` still reports pre-existing findings that
  were already there in `original.txt`; those aren't your edit's fault and don't block the
  update.

You only need to send the fields you're changing — a `POST` update with just `{"content":
...}` leaves title, status, template, and everything else untouched.

**Editing a page that's already published/scheduled/private.** Note that the raw `update.json`
above only sends `content`, so it never touches `status` — a live page stays live. This is
*not* what `publish.py draft --page-id` does: `draft` always sends `status: "draft"`, so
running it against a currently `publish`/`future`/`private` page would take that page offline.
`publish.py` guards against this itself (see "Editing a live page" in the "Using publish.py"
section above): `draft --page-id` checks the page's current status first and refuses if it's
live, and the fix is `publish.py publish --page-id ID --content edited.txt --yes`, which sends
`content` (and, for a page that is already `publish`, `status: "publish"`) in one request — the
same shape as this section's raw `curl` example, staying live throughout instead of
round-tripping through draft. For a `private` or `future` page it sends no `status` at all, so
the page stays private or scheduled; only `--status publish` changes that. It validates against
the page's current content as the baseline, like `validate.py --baseline` above.

## 7. CSS cache behavior

Divi caches per-page CSS under `wp-content/et-cache/<page-id>/` (5 files:
`et-core-unified-<id>.min.css`, `et-core-unified-deferred-<id>.min.css`,
`et-divi-dynamic-<id>-critical.css`, `et-divi-dynamic-<id>-late.css`, `et-divi-dynamic-<id>.css`).

**Verified: a REST `content` update deletes the page's entire `et-cache/<id>/` directory
synchronously, as part of the save** — not a lazy invalidation, not a partial touch. The very
next front-end page load regenerates all 5 files from scratch and reflects the new content
immediately. **No manual cache-purge call is needed after a REST update** — this is handled
by WordPress/Divi's own save hooks the same as an edit made in the block editor or Divi
Builder UI.

## 8. Troubleshooting

**401 Unauthorized.** Wrong username/password, or Application Passwords disabled (see
Auth above). Typical bodies:

```json
{"code":"rest_forbidden_context","message":"Sorry, you are not allowed to edit posts in this post type.","data":{"status":401}}
{"code":"rest_cannot_create","message":"Sorry, you are not allowed to create posts as this user.","data":{"status":401}}
```

Note that a plain `GET /wp/v2/pages` (no `context=edit`) succeeds with `200` even with no/bad
credentials — it just returns the public page list. Auth is only enforced on routes that
need elevated access: `context=edit`, creating, updating, deleting, or reading unpublished
content.

**403 Forbidden, `rest_cannot_edit`.** The credentials are valid, but that WordPress user
lacks `edit_post` capability on the specific page being targeted (for example, a Contributor
account trying to edit a page it doesn't own, or trying to publish without `publish_pages`).
Fix by using an account with sufficient capability (Editor or Administrator) for content
management, or granting the specific capability needed.

**Content altered on save.** In testing, `content.raw` round-tripped byte-for-byte through
REST for both a plain-ASCII fixture and a fixture containing curly quotes, an em dash, an
emoji, and already-percent-encoded escape sequences (`%22`, `%91`, `%93`, `%92`, `%5c`) inside
a `custom_css_*` attribute — none of it was altered by WordPress on write or read. If you
*do* see altered characters (most commonly this would be a raw `<` inside an attribute
desyncing `wptexturize()`, or unescaped `"`/`[`/`]` breaking attribute parsing — see the
escaping table in `page-format.md`), diff `content.raw` against what you sent with
`difflib.unified_diff` and check the offending page against `page-format.md`'s escaping rules
before re-sending.

## Reference: request/response shapes seen in testing

Create (`POST /wp/v2/pages`):
```json
{"title": "Plan Test: REST create", "status": "draft", "content": "<shortcode text>", "meta": {"_et_pb_use_builder": "on"}}
```

Read for editing (`GET /wp/v2/pages/<id>?context=edit`) — relevant fields:
```json
{"id": 15, "status": "draft", "content": {"raw": "<shortcode text>", "rendered": "<... do_shortcode output ...>"}, "meta": {"_et_pb_use_builder": "on", ...}, "link": "https://client-site.example/?page_id=15"}
```

Update (`POST /wp/v2/pages/<id>`), any subset of fields:
```json
{"content": "<new shortcode text>"}
{"status": "publish"}
{"template": "page-template-blank.php"}
```

Delete (`DELETE /wp/v2/pages/<id>?force=true`) — bypasses trash, used for cleanup in testing.
