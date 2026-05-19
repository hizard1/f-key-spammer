"""F-key spammer — global hotkeys while the game stays focused."""

from __future__ import annotations

import ctypes
import threading
import time
import tkinter as tk
from ctypes import wintypes
from tkinter import ttk

user32 = ctypes.windll.user32

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_HOTKEY = 0x0312
VK_F = 0x46
VK_F5 = 0x74

MOD_NOREPEAT = 0x4000
PM_REMOVE = 0x0001
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080

MAX_RATE = 6
HOTKEY_PICK = 1


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]


running = False
spam_thread: threading.Thread | None = None
game_hwnd: int | None = None


def _root_hwnd() -> int:
    return user32.GetParent(root.winfo_id())


def _foreground_hwnd() -> int:
    return user32.GetForegroundWindow()


def _apply_overlay_style() -> None:
    hwnd = _root_hwnd()
    style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    user32.SetWindowLongW(
        hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
    )


def _is_our_window(hwnd: int) -> bool:
    if not hwnd:
        return True
    ours = _root_hwnd()
    while hwnd:
        if hwnd == ours:
            return True
        hwnd = user32.GetParent(hwnd)
    return False


def _window_title(hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(hwnd) + 1
    buf = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, buf, length)
    title = buf.value.strip() or "(untitled)"
    if len(title) > 36:
        title = title[:33] + "..."
    return title


def _clamp_rate(rate: float) -> float:
    return max(1.0, min(float(MAX_RATE), rate))


def _f_scan_code() -> int:
    return user32.MapVirtualKeyW(VK_F, 0)


def _postmessage_f(hwnd: int) -> None:
    scan = _f_scan_code()
    lp_down = 1 | (scan << 16)
    lp_up = lp_down | (1 << 30) | (1 << 31)
    user32.PostMessageW(hwnd, WM_KEYDOWN, VK_F, lp_down)
    user32.PostMessageW(hwnd, WM_KEYUP, VK_F, lp_up)


def press_f(hwnd: int) -> None:
    if hwnd and not _is_our_window(hwnd):
        _postmessage_f(hwnd)


def _set_status(text: str) -> None:
    root.after(0, lambda: status_var.set(text))


def _update_buttons() -> None:
    if running:
        start_btn.config(state=tk.DISABLED)
        stop_btn.config(state=tk.NORMAL)
    else:
        start_btn.config(state=tk.NORMAL)
        stop_btn.config(state=tk.DISABLED)


def capture_game_window() -> None:
    global game_hwnd
    hwnd = _foreground_hwnd()
    if _is_our_window(hwnd):
        status_var.set("Click the game first, then press Pick game")
        return
    game_hwnd = hwnd
    status_var.set(f"Game: {_window_title(hwnd)}")


def spam_loop(keys_per_second: float) -> None:
    global running, game_hwnd
    target = game_hwnd
    if not target or _is_our_window(target):
        _set_status("Pick the game first (F5 or Pick game window)")
        running = False
        root.after(0, _update_buttons)
        return

    _set_status(f"ON — F at {keys_per_second:.0f}/s")
    interval = 1.0 / keys_per_second
    while running:
        hwnd = game_hwnd or target
        if hwnd and not _is_our_window(hwnd):
            press_f(hwnd)
        time.sleep(interval)

    if game_hwnd:
        _set_status(f"OFF — game: {_window_title(game_hwnd)}")
    else:
        _set_status("OFF")


def start_spam() -> None:
    global running, spam_thread, game_hwnd
    if running:
        return

    if not game_hwnd or _is_our_window(game_hwnd):
        hwnd = _foreground_hwnd()
        if not _is_our_window(hwnd):
            game_hwnd = hwnd
        else:
            _set_status("Pick the game first (F5 or Pick game window)")
            return

    rate = _clamp_rate(rate_var.get())
    running = True
    root.after(0, _update_buttons)
    spam_thread = threading.Thread(target=spam_loop, args=(rate,), daemon=True)
    spam_thread.start()


def stop_spam() -> None:
    global running
    running = False
    root.after(0, _update_buttons)


def on_rate_change(_value: str) -> None:
    rate = _clamp_rate(rate_var.get())
    if rate != rate_var.get():
        rate_var.set(rate)
    rate_label.config(text=f"{rate:.0f} keys per second (max {MAX_RATE})")
    if running:
        _set_status(f"ON — F at {rate:.0f}/s (game stays focused)")


def _register_hotkeys() -> None:
    hwnd = _root_hwnd()
    user32.RegisterHotKey(hwnd, HOTKEY_PICK, MOD_NOREPEAT, VK_F5)


def _unregister_hotkeys() -> None:
    user32.UnregisterHotKey(_root_hwnd(), HOTKEY_PICK)


def _poll_hotkeys() -> None:
    hwnd = _root_hwnd()
    msg = MSG()
    while user32.PeekMessageW(ctypes.byref(msg), hwnd, WM_HOTKEY, WM_HOTKEY, PM_REMOVE):
        if msg.wParam == HOTKEY_PICK:
            capture_game_window()
    root.after(80, _poll_hotkeys)


def on_close() -> None:
    stop_spam()
    _unregister_hotkeys()
    root.destroy()


root = tk.Tk()
root.title("F Spammer")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_close)
root.attributes("-topmost", True)

main = ttk.Frame(root, padding=12)
main.grid(row=0, column=0, sticky="nsew")

ttk.Label(main, text="F Key Spammer", font=("Segoe UI", 12, "bold")).grid(
    row=0, column=0, columnspan=2, pady=(0, 8)
)

ttk.Label(main, text="Press rate:").grid(row=1, column=0, sticky="w")

rate_var = tk.DoubleVar(value=3.0)
rate_slider = ttk.Scale(
    main,
    from_=1,
    to=MAX_RATE,
    orient=tk.HORIZONTAL,
    length=200,
    variable=rate_var,
    command=on_rate_change,
)
rate_slider.grid(row=1, column=1, padx=(8, 0), sticky="ew")

rate_label = ttk.Label(main, text=f"3 keys per second (max {MAX_RATE})")
rate_label.grid(row=2, column=0, columnspan=2, pady=(4, 10))

pick_btn = ttk.Button(main, text="Pick game window", command=capture_game_window)
pick_btn.grid(row=3, column=0, columnspan=2, pady=(0, 8), sticky="ew")

btn_row = ttk.Frame(main)
btn_row.grid(row=4, column=0, columnspan=2, pady=(0, 8))

start_btn = ttk.Button(btn_row, text="Start", width=11, command=start_spam)
start_btn.grid(row=0, column=0, padx=(0, 6))

stop_btn = ttk.Button(btn_row, text="Stop", width=11, command=stop_spam, state=tk.DISABLED)
stop_btn.grid(row=0, column=1)

status_var = tk.StringVar(value="F5 = pick game")
ttk.Label(main, textvariable=status_var, foreground="#555", wraplength=260).grid(
    row=5, column=0, columnspan=2
)

ttk.Label(
    main,
    text="Pick shows the game title when set. Start sends F to that window only.",
    font=("Segoe UI", 8),
    foreground="#888",
    justify=tk.LEFT,
).grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="w")

root.update_idletasks()
_apply_overlay_style()
_register_hotkeys()
_poll_hotkeys()

root.mainloop()
