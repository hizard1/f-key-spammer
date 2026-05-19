# F Key Spammer

A small Windows GUI that repeatedly presses the **F** key at a rate you choose.

## Setup

1. Install [Python 3](https://www.python.org/downloads/) if you do not have it.
2. Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Usage

1. Open the app and use the slider to set **keys per second** (1–100).
2. Click **Start** — the window minimizes and a **3 second countdown** runs.
3. Alt-tab into your fullscreen game before the countdown ends.
4. Click **Stop** to turn it off (the window comes back).

Uses DirectInput-style key events so fullscreen games usually receive **F**. If a game still ignores input, try running the terminal or Python as administrator.
