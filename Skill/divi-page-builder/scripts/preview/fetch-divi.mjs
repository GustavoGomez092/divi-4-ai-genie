#!/usr/bin/env node
// Download + unpack a specific Divi version (4.x or 5.x) from the Elegant Themes API into a local cache.
//
//   ET_USERNAME=... ET_API_KEY=... node fetch-divi.mjs [version|latest|latest5] [--cache DIR]
//   (latest = newest Divi 4, as always; latest5 = newest Divi 5)
//
// Endpoints (from Divi core/components/api/ElegantThemes.php + core/components/Updates.php):
//   version check : GET https://www.elegantthemes.com/api/api.php?api_update=1&action=check_version_status&product=Divi&version=V&username=U&api_key=K
//                   -> PHP-serialized a:1:{s:6:"status";s:9:"available"|"not_available"|"blocklisted"}   (does NOT validate credentials)
//   latest        : POST https://www.elegantthemes.com/api/api.php  action=check_theme_updates installed_themes[Divi]=4.0.0 automatic_updates=on username api_key
//                   -> serialized array; ['Divi']['new_version'] + ['Divi']['package']. The server picks the upgrade line
//                   from the installed version: installed 0 -> 2.3.6 (!), 4.0.0 -> newest Divi 4 (4.27.9 on 2026-09-24).
//                   Divi 5 is only offered when the divi_5 parameter is sent (et_core_maybe_add_divi5_api_parameter):
//                   `latest5` sends divi_5=on with installed_themes[Divi]=5.0.0; `latest` never sends it.
//                   Verified 2026-09-29: latest5 -> "5.14"; the 5.13.1 zip is 32.7 MB, top-level "Divi/" as for Divi 4.
//   download      : GET https://www.elegantthemes.com/api/api_downloads.php?api_update=1&theme=Divi&version=V&username=U&api_key=K
//                   -> 200 application/zip (top-level dir "Divi/"); omit `version` for latest.
//                   bad api key -> 200 text/html "API key is not valid"; bad user -> "Subscription is not active";
//                   unknown version -> 403 XML AccessDenied (S3). Too many calls (~15 in a few minutes) -> 429 HTML page.
// Credentials are only ever held in memory; nothing here prints or writes them.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// PP_ET_ENDPOINT: internal/test-only override for the API base URL (never set for real use). Lets
// tests point at a local stand-in instead of the real Elegant Themes API, without real credentials.
const API = process.env.PP_ET_ENDPOINT || 'https://www.elegantthemes.com/api/';
const UA = 'WordPress/6.8; Elegant Themes/4.27.9; https://localhost/';

export function cacheRoot() {
	if (process.env.PP_CACHE_DIR) return process.env.PP_CACHE_DIR;
	if (process.platform === 'win32' && process.env.LOCALAPPDATA) return path.join(process.env.LOCALAPPDATA, 'divi-page-builder');
	return path.join(process.env.XDG_CACHE_HOME || path.join(os.homedir(), '.cache'), 'divi-page-builder');
}
export function defaultCacheDir() {
	return process.env.PP_DIVI_CACHE || path.join(cacheRoot(), 'divi');
}

function creds() {
	const username = process.env.ET_USERNAME, api_key = process.env.ET_API_KEY;
	if (!username || !api_key) throw new Error('Divi is not cached for this version: set ET_USERNAME and ET_API_KEY (Elegant Themes account > API Key) to download it.');
	return { username, api_key };
}
// Secrets that must never reach a child process that doesn't need them (npx / WordPress Playground).
const CHILD_SECRETS = ['ET_USERNAME', 'ET_API_KEY', 'WP_APP_PASSWORD'];
export function playgroundEnv(env = process.env) {
	const out = { ...env };
	for (const k of CHILD_SECRETS) delete out[k];
	return out;
}
// For response BODY text, which is never URL-encoded, so a raw substring match is correct here.
const redact = (s, c) => String(s).split(c.api_key).join('<API_KEY>').split(c.username).join('<ET_USERNAME>');

