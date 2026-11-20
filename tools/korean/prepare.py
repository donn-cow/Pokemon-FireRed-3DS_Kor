#!/usr/bin/env python3
"""Make a bootstrapped tree (tools/bootstrap.py) the Korean edition, from the
player's own Korean ROM.

    python tools/korean/prepare.py --rom "Pokemon FireRed (K260613).gba" [--tree build/upstream]

The repository holds no Korean text or graphics: only where each string and
graphic is in the Korean ROM (strings_ko_addr.json, graphics_ko_addr.json).
This reads them from the ROM and writes them into the tree:

1. the strings (apply_korean_strings.py): charmap + .string / _() / JSON,
   each re-encoded and checked against the ROM's bytes;
2. the strings the port added (port_strings_ko.py: party EXP, Mega Evolution);
3. Easy Chat word order and the Trainer Tower data (struct_easychat_tower.py);
4. the Easy Chat consonant lists (gen_easychat_by_letter_ko.py);
5. the 33 graphics the Korean ROM changed (apply_korean_graphics.py);
6. the five Korean fonts (extract_korean_fonts.py) and the particle tables
   (gen_korean_tables.py).

Then build with KOREAN=1:  make -C build/upstream/3ds_port KOREAN=1
Run it once per bootstrapped tree; bootstrap --clean starts again.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KOREAN_SHA1 = "a79a61464f6b79d830af784969324945c5b73340"
MARKER = ".firered3ds-korean"


def run(*args):
    cmd = [sys.executable, *[str(a) for a in args]]
    print("+ " + " ".join(cmd[1:]), flush=True)
    subprocess.run(cmd, check=True)


def strings_from_rom(rom: bytes, out: Path) -> int:
    """strings_ko_addr.json + the ROM -> the rows apply_korean_strings.py reads."""
    rows = json.load(open(HERE / "strings_ko_addr.json", encoding="utf-8"))
    n = 0
    for r in rows:
        if "kor_addr" not in r:
            continue
        a = int(r["kor_addr"], 16)
        end = rom.index(0xFF, a)
        if "kor_max" in r:
            end = min(end, a + r["kor_max"])
            r["kor_hex"] = rom[a:end].hex() + "ff"
        else:
            r["kor_hex"] = rom[a:end + 1].hex()
        n += 1
    json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rom", type=Path, required=True, help="Pokemon FireRed Korean (K260613)")
    ap.add_argument("--tree", type=Path, default=ROOT / "build" / "upstream")
    args = ap.parse_args()

    rom = args.rom.read_bytes()
    if hashlib.sha1(rom).hexdigest() != KOREAN_SHA1:
        sys.exit("prepare: not the Korean ROM K260613 (SHA-1 %s)" % KOREAN_SHA1)
    tree = args.tree.resolve()
    if not (tree / "charmap.txt").is_file():
        sys.exit("prepare: %s is not a bootstrapped tree (run tools/bootstrap.py first)" % tree)
    marker = tree / MARKER
    if marker.exists():
        print("prepare: %s is already the Korean edition" % tree)
        return 0

    with tempfile.TemporaryDirectory(prefix="fr3ds-ko-") as tmp:
        strings = Path(tmp) / "strings_ko.json"
        print("prepare: %d strings from the ROM" % strings_from_rom(rom, strings))
        run(HERE / "apply_korean_strings.py", tree, "--strings", strings)
    run(HERE / "port_strings_ko.py", tree)
    run(HERE / "struct_easychat_tower.py", args.rom, tree, "--write")
    run(HERE / "gen_easychat_by_letter_ko.py", args.rom, tree / "src/data/easy_chat/easy_chat_words_by_letter_ko.h")
    run(HERE / "apply_korean_graphics.py", args.rom, tree)
    run(HERE / "extract_korean_fonts.py", args.rom, tree / "graphics/fonts/korean")
    run(HERE / "gen_korean_tables.py", tree / "include/korean_text_tables.h")
    marker.write_text(KOREAN_SHA1 + "\n", encoding="ascii")
    print("prepare: done; build with  make -C %s KOREAN=1" % (tree / "3ds_port"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
