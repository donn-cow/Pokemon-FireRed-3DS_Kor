<p align="center">
  <img src="3ds_port/assets/artwork/FireRed%203DS.png" alt="FireRed 3DS" width="560">
</p>

> **한국어판 포크입니다.** 이 저장소는
> [NachoGonzalez2001/Pokemon-FireRed-3DS](https://github.com/NachoGonzalez2001/Pokemon-FireRed-3DS)를
> 포크해서 **포켓몬스터 파이어레드 한글판(K260613)** 롬으로 실행할 수 있게 한 비공식 버전입니다.
> 원본 프로젝트와 별개로 관리되며, 원본 제작자에게 이 포크에 관한 문의를 하지 말아 주세요.

## 한국어판 (FireRed3DS-KO)

- 한글 대사·메뉴·전투, 한글판 롬의 글꼴(기본·남자·여자 대사 글꼴)과 조사 처리
- 아래 화면 메뉴의 한국어화
- 한글판에서 바뀐 그래픽(타이틀 로고 등) 반영
- 간이회화 가나다(자음) 모드, 트레이너 타워 한글 데이터
- 포트가 새로 넣은 문장(파티 경험치, 메가진화 이름·특성·메시지)의 한국어 번역
- 실행 파일, 세이브, 설정, 데이터가 모두 SD 카드의 `/3ds/firered3ds-ko/` 한 폴더에 있어서 영어판과 섞이지 않습니다.
- 홈 메뉴용 CIA 포워더(영어판 포워더와 함께 설치 가능)

**이 저장소와 배포 파일에는 게임도, 한글판의 번역문이나 그래픽도 들어 있지 않습니다.**
빌더가 사용자의 한글판 롬에서 직접 만듭니다. 저장소에는 각 문자열과 그래픽이
한글판 롬의 어디에 있는지(주소)만 들어 있습니다.

### 준비물

- 커스텀 펌웨어(Luma3DS)와 홈브류 런처가 설치된 3DS / 2DS 계열 기기
- 포켓몬스터 파이어레드 한글판 롬 (K260613), SHA-1 `a79a61464f6b79d830af784969324945c5b73340`
  (일본판 롬에 한글 패치 `20260613 포켓몬스터 파이어레드(J-K).xdelta`를 적용한 롬)

### 설치

1. [Releases](../../releases)에서 `FireRed3DS-KO-v…-Windows.zip`을 받아 압축을 풉니다.
2. `FireRed3DS-Builder.exe`를 실행하고 한글판 롬과 SD 카드를 고른 뒤 **설치**를 누릅니다.
3. 홈브류 런처에서 "Pokemon FireRed 3DS KO"를 실행합니다.
   홈 메뉴에서 실행하려면 `FireRed3DS-KO-Forwarder.cia`를 FBI 등으로 설치합니다.

원본의 웹 빌더는 미국판 전용이라 한국어판에는 쓸 수 없습니다.

### 빌드 (개발자)

```sh
python tools/bootstrap.py                                   # 디컴프 + patches/ (0031: 한글 엔진)
python tools/korean/prepare.py --rom "Pokemon FireRed (K260613).gba"   # 한글판 롬에서 문자열·그래픽·글꼴
make -C build/upstream tools generated
make -C build/upstream/3ds_port KOREAN=1 all                # 개발용(데이터 포함, 배포 금지)
make -C build/upstream/3ds_port KOREAN=1 release            # 실행 파일만
python tools/build_release.py --version 0.5.2-ko --rom "Pokemon FireRed (K260613).gba" --tree build/upstream
```

| 경로 | 내용 |
|---|---|
| `patches/pokefirered/0031-korean-text-engine.patch` | 디컴프 쪽 한글 엔진(`KOREAN_TEXT`) |
| `tools/korean/` | 한글판 롬에서 데이터를 읽어 트리에 넣는 도구와 주소 목록 |
| `3ds_port/src/fr_korean_ui.h` | 아래 화면 메뉴 번역 |
| `3ds_port/include/3ds_paths.h` | SD 카드 폴더(`KOREAN=1`이면 `firered3ds-ko`) |

### 크레딧 (한국어판)

- 원본 포트: [NachoGonzalez2001](https://github.com/NachoGonzalez2001) — Pokémon FireRed 3DS
- 한글 번역·그래픽·글꼴: 포켓몬스터 파이어레드 한글 패치(20260613) 제작자분들. 이 저장소에는 포함되어 있지 않고 사용자의 롬에서만 읽습니다.
- 한국어판 포팅: [donn-cow](https://github.com/donn-cow)

---

# Pokémon FireRed 3DS (voxel)

A native Nintendo 3DS port of Pokémon FireRed that uses both screens, with an
HD-2D style voxel world. It is built from the
[pret/pokefirered](https://github.com/pret/pokefirered) decompilation on the
technical groundwork of
[Pokémon Emerald 3Ds Dual Screen](https://github.com/ZallaxDev/pokeemerald-3Ds-dualscreen).

**This repository and its releases do not contain the game.** You need your
own dump of your own Pokémon FireRed cartridge.

**Website and web builder:
[nachogonzalez2001.github.io/Pokemon-FireRed-3DS](https://nachogonzalez2001.github.io/Pokemon-FireRed-3DS/)**,
to build the game in your browser from your ROM, with nothing to install. Its
[guide](https://nachogonzalez2001.github.io/Pokemon-FireRed-3DS/guide.html)
lists where every wild Pokémon lives in this version.

## Screenshots

<p align="center">
  <img src="docs/screenshots/dual-screen.png" alt="Cerulean City with Charmeleon following on the top screen, the region map, party and menu on the bottom screen" width="400">
</p>

<table>
  <tr>
    <td><img src="docs/screenshots/route-25.png" alt="Route 25 with Eevee following"><br><sub>Route 25</sub></td>
    <td><img src="docs/screenshots/vermilion.png" alt="Vermilion City harbour with Squirtle following"><br><sub>Vermilion City, morning</sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/cerulean-dusk.png" alt="Cerulean City at dusk with Psyduck following"><br><sub>Cerulean City, dusk</sub></td>
    <td><img src="docs/screenshots/lavender-night.png" alt="Lavender Town at night with Gengar following"><br><sub>Lavender Town, night</sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/cinnabar-dusk.png" alt="Cinnabar Island at dusk with Arcanine following"><br><sub>Cinnabar Island, dusk</sub></td>
    <td><img src="docs/screenshots/fuchsia.png" alt="Fuchsia City with Snorlax following"><br><sub>Fuchsia City</sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/viridian-forest.png" alt="Viridian Forest with Butterfree following"><br><sub>Viridian Forest</sub></td>
    <td><img src="docs/screenshots/mt-moon.png" alt="Mt. Moon with Clefairy following"><br><sub>Mt. Moon</sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/silph-co.png" alt="Silph Co. with Porygon following"><br><sub>Silph Co.</sub></td>
    <td><img src="docs/screenshots/pokemon-mansion.png" alt="Pokémon Mansion with Growlithe following"><br><sub>Pokémon Mansion</sub></td>
  </tr>
</table>

**Day and night.** Outdoors the light follows the console's clock (or a day
that passes in 24 minutes, or stays off - OPTIONS > DAY/NIGHT):

<table>
  <tr>
    <td><img src="docs/screenshots/pallet-dawn.png" alt="Pallet Town at dawn"><br><sub>Dawn</sub></td>
    <td><img src="docs/screenshots/pallet-day.png" alt="Pallet Town by day"><br><sub>Day</sub></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/pallet-dusk.png" alt="Pallet Town at dusk"><br><sub>Dusk</sub></td>
    <td><img src="docs/screenshots/pallet-night.png" alt="Pallet Town at night"><br><sub>Night</sub></td>
  </tr>
</table>

## Features

- **The whole game, native on the 3DS**, at the console's own frame rate.
- **A 3D overworld**: towns, routes, caves and interiors rebuilt in 3D from
  the game's own drawing - buildings, trees, relief, furniture - with lighting,
  shadows, a day/night cycle and an adjustable camera. The classic 2D field
  is one option away.
- **3D battles** (optional): the battle in front of the voxel world.
- **A bottom screen made for touch**: region map, party and quick menu keys in
  the field, with their own touch screens for the battle, the party, the bag,
  the summary, the trainer card, the Pokédex, the PC's boxes and the fly map,
  while the top screen keeps the world. Other menus show the game's own
  picture there and use the console's buttons.
- **Free movement** (optional): walk any way the circle pad points.
- **A Pokémon that follows you** in the 3D world: the first of your party
  walks behind you, in eight directions, in Mystery Dungeon style (see below).
- **Renewed wild Pokémon**: every non-legendary Pokémon of the first three
  generations lives somewhere in Kanto or the Sevii Islands, by level and
  habitat, and the National Pokédex is open from the start.
- **Visible wild Pokémon** (optional, OPTIONS > VISIBLE WILD): instead of
  random encounters, up to 2, 4 or 6 wild Pokémon wander the grass, caves and
  water in Mystery Dungeon style; touch one to battle it.
- **Mega Evolution**: 48 Mega Evolutions of the first three generations and
  of Pokémon Legends: Z-A, with the MEGA RING and MEGA STONES found in the
  story, and renewed Gym Leaders and Elite Four that use them.
- **Physical/special split** (optional, OPTIONS > MOVE SPLIT): each move is
  physical or special by itself, as in the later games, instead of by its
  type; the move pages show its category.
- **Options**: settings, quality-of-life enhancements (game speed, exp share,
  reusable TMs, HMs without the move...) and cheats, from the bottom screen.

## Install (players)

**In your browser (any system).** Open the
[web builder](https://nachogonzalez2001.github.io/Pokemon-FireRed-3DS/build.html),
choose your ROM - Pokémon FireRed (USA, Rev 1), SHA-1
`dd5945db9b930750cb39d00c84da8571feebf417` - and it makes a ZIP with the
`3ds` folder to copy to the root of the SD card. The ROM is read on your
device and never uploaded; the first build takes a few minutes.

**On Windows**, the same builder as a program that installs straight to the
SD card:

1. Download `FireRed3DS-v<version>-Windows.zip` from the
   [Releases](../../releases) page and extract it.
2. Run `FireRed3DS-Builder.exe`, choose your ROM - Pokémon FireRed (USA,
   Rev 1), SHA-1 `dd5945db9b930750cb39d00c84da8571feebf417` - and your 3DS's SD
   card. The builder generates the game's data from your ROM on your computer
   and installs it in `/3ds/firered3ds/`. The ROM is never uploaded or copied.
3. Start the game from the Homebrew Launcher, or install
   `FireRed3DS-Forwarder.cia` once with FBI for a HOME Menu icon (it starts
   the installed game, so updates don't need a new CIA).

Needs a 3DS / 2DS family console with custom firmware (Luma3DS). For sound,
the console needs `/3ds/dspfirm.cdc`, dumped once from your own console with
the DSP1 homebrew; without it the game plays without sound.

**On the Azahar emulator**, copy the same `3ds` folder into Azahar's SD folder
(File > Open Azahar Folder, then `sdmc`) and open
`sdmc/3ds/firered3ds/FireRed3DS.3dsx`. Sound works there without
`dspfirm.cdc` (since v0.5.2).

Saves are in
`/3ds/firered3ds/firered3ds.sav`, in the GBA's format: the same 128 KB file
moves between the 3DS, GBA emulators and a cartridge dump. (v0.2.3 converts a
save from an earlier version once, keeping the original as
`firered3ds.sav.bak`.)

**Linux, macOS or a Chromebook (Linux).** The builder is plain Python: with
Python 3.11+ and Pillow, use the `payload` folder from the release ZIP and the
builder's sources from the same version:

```
git clone --branch v<version> https://github.com/NachoGonzalez2001/Pokemon-FireRed-3DS
cd Pokemon-FireRed-3DS/builder
python3 -m firered3ds_builder --payload /path/to/FireRed3DS-v<version>-Windows/payload     build --rom /path/to/firered.gba --output out
```

then copy `out/3ds` to the root of the SD card.

**The Pokémon that follows you.** Its sprites come from
[PMD SpriteCollab](https://github.com/PMDCollab/SpriteCollab), most of them Spike
Chunsoft's own from the Pokémon Mystery Dungeon games, so this repository and
its releases do not include them: the builder downloads them while it installs
(it needs an internet connection for that, once) and writes `followers.bin`
and `followers-credits.txt`, every artist credited, next to the game. Without
them the game works the same, without its follower; it can be turned off in
OPTIONS (3D FOLLOWER).

## Build (developers)

The source tree is the pinned decomp plus this project's patches and port:

```sh
python tools/bootstrap.py --dir C:/fr3ds/upstream     # pret/pokefirered + patches/ + 3ds_port/
make -C C:/fr3ds/upstream/3ds_port all                 # devkitARM, libctru, citro2d/3d
```

`make all` embeds the game data built from the decomp (a development build);
`make release` builds the executable alone. `tools/build_release.py` makes a
release: the recipe the builder rebuilds the data from (`tools/gen_recipe.py`),
the payload, the standalone builder and an audit that nothing from the game
is inside (`tools/release_audit.py`).

| Path | What |
|---|---|
| `patches/pokefirered/` | the changes to the decomp, one patch per topic |
| `3ds_port/` | the 3DS platform layer, renderer, voxel world and bottom screen |
| `3ds_port/scripts/` | generators of the 3D world from the game's art |
| `builder/` | the player's builder: ROM to data pack |
| `tools/` | bootstrap, patch export, release tools |

## Support the project

Pokémon FireRed 3DS is free and always will be. If you enjoy it and want to
support the time that goes into it, you can make a voluntary donation through
PayPal. Donations support development only: they do not buy the game, early
access or anything else, and the releases never include the game.

[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-00457C?logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=YRCM45GNZ59XW)

## Acknowledgements

Special thanks to **[ZallaxDev](https://github.com/ZallaxDev)**, creator of
[Pokémon Emerald 3Ds Dual Screen](https://github.com/ZallaxDev/pokeemerald-3Ds-dualscreen).
This project stands on that port: its 3DS platform layer, audio, bottom-screen
design, voxel renderer and tooling are where this one started, and its
approach to bringing a GBA Pokémon game to both screens of the 3DS made this
port possible.

Thanks as well to the [pret](https://github.com/pret) team for the
pokefirered decompilation.

See [NOTICE.md](NOTICE.md) for credits and licences. Pokémon FireRed 3DS is an
unofficial fan project, not affiliated with or endorsed by Nintendo, Game
Freak, Creatures or The Pokémon Company.