// A safe-to-print URL built from the SAME params, with credentials replaced before encoding. Never
// derive this by string-matching the raw credentials against the already-encoded URL: URLSearchParams
// percent-encodes (e.g. '@' -> '%40', '+' -> '%2B'), so an email-style username or a key containing
// '+'/'/' would survive untouched in that encoded form and leak into an error message.
function redactedUrl(endpoint, params) {
	const safe = { ...params };
	if ('username' in safe) safe.username = '<ET_USERNAME>';
	if ('api_key' in safe) safe.api_key = '<API_KEY>';
	return API + endpoint + '.php?' + new URLSearchParams(safe);
}

async function etGet(endpoint, params) {
	const url = API + endpoint + '.php?' + new URLSearchParams(params);
	const r = await fetch(url, { headers: { 'User-Agent': UA } });
	return { status: r.status, type: r.headers.get('content-type') || '', body: Buffer.from(await r.arrayBuffer()), url, redactedUrl: redactedUrl(endpoint, params) };
}

// "latest" is the Divi 4 line (what it always meant); "latest4"/"latest5" name the line explicitly.
export const LATEST_ALIASES = { latest: 4, latest4: 4, latest5: 5 };

// The newest Divi of the `major` line. Divi 5 is only offered with divi_5=on (what Divi 5's own updater adds,
// et_core_maybe_add_divi5_api_parameter) and an installed 5.x.
export async function latestVersion(major = 4) {
	const c = creds();
	const form = { action: 'check_theme_updates', 'installed_themes[Divi]': major === 5 ? '5.0.0' : '4.0.0', class_version: '1.2', automatic_updates: 'on' };
	if (major === 5) form.divi_5 = 'on';
	const body = new URLSearchParams({ ...form, ...c });
	const r = await fetch(API + 'api.php', { method: 'POST', body, headers: { 'User-Agent': UA, 'Content-Type': 'application/x-www-form-urlencoded' } });
	const text = await r.text();
	const m = text.match(/s:11:"new_version";s:\d+:"([^"]+)"/);
	if (!m) throw new Error(`Could not determine latest Divi version (HTTP ${r.status}${r.status === 429 ? ' rate-limited, retry later' : ''})`);
	return m[1];
}

export function unzip(zip, dest) {
	fs.mkdirSync(dest, { recursive: true });
	// unzip (macOS/Linux) or bsdtar (macOS, Windows 10+ tar.exe) - both read zip archives.
	for (const [cmd, args] of [['unzip', ['-q', '-o', zip, '-d', dest]], ['tar', ['-xf', zip, '-C', dest]]]) {
		const r = spawnSync(cmd, args, { stdio: 'ignore' });
		if (r.status === 0) return;
	}
	throw new Error('Could not extract ' + zip + ' (need `unzip` or bsdtar `tar`).');
}

// 5.14 and 5.14.0 are one version (the Divi 5 API reports short versions).
export function sameVersion(a, b) {
	const key = (v) => { const p = v.split('.'); while (p.length > 1 && p[p.length - 1] === '0') p.pop(); return p.join('.'); };
	return key(a) === key(b);
}

