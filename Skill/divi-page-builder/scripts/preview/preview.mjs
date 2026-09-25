#!/usr/bin/env node
// One-command Divi 4 preview on WordPress Playground (WebAssembly PHP + WordPress + SQLite; no MySQL, no LocalWP).
//
//   node preview.mjs serve  [--pages DIR] [--divi VER | --tokens tokens.json] [--port 9400] [--php 8.2] [--wp 7.1.2] [--fresh]
//       Boots WordPress + the real Divi theme and serves http://127.0.0.1:PORT/?pp_preview=<name>
//       for every DIR/<name>.txt (Divi 4 shortcode). The file is re-read on every request: edit, reload.
//   node preview.mjs render <layout.txt> [--out page.html] [--divi VER | --tokens tokens.json] [same flags]
//       Boots, renders one layout to a self-contained HTML file (local CSS/JS/icon fonts inlined), shuts down.
//   node preview.mjs fetch-divi <VER|latest>
//       Downloads and caches a Divi version from Elegant Themes. The only command that needs credentials.
//   node preview.mjs doctor
//       Prints Node/npx/unzip/tar status, the cache dir, and cached Divi/WordPress versions. Exit 0 = usable.
//
// Divi version resolution (serve/render): --divi, else --tokens (site.divi_version), else the newest
// cached version, else "latest" (network). A cached version never triggers an Elegant Themes API call
// (it rate-limits at about 15 calls per 5 minutes).
//
// Env: ET_USERNAME / ET_API_KEY  - only needed when the resolved Divi version is not cached yet; never
//                                  printed or written (see fetch-divi.mjs).
//      PP_CACHE_DIR              - cache root (default ~/.cache/divi-page-builder, %LOCALAPPDATA%\divi-page-builder):
//                                    divi/Divi-<v>/Divi        unpacked theme (+ the zip)
//                                    wordpress/<v>/wordpress    pristine WordPress core
//                                    sites/wp<v>-divi<v>/wordpress  persistent Playground site (SQLite DB inside)
//      PP_WP_VERSION             - WordPress version (default 7.1.2).
//      PP_PLAYGROUND_CLI         - npm spec of the Playground CLI (pinned by default).
// After the first run (Divi + WordPress + npm package cached) it works fully offline.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { ensureDivi, defaultCacheDir, cacheRoot, unzip, playgroundEnv } from './fetch-divi.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
// Pinned: the offline/preferredVersions quirks documented below are specific to this CLI version.
const CLI = process.env.PP_PLAYGROUND_CLI || '@wp-playground/cli@3.1.55';

function parseArgs(argv) {
	const o = { _: [], port: '9400', php: '8.2', wp: process.env.PP_WP_VERSION || '7.1.2', pages: process.cwd(), out: null, divi: null, tokens: null, debug: false, fresh: false };
	for (let i = 0; i < argv.length; i++) {
		const a = argv[i];
		if (a === '--debug' || a === '--fresh') o[a.slice(2)] = true;
		else if (a.startsWith('--')) { const [k, v] = a.includes('=') ? a.slice(2).split(/=(.*)/s) : [a.slice(2), argv[++i]]; o[k] = v; }
		else o._.push(a);
	}
	return o;
}

// All Divi versions found in the cache, oldest first (only those with a readable style.css).
function listCachedDivi(cacheDir) {
	if (!fs.existsSync(cacheDir)) return [];
	const v = fs.readdirSync(cacheDir).map((d) => (d.match(/^Divi-(\d+(?:\.\d+)*)$/) || [])[1]).filter(Boolean)
		.filter((ver) => fs.existsSync(path.join(cacheDir, `Divi-${ver}`, 'Divi', 'style.css')));
	v.sort((a, b) => a.split('.').map(Number).reduce((r, x, i) => r || x - (b.split('.').map(Number)[i] || 0), 0));
	return v;
}

