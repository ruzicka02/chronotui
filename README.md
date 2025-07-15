# ChronoTUI

ChronoTUI is a modern terminal-based stopwatch and timer manager built with [Textual](https://textual.textualize.io/). It lets you track multiple timers with a beautiful, keyboard-driven interface, and automatically saves your session state.

## Features

- Multiple stopwatches, each with custom names
- Start, stop, reset, and rename timers
- Keyboard navigation and control (Vim-like bindings)
- Autosave and autoload: your timers persist between sessions
- Dark/light mode toggle
- Fast, responsive UI in your terminal

## Installation

You can install ChronoTUI using either `pip` or [`uv`](https://github.com/astral-sh/uv):

```sh
pip install chronotui
```

Alternatively, if you have `uv` installed, you can install it in a special virtual environment:

```sh
uv tool run chronotui
# identical to the shortcut alias
uvx chronotui
```

Note that when installed via `uv`, you have to run it with the `uvx` command on every start.

## Usage

After installation, launch ChronoTUI from your terminal:

```sh
chronotui
```

If this doesn't work (possibly due to incorrect symlink creation during installation), you can also run it as a module:

```sh
python -m chronotui
```

## Keyboard Shortcuts

- `q` — Save and quit
- `space` — Start/stop selected stopwatch
- `r` — Reset selected stopwatch
- `a` — Add a new stopwatch
- `d` — Delete selected stopwatch
- `n` — reName timer (alternatively `c` for "change name")
- `t` — Theme selection
- `s` — Settings
- `up`/`down`/`j`/`k` — Select stopwatch (hidden)
- `S` — Save stopwatches manually (hidden)
- `L` — Load stopwatches manually (hidden)

## State Persistence

ChronoTUI automatically saves your timers and their states to `session.json` in your user data directory when you quit, and reloads them when you start the app. If a stopwatch was running when you quit, its elapsed time will be updated when you restart.

User data directory is typically located at `~/.local/share/chronotui/` on Linux, or `%APPDATA%\Local\chronotui\` on Windows.

Similarly, the configuration file is saved to `config.json` in the user config directory, allowing you to customize settings like the theme and key bindings.

User config directory is typically located at `~/.config/chronotui/` on Linux, or `%APPDATA%\Local\chronotui\` on Windows (same as user data).