/** Returns the absolute path of an unpacked Divi theme dir (…/Divi-<version>/Divi) for `version`. */
export async function ensureDivi(version = 'latest', cacheDir = defaultCacheDir(), log = console.error) {
	if (LATEST_ALIASES[version]) version = await latestVersion(LATEST_ALIASES[version]);
	const themeDir = path.join(cacheDir, `Divi-${version}`, 'Divi');
	const styleCss = path.join(themeDir, 'style.css');
	if (fs.existsSync(styleCss)) return { version, themeDir, cached: true };
	// Another spelling of the same version (Divi-5.14 for 5.14.0, or the reverse) is the same cached build.
	const same = listCachedDivi(cacheDir).find((v) => sameVersion(v, version));
	if (same) return { version, themeDir: path.join(cacheDir, `Divi-${same}`, 'Divi'), cached: true };

	const c = creds();
	const st = await etGet('api', { api_update: 1, action: 'check_version_status', product: 'Divi', version, ...c });
	const status = (st.body.toString().match(/"status";s:\d+:"([^"]+)"/) || [])[1];
	if (status !== 'available') {
		throw new Error(`Divi ${version} is not downloadable (status=${status || 'unexpected response HTTP ' + st.status + (st.status === 429 ? ' rate-limited, retry later' : '')}) url=${st.redactedUrl}`);
	}

	const t0 = Date.now();
	const dl = await etGet('api_downloads', { api_update: 1, theme: 'Divi', version, ...c });
	if (dl.status !== 200 || dl.body.subarray(0, 2).toString() !== 'PK') {
		// A redacted URL (never the raw credentials) so a failed download can still be diagnosed. The body is
		// redacted before it is truncated, so a credential cut in two by the slice can't escape redaction.
		throw new Error(`Divi download failed: HTTP ${dl.status} ${dl.type} url=${dl.redactedUrl} ${redact(dl.body.toString(), c).slice(0, 160).trim()}`);
	}
	fs.mkdirSync(cacheDir, { recursive: true });
	const zip = path.join(cacheDir, `Divi-${version}.zip`);
	fs.writeFileSync(zip, dl.body);
	unzip(zip, path.join(cacheDir, `Divi-${version}`));
	const got = (fs.readFileSync(styleCss, 'utf8').match(/^Version:\s*(\S+)/m) || [])[1];
	if (!got || !sameVersion(got, version)) throw new Error(`Downloaded zip has Divi ${got}, expected ${version}`);
	log(`Fetched Divi ${version} (${(dl.body.length / 1048576).toFixed(1)} MB) in ${Date.now() - t0} ms -> ${themeDir}`);
	return { version, themeDir, cached: false };
}

// ---- version selection (shared by preview.mjs) --------------------------------------------------------------
const cmpVersions = (a, b) => a.split('.').map(Number).reduce((r, x, i) => r || x - (b.split('.').map(Number)[i] || 0), 0);

/** Cached Divi versions (those with a readable style.css), oldest first; only Divi `major` when given. */
export function listCachedDivi(cacheDir = defaultCacheDir(), major = null) {
	if (!fs.existsSync(cacheDir)) return [];
	return fs.readdirSync(cacheDir).map((d) => (d.match(/^Divi-(\d+(?:\.\d+)*)$/) || [])[1]).filter(Boolean)
		.filter((ver) => fs.existsSync(path.join(cacheDir, `Divi-${ver}`, 'Divi', 'style.css')))
		.filter((ver) => major == null || Number(ver.split('.')[0]) === major)
		.sort(cmpVersions);
}

export function newestCached(cacheDir = defaultCacheDir(), major = null) {
	return listCachedDivi(cacheDir, major).pop() || null;
}

/** 5 for Divi 5 block markup (a `<!-- wp:divi/` block), else 4 (shortcode, or nothing to go on). */
export function contentMajor(text) {
	return /<!--\s+wp:divi\/[a-z0-9-]+/.test(text || '') ? 5 : 4;
}

// --divi, else --tokens (site.divi_version), else the newest cached version OF THE CONTENT'S MAJOR, else
// "latest" / "latest5" (network). Never resolves to a network call when a version of that major is cached.
export function resolveDiviVersion(o, diviCache = defaultCacheDir(), major = 4) {
	const fallback = () => newestCached(diviCache, major) || (major === 5 ? 'latest5' : 'latest');
	if (o.divi) return o.divi;
	if (o.tokens) {
		const tokens = JSON.parse(fs.readFileSync(path.resolve(o.tokens), 'utf8'));
		const site = (tokens && tokens.site) || {};
		if (!('divi_version' in site)) throw new Error(`No site.divi_version in ${o.tokens}`);
		if (site.divi_version) return site.divi_version;
		// Empty version (not detected when the tokens were extracted): fall through to the next rule.
		const v = fallback();
		console.error(`note: site.divi_version is empty in ${o.tokens}; using ${v.startsWith('latest') ? v : 'the newest cached Divi ' + major + ', ' + v}`);
		return v;
	}
	return fallback();
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
	const args = process.argv.slice(2);
	const ci = args.indexOf('--cache');
	const cache = ci >= 0 ? args.splice(ci, 2)[1] : defaultCacheDir();
	ensureDivi(args[0] || 'latest', cache)
		.then((r) => console.log(JSON.stringify(r)))
		.catch((e) => { console.error('fetch-divi: ' + e.message); process.exit(1); });
}