function newestCached(cacheDir) {
	return listCachedDivi(cacheDir).pop() || null;
}

function listCachedWordPress() {
	const dir = path.join(cacheRoot(), 'wordpress');
	if (!fs.existsSync(dir)) return [];
	return fs.readdirSync(dir).filter((v) => fs.existsSync(path.join(dir, v, 'wordpress', 'wp-settings.php')));
}

// --divi, else --tokens (site.divi_version), else the newest cached version, else "latest" (network).
// Never resolves to a network call when a version is already cached.
function resolveDiviVersion(o, diviCache) {
	if (o.divi) return o.divi;
	if (o.tokens) {
		const tokens = JSON.parse(fs.readFileSync(path.resolve(o.tokens), 'utf8'));
		const site = (tokens && tokens.site) || {};
		if (!('divi_version' in site)) throw new Error(`No site.divi_version in ${o.tokens}`);
		if (site.divi_version) return site.divi_version;
		// Empty version (not detected when the tokens were extracted): fall through to the next rule.
		const fallback = newestCached(diviCache) || 'latest';
		console.error(`note: site.divi_version is empty in ${o.tokens}; using ${fallback === 'latest' ? 'latest' : 'the newest cached Divi, ' + fallback}`);
		return fallback;
	}
	return newestCached(diviCache) || 'latest';
}

// WordPress core, downloaded by us (not by the CLI): the CLI's own download path always asks
// api.wordpress.org to resolve the version first, even for a pinned version or release URL => not offline-safe.
async function ensureWordPress(ver, log) {
	const dir = path.join(cacheRoot(), 'wordpress', ver);
	if (fs.existsSync(path.join(dir, 'wordpress', 'wp-settings.php'))) return path.join(dir, 'wordpress');
	const t = Date.now();
	const r = await fetch(`https://downloads.wordpress.org/release/wordpress-${ver}.zip`);
	if (!r.ok) throw new Error(`WordPress ${ver} download failed: HTTP ${r.status}`);
	fs.mkdirSync(dir, { recursive: true });
	const zip = path.join(dir, `wordpress-${ver}.zip`);
	fs.writeFileSync(zip, Buffer.from(await r.arrayBuffer()));
	unzip(zip, dir);
	fs.rmSync(zip);
	log(`Fetched WordPress ${ver} in ${Date.now() - t} ms`);
	return path.join(dir, 'wordpress');
}

// One persistent site per (WP, Divi) pair: Playground installs into it once (SQLite DB in
// wp-content/database), later boots skip the install. Divi's own options never leak across Divi versions.
function ensureSite(wpDir, wpVer, diviVer, fresh) {
	const site = path.join(cacheRoot(), 'sites', `wp${wpVer}-divi${diviVer}`, 'wordpress');
	if (fresh) fs.rmSync(path.dirname(site), { recursive: true, force: true });
	if (!fs.existsSync(path.join(site, 'wp-settings.php'))) fs.cpSync(wpDir, site, { recursive: true });
	for (const d of ['themes/Divi', 'mu-plugins']) fs.mkdirSync(path.join(site, 'wp-content', d), { recursive: true });
	return site;
}

function writeBlueprint(php) {
	// preferredVersions.php must be set: without it the blueprint's default wins over --php (seen: PHP 8.5 ran).
	const bp = JSON.parse(fs.readFileSync(path.join(HERE, 'blueprint.json'), 'utf8'));
	bp.preferredVersions = { php, wp: 'latest' }; // wp is ignored in install-from-existing-files mode
	const f = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'pp-bp-')), 'blueprint.json');
	fs.writeFileSync(f, JSON.stringify(bp));
	return f;
}

