"""The builder's window: pick the ROM, pick the SD card, Install."""

from __future__ import annotations

import queue
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import __version__
from . import followers
from .build import Payload, build_pack, default_payload
from .errors import BuilderError
from .install import APP_DIR, find_sd_cards, install
from .rom import load_rom

TITLE = "포켓몬스터 파이어레드 3DS 한글판 빌더"


class App:
    def __init__(self, root: tk.Tk, payload: Payload):
        self.root = root
        self.payload = payload
        self.events: queue.Queue = queue.Queue()
        self.busy = False
        root.title("%s %s" % (TITLE, __version__))
        root.resizable(False, False)
        frame = ttk.Frame(root, padding=16)
        frame.grid(sticky="nsew")

        ttk.Label(frame, text="포켓몬스터 파이어레드 한글판 롬 (K260613)").grid(
            row=0, column=0, columnspan=2, sticky="w")
        self.rom = tk.StringVar()
        ttk.Entry(frame, textvariable=self.rom, width=56).grid(row=1, column=0, sticky="we")
        ttk.Button(frame, text="찾아보기...", command=self.pick_rom).grid(row=1, column=1, padx=(8, 0))
        self.rom_status = ttk.Label(frame, text="")
        self.rom_status.grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 10))

        ttk.Label(frame, text="설치할 곳 (3DS SD 카드의 최상위 폴더)").grid(
            row=3, column=0, columnspan=2, sticky="w")
        self.sd = tk.StringVar()
        self.sd_box = ttk.Combobox(frame, textvariable=self.sd, width=53)
        self.sd_box.grid(row=4, column=0, sticky="we")
        ttk.Button(frame, text="찾아보기...", command=self.pick_sd).grid(row=4, column=1, padx=(8, 0))
        self.sd_status = ttk.Label(frame, text="")
        self.sd_status.grid(row=5, column=0, columnspan=2, sticky="w", pady=(2, 10))

        self.bar = ttk.Progressbar(frame, length=420, maximum=1000)
        self.bar.grid(row=6, column=0, columnspan=2, sticky="we")
        self.step = ttk.Label(frame, text="")
        self.step.grid(row=7, column=0, columnspan=2, sticky="w", pady=(2, 10))

        self.button = ttk.Button(frame, text="설치", command=self.start)
        self.button.grid(row=8, column=0, columnspan=2)
        ttk.Label(frame, text="롬은 이 컴퓨터 밖으로 나가지 않고 복사되지도 않습니다. "
                              "롬에서 만든 데이터 팩만 SD 카드에 씁니다.", foreground="#555",
                  wraplength=460).grid(row=9, column=0, columnspan=2, pady=(12, 0))

        self.rom.trace_add("write", lambda *a: self.check_rom())
        self.sd.trace_add("write", lambda *a: self.check_sd())
        self.refresh_cards()
        root.after(100, self.poll)

    # -- inputs -------------------------------------------------------------
    def pick_rom(self):
        path = filedialog.askopenfilename(title="포켓몬스터 파이어레드 한글판 롬",
                                          filetypes=[("GBA ROM", "*.gba *.zip"), ("모든 파일", "*.*")])
        if path:
            self.rom.set(path)

    def pick_sd(self):
        path = filedialog.askdirectory(title="SD 카드 또는 출력 폴더")
        if path:
            self.sd.set(path)

    def refresh_cards(self):
        cards = [str(c) for c in find_sd_cards()]
        self.sd_box["values"] = cards
        if cards and not self.sd.get():
            self.sd.set(cards[0])

    def check_rom(self):
        path = self.rom.get().strip()
        if not path:
            self.rom_status.config(text="", foreground="")
            return
        try:
            rom = load_rom(Path(path))
        except BuilderError as exc:
            self.rom_status.config(text="X  " + exc.message, foreground="#b00020")
            return
        self.rom_status.config(text="확인  한글판 롬 (SHA-1 일치)", foreground="#1b7a1b")

    def check_sd(self):
        path = Path(self.sd.get().strip()) if self.sd.get().strip() else None
        if path is None:
            self.sd_status.config(text="")
        elif (path / "Nintendo 3DS").is_dir():
            self.sd_status.config(text="확인  3DS SD 카드를 찾았습니다", foreground="#1b7a1b")
        elif path.is_dir():
            self.sd_status.config(text="3DS SD 카드가 아닌 폴더입니다. 이 폴더에 파일을 만들어 두니 "
                                       "직접 SD 카드로 복사하세요.", foreground="#8a6d00")
        else:
            self.sd_status.config(text="X  폴더를 찾을 수 없습니다", foreground="#b00020")

    # -- work -----------------------------------------------------------------
    def start(self):
        if self.busy:
            return
        rom, sd = self.rom.get().strip(), self.sd.get().strip()
        if not rom or not sd:
            messagebox.showwarning(TITLE, "롬과 설치할 곳을 먼저 선택하세요.")
            return
        dest = Path(sd) / APP_DIR
        if not messagebox.askokcancel(TITLE, "다음 위치에 설치합니다:\n\n%s\n\n계속할까요?" % dest):
            return
        self.busy = True
        self.button.state(["disabled"])
        threading.Thread(target=self.work, args=(Path(rom), Path(sd)), daemon=True).start()

    def work(self, rom: Path, sd: Path):
        def progress(fraction, message):
            self.events.put(("progress", fraction, message))
        try:
            self.payload.check()
            with tempfile.TemporaryDirectory(prefix="firered3ds-") as tmp:
                pak_path = Path(tmp) / "firered3ds.pak"
                info = build_pack(rom, self.payload, pak_path, lambda f, m: progress(f * 0.8, m))
                files = {exe.name: exe for exe in info["payload"].executables()}
                files["firered3ds.pak"] = pak_path
                warning = ""
                try:
                    followers.build(Path(tmp), progress=lambda f: progress(
                        0.8 + 0.1 * f, "동행 포켓몬 이미지 내려받는 중"))
                    for name in followers.OUTPUTS:
                        files[name] = Path(tmp) / name
                except followers.FollowerError as exc:
                    warning = ("\n\n동행 포켓몬 이미지를 내려받지 못했습니다(%s). "
                               "게임은 그대로 할 수 있고, 인터넷에 연결한 뒤 다시 설치하면 "
                               "추가됩니다." % exc)
                dest = install(sd, files, lambda f: progress(0.9 + 0.1 * f, "SD 카드에 복사하는 중"))
            self.events.put(("done", str(dest) + warning))
        except BuilderError as exc:
            self.events.put(("error", str(exc)))
        except Exception as exc:  # the player gets a message, never a traceback
            self.events.put(("error", "예상하지 못한 오류: %s" % exc))

    def poll(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "progress":
                    self.bar["value"] = int(event[1] * 1000)
                    self.step.config(text=event[2])
                elif event[0] == "done":
                    self.finish()
                    messagebox.showinfo(TITLE, "설치를 마쳤습니다:\n%s\n\n"
                                               "홈브류 런처(또는 CIA 포워더)로 실행하세요." % event[1])
                elif event[0] == "error":
                    self.finish()
                    messagebox.showerror(TITLE, event[1])
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def finish(self):
        self.busy = False
        self.button.state(["!disabled"])
        self.step.config(text="")
        self.bar["value"] = 0


def main(payload: Path | None = None) -> int:
    root = tk.Tk()
    App(root, Payload(payload or default_payload()))
    root.mainloop()
    return 0
