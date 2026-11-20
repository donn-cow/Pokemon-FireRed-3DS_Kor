#!/usr/bin/env python3
"""Put the Korean ROM's strings into a pokefirered source tree.

Reads tools/korean/strings_ko_addr.json (via prepare.py) (decomp string -> exact Korean bytes) and
rewrites, in TREE:
  - charmap.txt: + the 2350 KS X 1001 syllables (2 bytes) and particle constants
  - data/**/*.inc|*.s  `.string` runs
  - src/**/*.c|*.h     `_("...")` literals
  - src/data/items.json, src/data/region_map/region_map_sections.json
Every rewritten string is re-encoded with the new charmap and checked against
the Korean bytes, so the build reproduces them exactly.

    python apply_korean_strings.py TREE [--report OUT.json]
"""
import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BS = chr(92)
SKIP_FILES = ('src/keyboard_text.c',)           # naming-screen layouts stay latin
SKIP_SUFFIX = ('pokedex_text_lg.h',)

JOSA = {0xEE: 'JOSA_WA_GWA', 0xEF: 'JOSA_EUN_NEUN', 0xF0: 'JOSA_EUL_REUL',
        0xF1: 'JOSA_I_GA', 0xF2: 'JOSA_I', 0xF4: 'JOSA_EU'}


def ks_char(idx):
    r, c = divmod(idx, 94)
    return bytes([0xB0 + r, 0xA1 + c]).decode('euc_kr')