function startPlayground({ siteDir, themeDir, pagesDir, port, php, debug }) {
	// --prefer-offline: the CLI version is pinned, so never revalidate against the registry (offline, npx
	// otherwise waits ~70 s for the registry to time out before using its cache).
	const args = ['-y', '--prefer-offline', CLI, 'server', `--php=${php}`, `--port=${port}`,
		// install-from-existing-files + our own WordPress download: the CLI's normal --wp path always calls
		// api.wordpress.org/core/version-check first, which fails offline even for a pinned version.
		`--mount-before-install=${siteDir}:/wordpress`, '--wordpress-install-mode=install-from-existing-files-if-needed',
		`--mount=${themeDir}:/wordpress/wp-content/themes/Divi`,
		`--mount=${path.join(HERE, 'mu-plugin')}:/wordpress/wp-content/mu-plugins`,
		`--mount=${pagesDir}:/pp-pages`,
		`--blueprint=${writeBlueprint(php)}`];
	if (debug) args.push('--define-bool', 'WP_DEBUG', 'true', '--define-bool', 'WP_DEBUG_DISPLAY', 'true');
	const win = process.platform === 'win32';
	const child = spawn(win ? 'npx.cmd' : 'npx', args, { stdio: ['ignore', 'pipe', 'pipe'], detached: !win, shell: win, env: playgroundEnv() });
	let exited = false;
	child.on('exit', () => { exited = true; });
	const kill = (sig) => { try { win ? spawn('taskkill', ['/pid', String(child.pid), '/T', '/F']) : process.kill(-child.pid, sig); } catch {} };
	// Resolves once the whole process group is gone (SIGKILL after 5 s).
	const stop = () => new Promise((resolve) => {
		if (exited) return resolve();
		child.once('exit', () => resolve());
		kill('SIGTERM');
		setTimeout(() => { kill('SIGKILL'); resolve(); }, 5000).unref();
	});
	const ready = new Promise((resolve, reject) => {
		let log = '';
		const onData = (d) => {
			log += d;
			const m = log.match(/Ready! WordPress is running on (\S+)/);
			if (m) resolve(m[1]);
		};
		child.stdout.on('data', onData);
		child.stderr.on('data', (d) => { if (!/EBADENGINE|npm warn|npm notice/.test(d)) process.stderr.write(d); onData(d); });
		child.on('exit', (code) => reject(new Error(`Playground exited (${code}) before ready:\n${log.replace(/npm (warn|notice).*\n/g, '').slice(-2000)}`)));
	});
	return { stop, ready };
}

function hasBinary(cmd, args) {
	try {
		const r = spawnSync(cmd, args, { stdio: 'ignore' });
		return r.error == null;
	} catch {
		return false;
	}
}

function doctor() {
	let ok = true;
	const lines = [];

	const nodeMajor = Number(process.versions.node.split('.')[0]);
	const nodeOk = nodeMajor >= 20;
	ok = ok && nodeOk;
	lines.push(`node: ${process.version}${nodeOk ? '' : ' (need >= 20 for global fetch)'}`);

	const npxOk = hasBinary(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['--version']);
	ok = ok && npxOk;
	lines.push(`npx: ${npxOk ? 'found' : 'MISSING'}`);

	const unzipOk = hasBinary('unzip', ['-v']);
	const tarOk = hasBinary('tar', ['--version']);
	if (!unzipOk && !tarOk) ok = false;
	lines.push(`unzip: ${unzipOk ? 'found' : 'not found'}`);
	lines.push(`tar: ${tarOk ? 'found' : 'not found'}`);

	lines.push(`cache dir: ${cacheRoot()}`);
	const diviVersions = listCachedDivi(defaultCacheDir());
	lines.push(`cached Divi versions: ${diviVersions.length ? diviVersions.join(', ') : '(none)'}`);
	const wpVersions = listCachedWordPress();
	lines.push(`cached WordPress versions: ${wpVersions.length ? wpVersions.join(', ') : '(none)'}`);

	console.log(lines.join('\n'));
	process.exit(ok ? 0 : 1);
}

