#!/usr/bin/env python3
"""한글판에서 바뀐 그래픽 33개를 사용자의 한글판 롬에서 읽어 빌드 트리에 넣는다.

graphics_ko_addr.json에는 파일 경로와 한글판 롬 안의 위치만 있다.
.lz는 LZ77 헤더를 따라 압축 길이만큼 읽고 풀린 파일도 같이 쓴다. 그 밖의
파일은 기록된 길이(size)만큼 읽는다.

    python apply_korean_graphics.py KOREAN.gba TREE
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def lz_span(rom, off):
    """(압축 길이, 풀린 데이터) of the GBA LZ77 data at off."""
    if rom[off] != 0x10:
        raise ValueError('not LZ77 at %#x' % off)
    size = rom[off + 1] | (rom[off + 2] << 8) | (rom[off + 3] << 16)
    out = bytearray()
    pos = off + 4
    while len(out) < size:
        flags = rom[pos]
        pos += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                a, b = rom[pos], rom[pos + 1]
                pos += 2
                back = ((a & 0xF) << 8 | b) + 1
                for _ in range((a >> 4) + 3):
                    out.append(out[-back])
            else:
                out.append(rom[pos])
                pos += 1
    return pos - off, bytes(out[:size])


def main():
    rom = Path(sys.argv[1]).read_bytes()
    tree = Path(sys.argv[2])
    entries = json.load(open(HERE / 'graphics_ko_addr.json', encoding='utf-8'))
    for e in entries:
        dst = tree / e['path']
        off = int(e['kor'], 16)
        if e['path'].endswith('.lz'):
            n, raw = lz_span(rom, off)
            # 풀린 파일(.4bpp/.8bpp/.bin)을 먼저, .lz를 나중에 쓴다: make는 .lz가
            # 더 새것이면 영어판 원본에서 다시 압축하지 않는다. 풀린 .4bpp는
            # 복셀 생성기의 입력이기도 하다.
            dst.with_suffix('').write_bytes(raw)
            dst.write_bytes(rom[off:off + n])
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(rom[off:off + e['size']])
    print('korean graphics: %d files' % len(entries))


if __name__ == '__main__':
    main()
