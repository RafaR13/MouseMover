"""Mouse Mover — mexe o rato de X em X segundos, com janela e bandeja."""

from __future__ import annotations

import ctypes
import time
import sys
import threading
from ctypes import wintypes

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageDraw
import pystray

MOUSEEVENTF_MOVE = 0x0001
INPUT_MOUSE = 0


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    )


class INPUT(ctypes.Structure):
    _fields_ = (
        ("type", wintypes.DWORD),
        ("mi", MOUSEINPUT),
    )


def _enable_dpi_awareness() -> None:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def jiggle_mouse(pixels: int = 100) -> None:
    """Move o rato 1 pixel e volta — gera um evento real de rato."""
    extra = ctypes.c_void_p(0)
    send = ctypes.windll.user32.SendInput
    send.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
    send.restype = wintypes.UINT

    def move(dx: int, dy: int) -> None:
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, extra)
        send(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    move(pixels, 0)
    time.sleep(2)
    move(-pixels, 0)


def make_tray_icon() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((6, 4, 58, 60), fill=(37, 99, 235), outline=(30, 64, 175), width=3)
    draw.line((32, 10, 32, 34), fill=(255, 255, 255), width=3)
    draw.ellipse((26, 36, 38, 48), fill=(255, 255, 255))
    return img


class MouseMoverApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Mouse Mover")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        self.root.bind("<Unmap>", self._on_unmap)

        self.running = False
        self._after_id: str | None = None
        self.tray: pystray.Icon | None = None

        self.interval_var = tk.IntVar(value=30)
        self.status_var = tk.StringVar(value="Parado")

        self._build_ui()
        self._center_window()
        self._start_tray()

    def _build_ui(self) -> None:
        pad = {"padx": 16, "pady": 8}
        frame = ttk.Frame(self.root, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Mexe o rato automaticamente", font=("Segoe UI", 11, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", **pad
        )

        ttk.Label(frame, text="Intervalo (segundos):").grid(row=1, column=0, sticky="w", padx=16, pady=4)
        interval = ttk.Spinbox(
            frame,
            from_=5,
            to=3600,
            textvariable=self.interval_var,
            width=8,
            command=self._on_interval_changed,
        )
        interval.grid(row=1, column=1, sticky="e", padx=16, pady=4)
        interval.bind("<FocusOut>", lambda _e: self._on_interval_changed())
        interval.bind("<Return>", lambda _e: self._on_interval_changed())

        btns = ttk.Frame(frame)
        btns.grid(row=2, column=0, columnspan=2, pady=12)
        self.start_btn = ttk.Button(btns, text="Iniciar", command=self.start, width=12)
        self.start_btn.grid(row=0, column=0, padx=6)
        self.stop_btn = ttk.Button(btns, text="Parar", command=self.stop, width=12, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=6)

        ttk.Label(frame, textvariable=self.status_var).grid(row=3, column=0, columnspan=2, **pad)
        ttk.Label(
            frame,
            text="Fechar a janela esconde a app junto ao relógio.\nClique direito no ícone → Sair para fechar de vez.",
            justify="left",
            foreground="#444",
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 12))

    def _center_window(self) -> None:
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 3
        self.root.geometry(f"+{x}+{y}")

    def _on_unmap(self, event: tk.Event) -> None:
        if event.widget is self.root and self.root.state() == "iconic":
            self.hide_to_tray()

    def _on_interval_changed(self) -> None:
        try:
            value = int(self.interval_var.get())
        except (tk.TclError, ValueError):
            self.interval_var.set(30)
            return
        if value < 5:
            self.interval_var.set(5)
        elif value > 3600:
            self.interval_var.set(3600)
        if self.running:
            self._schedule(jiggle_now=False)
            self._refresh_status()

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self._refresh_status()
        self._schedule(jiggle_now=True)
        self._update_tray_menu()

    def stop(self) -> None:
        if not self.running:
            return
        self.running = False
        self._cancel_timer()
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.status_var.set("Parado")
        self._update_tray_menu()

    def _refresh_status(self) -> None:
        secs = int(self.interval_var.get())
        self.status_var.set(f"A correr — a cada {secs} s")

    def _schedule(self, jiggle_now: bool) -> None:
        self._cancel_timer()
        if jiggle_now:
            jiggle_mouse()
        ms = max(5, int(self.interval_var.get())) * 1000
        self._after_id = self.root.after(ms, self._tick)

    def _tick(self) -> None:
        self._after_id = None
        if not self.running:
            return
        jiggle_mouse()
        self._schedule(jiggle_now=False)

    def _cancel_timer(self) -> None:
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def hide_to_tray(self) -> None:
        self.root.withdraw()

    def show_window(self, *_args) -> None:
        self.root.after(0, self._show_window_main)

    def _show_window_main(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self, *_args) -> None:
        self.root.after(0, self._quit_main)

    def _quit_main(self) -> None:
        self.running = False
        self._cancel_timer()
        if self.tray is not None:
            self.tray.stop()
        self.root.destroy()

    def _ui(self, fn) -> None:
        self.root.after(0, fn)

    def _start_tray(self) -> None:
        menu = pystray.Menu(
            pystray.MenuItem("Mostrar", self.show_window, default=True),
            pystray.MenuItem("Iniciar", lambda: self._ui(self.start)),
            pystray.MenuItem("Parar", lambda: self._ui(self.stop)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Sair", self.quit_app),
        )
        self.tray = pystray.Icon("MouseMover", make_tray_icon(), "Mouse Mover", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def _update_tray_menu(self) -> None:
        if self.tray is not None:
            self.tray.update_menu()

    def run(self) -> None:
        self.start()
        self.root.mainloop()


def main() -> int:
    if sys.platform != "win32":
        print("Esta app é para Windows.")
        return 1
    _enable_dpi_awareness()
    MouseMoverApp().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
