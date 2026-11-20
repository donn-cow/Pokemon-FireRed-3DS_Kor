"""Recognise the player's ROM.

A clean Pokémon FireRed (USA) rev 1 dump (BPRE, 16 MiB, by SHA-1) is
recognised: the revision the port is built from. Building still requires a
recipe and executable made for the same ROM. A trimmed dump (trailing 0xFF
removed) is padded back before it is checked; a .zip holding a single .gba is
opened directly. The ROM is only ever read into memory: it is never copied,
written or sent anywhere.
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .errors import BuilderError

# 한글판 툴킷: 포켓몬스터 파이어레드 한글판(K260613) 롬만 받는다.
# 일본판 롬에 "20260613 포켓몬스터 파이어레드(J-K).xdelta"를 적용한 결과와 같다.
SUPPORTED_SHA1 = "a79a61464f6b79d830af784969324945c5b73340"
USA_SHA1 = "dd5945db9b930750cb39d00c84da8571feebf417"
JAPAN_SHA1 = "04139887b6cd8f53269aca098295b006ddba6cfe"
# The Korean ROM keeps the USA game code in its header (BPRE).
ROM_PROFILES = {"BPRE": SUPPORTED_SHA1}
ROM_SIZE = 16 * 1024 * 1024
KNOWN_CODES = {
    "BPRE": "Pokemon FireRed (USA, Rev 1)",
    "BPRJ": "Pokemon FireRed (Japan)",
    "BPRS": "Pokemon FireRed (Spain)",
    "BPRD": "Pokemon FireRed (Germany)",
    "BPRF": "Pokemon FireRed (France)",
    "BPRI": "Pokemon FireRed (Italy)",
    "BPGE": "Pokemon LeafGreen",
    "BPEE": "Pokemon Emerald",
    "AXVE": "Pokemon Ruby",
    "AXPE": "Pokemon Sapphire",
}


@dataclass
class Rom:
    data: bytes
    sha1: str
    title: str
    code: str
    source: Path


def _unzip(data: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith((".gba", ".agb", ".bin"))]
        if len(names) != 1:
            raise BuilderError("The ZIP file must contain exactly one .gba file.", code="rom_zip_contents")
        return zf.read(names[0])


def header(data: bytes) -> tuple[str, str]:
    if len(data) < 0xC0:
        return "", ""
    title = data[0xA0:0xAC].split(b"\0")[0].decode("ascii", "replace")
    code = data[0xAC:0xB0].decode("ascii", "replace")
    return title, code


def check_rom_bytes(data: bytes, source: Path, supported: tuple[str, ...] | None = None) -> Rom:
    """Recognise ROM bytes already in memory (the web builder has no file)."""
    if source.suffix.lower() == ".zip":
        try:
            data = _unzip(data)
        except zipfile.BadZipFile as exc:
            raise BuilderError("The ROM file could not be read.", str(exc), code="rom_unreadable") from exc
    if len(data) > ROM_SIZE:
        raise BuilderError("This file is larger than a GBA cartridge; it is not the supported ROM.",
                           code="rom_too_large")
    if len(data) < ROM_SIZE:
        # A trimmed dump: the cartridge's trailing 0xFF fill was cut off.
        data = data + b"\xff" * (ROM_SIZE - len(data))
    title, code = header(data)
    sha1 = hashlib.sha1(data).hexdigest()
    if supported is None:
        supported = tuple(ROM_PROFILES.values())
    if sha1 not in supported and sha1 == USA_SHA1:
        raise BuilderError("미국판(USA Rev 1) 롬입니다. 이 툴킷은 한글판 전용입니다.",
                           "미국판은 원래 FireRed3DS 툴킷을 사용하세요.", code="rom_wrong_game")
    if sha1 not in supported and sha1 == JAPAN_SHA1:
        raise BuilderError("일본판 롬입니다. 한글 패치를 먼저 적용하세요.",
                           "일본판 롬에 \"20260613 포켓몬스터 파이어레드(J-K).xdelta\"를 적용한 롬을 "
                           "선택하세요.", code="rom_wrong_game")
    if sha1 not in supported:
        raise BuilderError("지원하는 한글판 롬이 아닙니다.",
                           "포켓몬스터 파이어레드 한글판(K260613), SHA-1 %s 롬이 필요합니다."
                           % SUPPORTED_SHA1, code="rom_unsupported")
    if sha1 not in supported:
        codes = [c for c, s in ROM_PROFILES.items() if s in supported] or ["BPRE"]
        names = " or ".join(KNOWN_CODES[c] for c in codes)
        what = KNOWN_CODES.get(code)
        if what and code not in codes:
            raise BuilderError("This ROM is %s. Only %s is supported." % (what, names),
                               code="rom_wrong_game")
        if code in codes:
            raise BuilderError(
                "This is a %s ROM, but not an unmodified one." % what,
                "Patched, hacked or bad dumps are not supported. Use a clean dump of your cartridge "
                "(SHA-1 %s)." % ROM_PROFILES[code], code="rom_modified")
        raise BuilderError("This file is not the supported ROM.",
                           "Expected %s, SHA-1 %s." % (names, " or ".join(ROM_PROFILES[c] for c in codes)),
                           code="rom_unsupported")
    return Rom(data=data, sha1=sha1, title=title, code=code, source=source)


def load_rom(path: Path, supported: tuple[str, ...] | None = None) -> Rom:
    path = Path(path)
    if not path.is_file():
        raise BuilderError("The ROM file was not found:\n%s" % path.name, code="rom_not_found")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise BuilderError("The ROM file could not be read.", str(exc), code="rom_unreadable") from exc
    return check_rom_bytes(data, path, supported)
