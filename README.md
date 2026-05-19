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
2. Click into the game or app where you want **F** pressed.
3. Click **Start** to begin spamming; click **Stop** to turn it off.

Some games block simulated keyboard input. If nothing happens, the target app may be ignoring synthetic keys.
