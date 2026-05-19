"""Simple F-key spammer with adjustable rate (game-friendly input)."""

import threading
import time
import tkinter as tk
from tkinter import ttk

import pydirectinput

# DirectInput-style keys work in fullscreen games; default pause is too slow.
pydirectinput.PAUSE = 0.0

running = False
spam_thread: threading.Thread | None = None
FOCUS_COUNTDOWN_SECS = 3


def _set_status(text: str) -> None:
    root.after(0, lambda: status_var.set(text))


def spam_loop(keys_per_second: float) -> None:
    global running
    for remaining in range(FOCUS_COUNTDOWN_SECS, 0, -1):
        if not running:
            return
        _set_status(f"Starting in {remaining}s — click into your game")
        time.sleep(1)

    if not running:
        return

    _set_status(f"ON — pressing F at {keys_per_second:.0f}/s")
    interval = 1.0 / keys_per_second if keys_per_second > 0 else 0.01
    while running:
        pydirectinput.press("f")
        time.sleep(interval)


def start_spam() -> None:
    global running, spam_thread
    if running:
        return
    rate = rate_var.get()
    running = True
    start_btn.config(state=tk.DISABLED)
    stop_btn.config(state=tk.NORMAL)
    root.iconify()
    status_var.set(f"Starting in {FOCUS_COUNTDOWN_SECS}s — click into your game")
    spam_thread = threading.Thread(target=spam_loop, args=(rate,), daemon=True)
    spam_thread.start()


def stop_spam() -> None:
    global running
    running = False
    start_btn.config(state=tk.NORMAL)
    stop_btn.config(state=tk.DISABLED)
    root.deiconify()
    root.lift()
    status_var.set("OFF")


def on_rate_change(_value: str) -> None:
    rate_label.config(text=f"{rate_var.get():.0f} keys per second")
    if running:
        status_var.set(f"ON — pressing F at {rate_var.get():.0f}/s")


def on_close() -> None:
    stop_spam()
    root.destroy()


root = tk.Tk()
root.title("F Key Spammer")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_close)

main = ttk.Frame(root, padding=16)
main.grid(row=0, column=0, sticky="nsew")

ttk.Label(main, text="F Key Spammer", font=("Segoe UI", 14, "bold")).grid(
    row=0, column=0, columnspan=2, pady=(0, 12)
)

ttk.Label(main, text="Press rate:").grid(row=1, column=0, sticky="w")

rate_var = tk.DoubleVar(value=20.0)
rate_slider = ttk.Scale(
    main,
    from_=1,
    to=100,
    orient=tk.HORIZONTAL,
    length=220,
    variable=rate_var,
    command=on_rate_change,
)
rate_slider.grid(row=1, column=1, padx=(8, 0), sticky="ew")

rate_label = ttk.Label(main, text="20 keys per second")
rate_label.grid(row=2, column=0, columnspan=2, pady=(4, 16))

btn_row = ttk.Frame(main)
btn_row.grid(row=3, column=0, columnspan=2, pady=(0, 12))

start_btn = ttk.Button(btn_row, text="Start", width=12, command=start_spam)
start_btn.grid(row=0, column=0, padx=(0, 8))

stop_btn = ttk.Button(btn_row, text="Stop", width=12, command=stop_spam, state=tk.DISABLED)
stop_btn.grid(row=0, column=1)

status_var = tk.StringVar(value="OFF")
ttk.Label(main, textvariable=status_var, foreground="#555").grid(
    row=4, column=0, columnspan=2
)

ttk.Label(
    main,
    text="Start minimizes this window; you get 3s to focus the game.",
    font=("Segoe UI", 8),
    foreground="#888",
).grid(row=5, column=0, columnspan=2, pady=(12, 0))

root.mainloop()
