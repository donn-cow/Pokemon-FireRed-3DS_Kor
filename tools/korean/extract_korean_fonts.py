#!/usr/bin/env python3
"""Copy the Korean ROM's five text fonts into a build tree (development builds).

Each font is 14 pages of 256 glyphs, 64 bytes per glyph (2bpp, the latin font
format), followed by a 0xE00-byte width table:
  page 0  single-byte codes (latin + 30 frequent syllables)
  page 1  CHAR_EXTRA_SYMBOL (0xF9 xx)
  pages 2-11  KS X 1001 Hangul, lead bytes 0x37-0x40
  pages 12-13 lead bytes 0x41-0x42 (symbols)

    python extract_korean_fonts.py KOREAN.gba OUTDIR
"""
import hashlib
import sys
from pathlib import Path

KOREAN_SHA1 = 'a79a61464f6b79d830af784969324945c5b73340'
FONTS = {  # name: (glyph table, width table)
    'small': (0xEDF800, 0xF17800),
    'normal_copy_1': (0xF18800, 0xF50800),
    'normal': (0xF51800, 0xF89800),
    'male': (0xF8A800, 0xFFA800),
    'female': (0xFC2800, 0xFFB800),
}
GLYPH_BYTES = 14 * 256 * 64
WIDTH_BYTES = 14 * 256


def main(rom_path, out_dir):
    rom = Path(rom_path).read_bytes()
    if hashlib.sha1(rom).hexdigest() != KOREAN_SHA1:
        sys.exit('not the supported Korean ROM (K260613)')
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, (glyphs, widths) in FONTS.items():
        (out / ('%s.kofont' % name)).write_bytes(rom[glyphs:glyphs + GLYPH_BYTES])
        (out / ('%s.kowidth' % name)).write_bytes(rom[widths:widths + WIDTH_BYTES])
        print(name, hex(glyphs), hex(widths))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
