# F Key Spammer

A small Windows GUI that repeatedly presses the **F** key at a rate you choose.

## Setup

1. Install [Python 3](https://www.python.org/downloads/) if you do not have it.
2. Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
```

(No extra packages required — uses the Python standard library.)

## Run

```bash
python main.py
```

## Usage

1. Set **keys per second** on the slider (1–6).
2. With the **game focused**, press **F5** to pick the game window (or use the Pick button).
3. Press **F6** to start and **F7** to stop.
4. Or use the on-screen buttons when the control window is focused.

Hotkeys use `RegisterHotKey` so they can work while the game is focused. If hotkeys do nothing, run Python as administrator.
