#!/usr/bin/env python3
"""Generate Divi 5 escaping test pages: the same tricky values serialized several ways.

    python3 research/tools/divi5/make_escape_cases.py OUTDIR
    python3 research/tools/divi5/make_escape_cases.py --fixture tests/fixtures/divi5/escape-cases.html

Writes OUTDIR/<variant>.html. Every variant holds the same attribute *values* (after JSON
decoding); only the on-disk encoding differs, so rendering them side by side shows which
encodings Divi's parser accepts and whether any change the rendered output.

--fixture writes one canonical page (WordPress serialize_blocks() form: placeholder wrapper,
self-closing leaves, serialize_block_attributes() escaping) holding the same values plus EXTRA, so
that it uses every serialize_block_attributes() escape (\\ \" -- < > & U+2028 U+2029), JSON control
escapes, raw DEL, non-ASCII and astral characters. tests/test_divi5_judge.py has WordPress check it.
"""
import json
import os
import sys

HEADING = 'H1 "dq" \'sq\' <b>bold</b> a & b &amp; c -- d [br] ]] \\ one \\\\ two \\u0041 %22 %91 ü € 😀 end'
TEXT = ('<p>T1 "dq" \'sq\' &amp; &copy; & 5 &lt; 6 -- x [et_pb_text]not a shortcode[/et_pb_text] '
        '[caption] \\ back \\\\ dbl \\u0041 %22 ü € 😀</p>\n<p>line2 <a href="https://example.com/?a=1&b=2" '
        'onclick="x()">link</a> <span style="color:#ff0000">red</span></p><script>alert(1)</script>')
# Classes R3's two values miss: line/paragraph separators, tab and newline, a C0 control, DEL, a backslash
# right before a quote, three dashes, an HTML comment and a CSS escape.
EXTRA = ('<p>Tab\there; LS\u2028PS\u2029; bell\x01 del\x7f; path C:\\dir\\ and \\"quoted\\"; '
         'dashes --- and <!-- note -->; CSS \\201C</p>\n<p>second line</p>')


def attrs(kind, marker):
    if kind == 'heading':
        return {"title": {"innerContent": {"desktop": {"value": HEADING}}},
                "module": {"meta": {"adminLabel": {"desktop": {"value": marker}}}},
                "builderVersion": "5.13.1", "modulePreset": ["default"]}
    return {"content": {"innerContent": {"desktop": {"value": TEXT}}},
            "module": {"meta": {"adminLabel": {"desktop": {"value": marker}}}},
            "builderVersion": "5.13.1", "modulePreset": ["default"]}


def enc_php(a):  # WordPress serialize_block_attributes() (wp-includes/blocks.php, WP 7.1)
    s = json.dumps(a, ensure_ascii=False, separators=(',', ':'))
    s = s.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    out, i = [], 0
    # strtr semantics: longest match first, left to right, no re-scanning.
    pairs = [('\\\\', '\\u005c'), ('\\"', '\\u0022'), ('--', '\\u002d\\u002d'),
             ('<', '\\u003c'), ('>', '\\u003e'), ('&', '\\u0026')]
    while i < len(s):
        for k, v in pairs:
            if s.startswith(k, i):
                out.append(v); i += len(k); break
        else:
            out.append(s[i]); i += 1
    return ''.join(out)


def enc_js(a):  # @wordpress/blocks serializeAttributes() as bundled in Divi 5.13.1
    s = json.dumps(a, ensure_ascii=False, separators=(',', ':'))
    return (s.replace('--', '\\u002d\\u002d').replace('<', '\\u003c').replace('>', '\\u003e')
             .replace('&', '\\u0026').replace('\\"', '\\u0022'))


def enc_plain(a):
    return json.dumps(a, ensure_ascii=False, separators=(',', ':'))


def enc_ascii(a):
    return json.dumps(a, ensure_ascii=True, separators=(',', ':'))


STRUCT = {
    "section": {"builderVersion": "5.13.1", "modulePreset": ["default"]},
    "row": {"builderVersion": "5.13.1", "modulePreset": ["default"]},
    "column": {"module": {"advanced": {"type": {"desktop": {"value": "4_4"}}}},
               "builderVersion": "5.13.1", "modulePreset": ["default"]},
}


def page(enc, marker, selfclose=False, nl=False, wrap=False):
    j = '\n\n' if nl else ''
    o = lambda n, a: f'<!-- wp:divi/{n} {enc(a)} -->' + ('\n' if nl else '')
    c = lambda n: ('\n' if nl else '') + f'<!-- /wp:divi/{n} -->'
    leaf = (lambda n, a: f'<!-- wp:divi/{n} {enc(a)} /-->') if selfclose else \
           (lambda n, a: f'<!-- wp:divi/{n} {enc(a)} --><!-- /wp:divi/{n} -->')
    body = (o('section', STRUCT['section']) + o('row', STRUCT['row']) + o('column', STRUCT['column'])
            + leaf('heading', attrs('heading', marker + '-h')) + j + leaf('text', attrs('text', marker + '-t'))
            + c('column') + c('row') + c('section'))
    return f'<!-- wp:divi/placeholder -->{body}<!-- /wp:divi/placeholder -->' if wrap else body


VARIANTS = {
    'v1-php-canonical': dict(enc=enc_php),
    'v2-js-serializer': dict(enc=enc_js),
    'v3-plain-json': dict(enc=enc_plain),
    'v4-ascii-json': dict(enc=enc_ascii),
    'v5-vb-layout': dict(enc=enc_js, selfclose=True, nl=True, wrap=True),
    'v6-php-selfclose-wrapped': dict(enc=enc_php, selfclose=True, wrap=True),
}


def fixture_page():
    """The canonical escape-cases fixture: heading + text with R3's values, a text with EXTRA."""
    def leaf(name, a):
        return f'<!-- wp:divi/{name} {enc_php(a)} /-->'

    def wrap(name, a, inner):
        return f'<!-- wp:divi/{name} {enc_php(a)} -->{inner}<!-- /wp:divi/{name} -->'

    extra = {"content": {"innerContent": {"desktop": {"value": EXTRA}}},
             "module": {"meta": {"adminLabel": {"desktop": {"value": "Extra\tcases \u2028 --> \\ end"}}}},
             "css": {"desktop": {"value": {"mainElement": 'quotes: "\\201C" "\\201D";'}}},
             "builderVersion": "5.13.1", "modulePreset": ["default"]}
    column = wrap('column', STRUCT['column'], leaf('heading', attrs('heading', 'escape-cases-h'))
                  + leaf('text', attrs('text', 'escape-cases-t')) + leaf('text', extra))
    body = wrap('section', STRUCT['section'], wrap('row', STRUCT['row'], column))
    return f'<!-- wp:divi/placeholder -->{body}<!-- /wp:divi/placeholder -->'


if __name__ == '__main__':
    if sys.argv[1] == '--fixture':
        with open(sys.argv[2], 'w', encoding='utf-8', newline='') as fh:
            fh.write(fixture_page())
        print('wrote', sys.argv[2])
        sys.exit(0)
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, kw in VARIANTS.items():
        with open(os.path.join(out, name + '.html'), 'w', encoding='utf-8', newline='') as fh:
            fh.write(page(marker=name, **kw))
    with open(os.path.join(out, 'values.json'), 'w', encoding='utf-8') as fh:
        json.dump({'heading': HEADING, 'text': TEXT}, fh, ensure_ascii=False, indent=1)
    print('wrote', len(VARIANTS), 'variants to', out)