const o = parseArgs(process.argv.slice(2));
const cmd = o._[0];
if (!['serve', 'render', 'fetch-divi', 'doctor'].includes(cmd)) {
	console.error(fs.readFileSync(fileURLToPath(import.meta.url), 'utf8').split('\n').slice(1, 27).map((l) => l.replace(/^\/\/ ?/, '')).join('\n'));
	process.exit(2);
}

if (cmd === 'doctor') {
	doctor();
}

if (cmd === 'fetch-divi') {
	try {
		const divi = await ensureDivi(o._[1] || 'latest', defaultCacheDir(), (msg) => console.error(msg));
		console.log(`Divi ${divi.version} ${divi.cached ? '(cached)' : '(downloaded)'} -> ${divi.themeDir}`);
		process.exit(0);
	} catch (e) {
		console.error('fetch-divi: ' + e.message);
		process.exit(1);
	}
}

const t0 = Date.now();
const lap = (label) => console.error(`[${((Date.now() - t0) / 1000).toFixed(1)}s] ${label}`);
let pg, tmpPages;
const cleanup = async () => { await pg?.stop(); if (tmpPages) fs.rmSync(tmpPages, { recursive: true, force: true }); };
process.on('SIGINT', async () => { await cleanup(); process.exit(130); });
process.on('SIGTERM', async () => { await cleanup(); process.exit(143); });

try {
	const diviCache = defaultCacheDir();
	const divi = await ensureDivi(resolveDiviVersion(o, diviCache), diviCache, lap);
	lap(`Divi ${divi.version} ${divi.cached ? '(cached)' : '(downloaded)'}`);
	const wpDir = await ensureWordPress(o.wp, lap);
	const siteDir = ensureSite(wpDir, o.wp, divi.version, o.fresh);
	lap(`Site ${siteDir}`);

	let pagesDir = path.resolve(o.pages);
	if (cmd === 'render') {
		if (!o._[1]) throw new Error('render needs a layout file');
		pagesDir = tmpPages = fs.mkdtempSync(path.join(os.tmpdir(), 'pp-preview-'));
		fs.copyFileSync(path.resolve(o._[1]), path.join(pagesDir, 'page.txt'));
		const meta = path.resolve(o._[1]).replace(/\.[^.]+$/, '') + '.meta.json';
		if (fs.existsSync(meta)) fs.copyFileSync(meta, path.join(pagesDir, 'page.meta.json'));
	}

	pg = startPlayground({ siteDir, themeDir: divi.themeDir, pagesDir, port: o.port, php: o.php, debug: o.debug });
	const base = await pg.ready;
	lap(`WordPress ready at ${base}`);

	if (cmd === 'serve') {
		const pages = fs.readdirSync(pagesDir).filter((f) => f.endsWith('.txt'));
		for (const f of pages) console.log(`${base}/?pp_preview=${encodeURIComponent(f.slice(0, -4))}`);
		if (!pages.length) console.log(`(no *.txt in ${pagesDir}; add one and open ${base}/?pp_preview=<name>)`);
		console.error('Serving; Ctrl-C to stop.');
		await new Promise(() => {});
	} else {
		const t1 = Date.now();
		const r = await fetch(`${base}/?pp_preview=page&inline=1`);
		const html = await r.text();
		if (r.status !== 200 || !r.headers.get('x-pp-preview')) throw new Error(`render failed: HTTP ${r.status}\n${html.slice(0, 1500)}`);
		const out = path.resolve(o.out || path.basename(o._[1]).replace(/\.[^.]+$/, '') + '.html');
		fs.writeFileSync(out, html);
		lap(`Rendered in ${Date.now() - t1} ms -> ${out} (${(html.length / 1024).toFixed(1)} KB; ${r.headers.get('x-pp-env')})`);
		await cleanup();
		process.exit(0);
	}
} catch (e) {
	console.error('preview: ' + e.message);
	await cleanup();
	process.exit(1);
}
