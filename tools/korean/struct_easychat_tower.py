#!/usr/bin/env python3
"""간이회화 단어와 트레이너 타워 문자열을 롬의 데이터 구조에서 직접 읽어 대응한다.

문장 비교(map2/walk) 대신 구조를 쓴다:
- 간이회화: sEasyChatGroups 표(그룹마다 {단어 배열, 단어 수, 쓸 수 있는 수})와
  단어 배열({text, alphabeticalOrder, enabled}, 12바이트)을 두 롬에서 읽는다.
  단어 번호(그룹, 칸)가 같으면 같은 단어다. 세이브와 대사는 이 번호로 저장된다.
- 트레이너 타워: TrainerTowerFloor(0x3E0바이트) 32개가 연속으로 있다.
  트레이너 이름(11바이트)과 포켓몬 닉네임(11바이트)이 구조 안에 들어 있다.

미국판 롬으로 읽은 영어가 소스의 영어와 같은지 확인한 뒤에만 한글을 쓴다.

    python struct_easychat_tower.py KOREAN.gba TREE [--usa USA.gba] [--strings strings_ko.json] [--write]

--usa 없이 실행하면 미국판과의 대조를 건너뛴다(빌드 준비 단계: 대조는 표를 만들 때 이미 했다).
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import apply_korean_strings as A  # noqa: E402

EC_TABLE = {'usa': 0x3ECF44, 'kor': 0x3ECDD8}
TOWER = {'usa': 0x47AC0C, 'kor': 0x478608}
FLOOR_SIZE, TRAINER_SIZE, MON_SIZE = 0x3E0, 328, 44
NUM_FLOORS = 32


def cstr(rom, off, limit=None):
    end = rom.index(0xFF, off)
    if limit is not None:
        end = min(end, off + limit)
    return rom[off:end]


def ptr(rom, off):
    p = struct.unpack_from('<I', rom, off)[0]
    return p - 0x08000000


def easy_chat(U, K, tree, chars):
    src = (tree / 'src/data/easy_chat/easy_chat_groups.h').read_text(encoding='utf-8')
    groups = re.findall(r'(valueList|words) = (\w+)\},\s*\.numWords = (\d+),\s*\.numEnabledWords = (\d+)', src)
    out = []           # (file, symbol, usa_bytes, kor_bytes, order, enabled)
    problems = []
    for gi, (kind, gname, n, _) in enumerate(groups):
        if kind != 'words':
            continue
        n = int(n)
        ua, ka = ptr(U, EC_TABLE['usa'] + gi * 8), ptr(K, EC_TABLE['kor'] + gi * 8)
        hfile = 'src/data/easy_chat/easy_chat_group_%s.h' % re.sub(r'(?<!^)(?=[A-Z])', '_', gname.replace('sEasyChatGroup_', '')).lower()
        htext = (tree / hfile).read_text(encoding='utf-8')
        arr = htext[htext.index('struct EasyChatWordInfo %s[]' % gname):]
        syms = re.findall(r'\.text = (\w+)', arr)
        if len(syms) != n:
            problems.append((hfile, 'count', len(syms), n))
            continue
        for i, sym in enumerate(syms):
            ut, uo, ue = struct.unpack_from('<Iii', U, ua + i * 12)
            kt, ko, ke = struct.unpack_from('<Iii', K, ka + i * 12)
            out.append((hfile, sym, cstr(U, ut - 0x08000000), cstr(K, kt - 0x08000000), ko, ke, uo, ue,
                        kt - 0x08000000))
    return out, problems


def tower(U, K):
    """(floor, trainer, mon or None, usa_bytes, kor_bytes) for every slot."""
    rows = []
    for fl in range(NUM_FLOORS):
        for t in range(3):
            base = 4 + t * TRAINER_SIZE
            uo, ko = TOWER['usa'] + fl * FLOOR_SIZE + base, TOWER['kor'] + fl * FLOOR_SIZE + base
            rows.append((fl, t, None, cstr(U, uo, 11), cstr(K, ko, 11), ko))
            for m in range(6):
                d = 0x40 + m * MON_SIZE + 0x20
                rows.append((fl, t, m, cstr(U, uo + d, 11), cstr(K, ko + d, 11), ko + d))
    return rows


TOKEN = re.compile(r'DUMMY_TOWER_TEAM\(|DUMMY_TOWER_MON\(|\.name = _\("((?:[^"\\]|\\.)*)"\)|\.nickname = _\("((?:[^"\\]|\\.)*)"\)')


def tower_slots(text):
    """Source literals of each floor/trainer/mon slot, in the ROM's order:
    {(floor, trainer, mon|None): (start, end, literal, line)}."""
    slots = {}
    floors = [m.start() for m in re.finditer(r'static const struct TrainerTowerFloor \w+ = \{', text)]
    floors.append(len(text))
    for fl in range(len(floors) - 1):
        body_start = text.index('.trainers = {', floors[fl], floors[fl + 1])
        t, m = -1, 0
        for tok in TOKEN.finditer(text, body_start, floors[fl + 1]):
            s = tok.group(0)
            if s.startswith('DUMMY_TOWER_TEAM'):
                t += 1
                m = 6
            elif s.startswith('.name'):
                t += 1
                m = 0
                slots[(fl, t, None)] = (tok.start(1), tok.end(1), tok.group(1), text.count('\n', 0, tok.start()) + 1)
            elif s.startswith('DUMMY_TOWER_MON'):
                m += 1
            else:
                slots[(fl, t, m)] = (tok.start(2), tok.end(2), tok.group(2), text.count('\n', 0, tok.start()) + 1)
                m += 1
    return slots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('kor', type=Path)
    ap.add_argument('tree', type=Path)
    ap.add_argument('--usa', type=Path)
    ap.add_argument('--strings', type=Path)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    K = args.kor.read_bytes()
    U = args.usa.read_bytes() if args.usa else None
    check = U is not None
    if U is None:
        # 대조 없이: 미국판 자리에 한글판을 읽는다(영어 비교는 건너뛴다)
        U = K
        EC_TABLE['usa'], TOWER['usa'] = EC_TABLE['kor'], TOWER['kor']

    chars, consts = A.load_charmap(args.tree / 'charmap.txt')
    rows = json.load(open(args.strings, encoding='utf-8')) if args.strings else None

    def json_set(file, key, kb, addr, by_line=False, maxlen=None):
        if rows is None:
            return
        for r in rows:
            if r['file'] == file and (r['line'] == key if by_line else r['label'] == key):
                r['kor_hex'] = kb.hex() + 'ff'
                r['ko'] = A.to_source(kb, chars)
                r['via'] = 'struct'
                r['kor_addr'] = hex(addr)
                if maxlen:
                    r['kor_max'] = maxlen
                r.pop('rejected_ko', None)
                r.pop('rejected_hex', None)
                return

    # -- 간이회화 ----------------------------------------------------------
    words, problems = easy_chat(U, K, args.tree, chars)
    print('간이회화 단어', len(words), '문제', problems)
    byfile = {}
    for w in words:
        byfile.setdefault(w[0], []).append(w)
    changed = 0
    for hfile, ws in byfile.items():
        path = args.tree / hfile
        text = path.read_text(encoding='utf-8')
        for _, sym, ub, kb, ko, ke, uo, ue, kaddr in ws:
            m = re.search(r'\b%s\[\] = _\("((?:[^"\\]|\\.)*)"\);' % re.escape(sym), text)
            if not m:
                problems.append((hfile, sym, 'no literal'))
                continue
            if check and rows is not None:
                en = next((r['en'][:-1] for r in rows if r['file'] == hfile and r['label'] == sym), None)
                if en is not None and A.encode(en + '$', chars, consts) != ub + b'\xff':
                    problems.append((hfile, sym, 'usa mismatch', en))
                    continue
            new = A.to_source(kb, chars)
            if A.encode(new + '$', chars, consts) != kb + b'\xff':
                problems.append((hfile, sym, 'roundtrip'))
                continue
            if m.group(1) != new:
                changed += 1
                text = text[:m.start(1)] + new + text[m.end(1):]
            # 한글판의 가나다 순서와 사용 여부도 따른다
            em = re.search(r'\.text = %s,\s*\.alphabeticalOrder = (-?\w+),\s*\.enabled = (\w+)' % re.escape(sym), text)
            if em and (em.group(1), em.group(2)) != (str(ko), 'TRUE' if ke else 'FALSE'):
                text = (text[:em.start(1)] + str(ko) + text[em.end(1):em.start(2)]
                        + ('TRUE' if ke else 'FALSE') + text[em.end(2):])
            json_set(hfile, sym, kb, kaddr)
        if args.write:
            path.write_text(text, encoding='utf-8', newline='\n')
    print('간이회화 바뀐 단어', changed)

    # -- 트레이너 타워 -------------------------------------------------------
    rel = 'src/trainer_tower_sets.c'
    path = args.tree / rel
    text = path.read_text(encoding='utf-8')
    slots = tower_slots(text)
    edits, checked, tchanged = [], 0, 0
    for fl, t, m, ub, kb, kaddr in tower(U, K):
        slot = slots.get((fl, t, m))
        if slot is None:
            if ub:
                problems.append((rel, (fl, t, m), 'slot missing'))
            continue
        start, end, lit, line = slot
        # 미국판 롬의 영어와 소스 영어가 같은지(소스가 이미 한글이면 줄 번호의 영어로) 확인
        en = None
        if check and rows is not None:
            en = next((r['en'][:-1] for r in rows if r['file'] == rel and r['line'] == line), None)
        if en is not None and A.encode(en + '$', chars, consts) != ub + b'\xff':
            problems.append((rel, (fl, t, m), 'usa mismatch', en))
            continue
        checked += 1
        new = A.to_source(kb, chars)
        if lit != new:
            tchanged += 1
            edits.append((start, end, new))
        json_set(rel, line, kb, kaddr, by_line=True, maxlen=11)
    for start, end, new in sorted(edits, reverse=True):
        text = text[:start] + new + text[end:]
    if args.write:
        path.write_text(text, encoding='utf-8', newline='\n')
    print('트레이너 타워 칸', checked, '바뀐 문자열', tchanged)

    if rows is not None and args.write:
        json.dump(rows, open(args.strings, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for p in problems:
        print('  문제', p)
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