def ks_bytes(idx):
    return bytes([0x37 + idx // 239, idx % 239 + 1])


# ---------------------------------------------------------------- charmap
def load_charmap(path):
    chars, consts = {}, {}
    for line in open(path, encoding='utf-8'):
        line = line.split('@')[0].strip()
        if '=' not in line:
            continue
        lhs, rhs = [x.strip() for x in line.split('=', 1)]
        try:
            val = bytes(int(x, 16) for x in rhs.split())
        except ValueError:
            continue
        if lhs.startswith("'") and lhs.endswith("'") and len(lhs) >= 3:
            ch = lhs[1:-1]
            if ch == BS + "'":
                ch = "'"
            chars.setdefault(ch, val)
        else:
            consts.setdefault(lhs, val)
    return chars, consts


def extend_charmap(path):
    text = open(path, encoding='utf-8').read()
    if 'KOREAN_K260613' in text:
        return
    lines = ['', '@ KOREAN_K260613: KS X 1001 Hangul as the Korean ROM encodes it',
             '@ (lead 0x37 + idx / 239, trail idx % 239 + 1)']
    for idx in range(2350):
        b = ks_bytes(idx)
        lines.append("'%s' = %02X %02X" % (ks_char(idx), b[0], b[1]))
    lines.append('@ particles chosen at run time from the previous syllable')
    for t, name in JOSA.items():
        lines.append('%s = 41 %02X' % (name, t))
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


def encode(s, chars, consts):
    out = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c == BS:
            nxt = s[i + 1]
            out += chars['"'] if nxt == '"' else chars[BS + nxt]
            i += 2
        elif c == '{':
            j = s.index('}', i)
            for tok in s[i + 1:j].split():
                out += consts[tok] if tok in consts else bytes([int(tok, 0) & 0xFF])
            i = j + 1
        elif c == '$':
            out.append(0xFF)
            i += 1
        else:
            out += chars[c]
            i += 1
    return bytes(out)


# Single-byte characters written as themselves (others become {0xNN}).
SAFE = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 !?.,-:;/()&+=%'…‘’“”♂♀é")


def to_source(kb, chars):
    """Korean bytes (incl. FF) -> string-literal source text (without $)."""
    rev = {}
    for ch, v in chars.items():
        if len(v) == 1 and ch in SAFE:
            rev.setdefault(v[0], ch)
    out = []
    i = 0
    n = len(kb)
    while i < n:
        b = kb[i]
        if b == 0xFF:
            break
        if b == 0xFE:
            out.append(BS + 'n'); i += 1; continue
        if b == 0xFB:
            out.append(BS + 'p'); i += 1; continue
        if b == 0xFA:
            out.append(BS + 'l'); i += 1; continue
        if 0x37 <= b <= 0x40 and i + 1 < n:
            t = kb[i + 1]
            idx = (b - 0x37) * 239 + t - 1
            if 1 <= t <= 0xEF and idx < 2350:
                out.append(ks_char(idx)); i += 2; continue
        if b == 0x41 and i + 1 < n:
            t = kb[i + 1]
            out.append('{%s}' % JOSA[t] if t in JOSA else '{0x41 0x%02X}' % t)
            i += 2
            continue
        if b in (0xFC,):  # ext control code with its arguments, kept raw
            L = [1, 2, 2, 2, 4, 2, 2, 1, 2, 1, 1, 3, 2, 2, 2, 1, 3, 2, 2, 2, 2, 1, 1, 1, 1][kb[i + 1]]
            out.append('{' + ' '.join('0x%02X' % x for x in kb[i:i + 1 + L]) + '}')
            i += 1 + L
            continue
        if b in (0xFD, 0xF7, 0xF8, 0xF9) and i + 1 < n:
            out.append('{0x%02X 0x%02X}' % (b, kb[i + 1])); i += 2; continue
        if b in rev:
            out.append(rev[b]); i += 1; continue
        out.append('{0x%02X}' % b)
        i += 1
    return ''.join(out)


# ---------------------------------------------------------------- parsers
STR_RE = re.compile(r'"((?:[^"' + BS + BS + r']|' + BS + BS + r'.)*)"')
C_RE = re.compile(r'_\(\s*((?:"(?:[^"' + BS + BS + r']|' + BS + BS + r'.)*"\s*)+)\)', re.S)


def asm_runs(lines):
    """[(start_line, end_line, english)] for `.string` runs ending with $."""
    runs, start, buf = [], None, ''
    for n, line in enumerate(lines):
        m = re.match(r'^\s*\.string\s+(.*)$', line)
        if m:
            if start is None:
                start = n
            for sm in STR_RE.finditer(m.group(1)):
                buf += sm.group(1)
            if buf.endswith('$'):
                runs.append((start, n, buf))
                start, buf = None, ''
        elif re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)::?\s*$', line.split('@')[0]):
            start, buf = None, ''
    return runs


def c_literals(text):
    return [(m.start(), m.end(), ''.join(sm.group(1) for sm in STR_RE.finditer(m.group(1))) + '$')
            for m in C_RE.finditer(text)]


def split_source(src, limit=400):
    """Split literal text at paragraph/line breaks so each piece stays short."""
    parts, cur = [], ''
    for tok in re.split(r'(\\[npl])', src):
        cur += tok
        if tok in (BS + 'p', BS + 'n', BS + 'l') and len(cur.encode('utf-8')) > 0:
            if tok == BS + 'p' or len(cur) > limit:
                parts.append(cur)
                cur = ''
    if cur or not parts:
        parts.append(cur)
    return parts


def patch_region_templates(tree):
    """region_map_sections templates: key names on `name_en`, print `name`."""
    for rel in ('src/data/region_map/region_map_sections.strings.json.txt',
                'src/data/region_map/region_map_sections.entries.json.txt'):
        p = tree / rel
        t = open(p, encoding='utf-8').read()
        if 'name_en' in t:
            continue
        t = t.replace('_("{{ map_section.name }}")', '_("{{ map_section.@KO@ }}")')
        t = re.sub(r'map_section\.name\b(?!_)', 'map_section.name_en', t)
        t = t.replace('existsIn(map_section, "name")', 'existsIn(map_section, "name_en")')
        t = t.replace('@KO@', 'name')
        open(p, 'w', encoding='utf-8', newline='\n').write(t)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tree', type=Path)
    ap.add_argument('--strings', type=Path, default=HERE.parent / 'strings_ko.json')
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    tree = args.tree

    extend_charmap(tree / 'charmap.txt')
    chars, consts = load_charmap(tree / 'charmap.txt')

    rows = json.load(open(args.strings, encoding='utf-8'))
    byfile = collections.OrderedDict()
    for r in rows:
        byfile.setdefault(r['file'], []).append(r)

    stats = collections.Counter()
    problems = []

    def korean_for(r):
        if 'kor_hex' not in r or r['file'].endswith(SKIP_SUFFIX) or r['file'] in SKIP_FILES:
            return None
        kb = bytes.fromhex(r['kor_hex'])
        if kb == encode(r['en'], chars, consts):
            return None                       # unchanged
        src = to_source(kb, chars)
        if encode(src + '$', chars, consts) != kb:
            problems.append((r['file'], r['label'], 'roundtrip'))
            return None
        return src

    def match_rows(file_rows, parsed):
        """Pair parsed literals with rows of the same English text, in order."""
        pairs, j = [], 0
        for p in parsed:
            k = j
            while k < len(file_rows) and file_rows[k]['en'] != p[-1]:
                k += 1
            if k < len(file_rows):
                pairs.append((p, file_rows[k]))
                j = k + 1
        return pairs

    for rel, frows in byfile.items():
        path = tree / rel
        if not path.exists():
            stats['missing_file'] += 1
            continue
        if rel.endswith('.json'):
            data = json.load(open(path, encoding='utf-8'))
            lst = data.get('items') or data.get('map_sections') or []
            if 'map_sections' in data:
                # Variable names and de-duplication stay on the English name
                # (region_map.c refers to sMapsecName_<ENGLISH>); see
                # patch_region_templates.
                for it in lst:
                    if 'name' in it and 'name_en' not in it:
                        it['name_en'] = it['name']
                patch_region_templates(tree)
            keyed = {}
            for r in frows:
                ident, key = (r['label'] or ':').rsplit(':', 1)
                keyed[(ident, key)] = r
            changed = 0
            for i, it in enumerate(lst):
                ident = it.get('itemId') or it.get('id') or str(i)
                for key in ('english', 'description_english', 'name'):
                    r = keyed.get((ident, key))
                    if r and isinstance(it.get(key), str):
                        src = korean_for(r)
                        if src is not None:
                            it[key] = src
                            changed += 1
            if changed:
                with open(path, 'w', encoding='utf-8', newline='\n') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    f.write('\n')
            stats['json'] += changed
            continue

        text = open(path, encoding='utf-8', errors='surrogateescape').read()
        if rel.endswith(('.inc', '.s')):
            lines = text.split('\n')
            runs = asm_runs(lines)
            repl = {}
            for (start, end, en), r in match_rows(frows, runs):
                src = korean_for(r)
                if src is None:
                    continue
                indent = re.match(r'^(\s*)', lines[start]).group(1)
                pieces = split_source(src)
                new = ['%s.string "%s"' % (indent, p) for p in pieces[:-1]]
                new.append('%s.string "%s$"' % (indent, pieces[-1]))
                repl[start] = (end, new)
            if repl:
                out, n = [], 0
                while n < len(lines):
                    if n in repl:
                        end, new = repl[n]
                        out += new
                        n = end + 1
                    else:
                        out.append(lines[n])
                        n += 1
                open(path, 'w', encoding='utf-8', errors='surrogateescape', newline='\n').write('\n'.join(out))
            stats['asm'] += len(repl)
        else:
            lits = c_literals(text)
            edits = []
            for (s, e, en), r in match_rows(frows, lits):
                src = korean_for(r)
                if src is None:
                    continue
                if len(encode(src + '$', chars, consts)) > 1000:
                    pieces = split_source(src)
                    lit = '_(' + ' '.join('"%s"' % p for p in pieces) + ')'
                else:
                    lit = '_("%s")' % src
                edits.append((s, e, lit))
            for s, e, lit in reversed(edits):
                text = text[:s] + lit + text[e:]
            if edits:
                open(path, 'w', encoding='utf-8', errors='surrogateescape', newline='\n').write(text)
            stats['c'] += len(edits)

    print(dict(stats), 'problems', len(problems))
    for p in problems[:20]:
        print('  ', p)
    if args.report:
        json.dump({'stats': stats, 'problems': problems}, open(args.report, 'w'), indent=1)


if __name__ == '__main__':
    main()
