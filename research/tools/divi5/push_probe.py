#!/usr/bin/env python3
"""Push Divi 5 block files to the local D5 site four ways and compare stored + rendered output.

    ADMIN_USER=.. ADMIN_PW=.. EDITOR_USER=.. EDITOR_PW=.. \
      python3 research/tools/divi5/push_probe.py OUTDIR FILE...

Methods: wpcli-admin (wp post create --user=<admin>), wpcli-editor (--user=<editor>),
rest-admin and rest-editor (POST /wp/v2/pages, Basic auth with an Application Password,
meta._et_pb_use_builder=on). For each: stored post_content vs the file (byte compare),
REST content.raw vs the file, and the rendered heading/text fragments from the front end.
Credentials come from the environment only and are never written anywhere. Pages are
titled "D5 Probe: ..." and deleted at the end unless KEEP=1.
"""
import base64, json, os, re, subprocess, sys, urllib.request

SITE = os.environ.get('SITE', 'http://divi-5-test.local')
HERE = os.path.dirname(os.path.abspath(__file__))
WP = os.path.join(HERE, '..', 'wp-local.sh')
ENV = dict(os.environ, LOCAL_SITE_ID=os.environ.get('LOCAL_SITE_ID', 'fTZ3hcgdI'),
           LOCAL_SITE_PATH=os.environ.get('LOCAL_SITE_PATH',
                                          os.path.expanduser('~/Local Sites/divi-5-test/app/public')))


def wp(*args):
    r = subprocess.run([WP, *args], capture_output=True, text=True, env=ENV)
    return r.stdout.strip()


def raw_content(pid):
    # post_content exactly as stored (no trailing newline added by `wp post get`).
    out = wp('eval', f'echo base64_encode(get_post_field("post_content", {int(pid)}, "raw"));')
    return base64.b64decode(out).decode('utf-8')


def rest(method, path, user, pw, body=None):
    req = urllib.request.Request(SITE + '/wp-json' + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None)
    req.add_header('Authorization', 'Basic ' + base64.b64encode(f'{user}:{pw}'.encode()).decode())
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


def fetch(url):
    with urllib.request.urlopen(url) as r:
        return r.read().decode('utf-8')


def fragments(html):
    # Heading inner HTML, and everything from the text module's inner div to the end of the column.
    h = re.search(r'<div class="et_pb_heading_container">(.*?)</div>', html, re.S)
    t = re.search(r'<div class="et_pb_text_inner">(.*?)</div></div></div></div></div>', html, re.S)
    return (h.group(1) if h else None), (t.group(1) if t else None)


def main():
    out, files = sys.argv[1], sys.argv[2:]
    os.makedirs(out, exist_ok=True)
    creds = {'admin': (os.environ['ADMIN_USER'], os.environ['ADMIN_PW']),
             'editor': (os.environ['EDITOR_USER'], os.environ['EDITOR_PW'])}
    results, made = [], []
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        src = open(f, encoding='utf-8', newline='').read()
        for method in ('wpcli-admin', 'wpcli-editor', 'rest-admin', 'rest-editor'):
            role = method.split('-')[1]
            title = f'D5 Probe: {name} {method}'
            rest_raw = None
            meta_back = None
            if method.startswith('wpcli'):
                pid = wp('post', 'create', f, '--post_type=page', '--post_status=publish',
                         f'--post_title={title}', '--porcelain', f'--user={creds[role][0]}')
                wp('post', 'meta', 'update', pid, '_et_pb_use_builder', 'on')
            else:
                code, body = rest('POST', '/wp/v2/pages', *creds[role],
                                  {'title': title, 'status': 'publish', 'content': src,
                                   'meta': {'_et_pb_use_builder': 'on'}})
                if code >= 300:
                    results.append({'file': name, 'method': method, 'error': body}); continue
                pid = str(body['id'])
                code, got = rest('GET', f'/wp/v2/pages/{pid}?context=edit', *creds[role])
                rest_raw = got['content']['raw']
                meta_back = got.get('meta', {}).get('_et_pb_use_builder')
            made.append(pid)
            stored = raw_content(pid)
            url = wp('post', 'get', pid, '--field=url')
            html = fetch(url)
            h, t = fragments(html)
            open(os.path.join(out, f'{name}.{method}.stored.html'), 'w', encoding='utf-8').write(stored)
            open(os.path.join(out, f'{name}.{method}.frag.html'), 'w', encoding='utf-8').write(
                f'HEADING:\n{h}\nTEXT:\n{t}\n')
            r = {'file': name, 'method': method, 'id': pid,
                 'stored_identical': stored == src, 'stored_len': len(stored), 'src_len': len(src),
                 'rest_raw_identical': (rest_raw == src) if rest_raw is not None else None,
                 'meta_back': meta_back,
                 'rendered_heading': h is not None, 'rendered_text': t is not None,
                 'cache_files': sorted(os.listdir(os.path.join(ENV['LOCAL_SITE_PATH'], 'wp-content/et-cache', pid)))
                 if os.path.isdir(os.path.join(ENV['LOCAL_SITE_PATH'], 'wp-content/et-cache', pid)) else []}
            results.append(r)
            print(json.dumps(r, ensure_ascii=False))
    json.dump(results, open(os.path.join(out, 'results.json'), 'w'), indent=1, ensure_ascii=False)
    if os.environ.get('KEEP') != '1':
        for pid in made:
            wp('post', 'delete', pid, '--force')
    else:
        print('kept pages:', ' '.join(made))


if __name__ == '__main__':
    main()
