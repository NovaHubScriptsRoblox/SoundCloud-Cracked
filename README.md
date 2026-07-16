# SoundCloud Desktop v2.0

A lightweight desktop client for SoundCloud with ad-blocking, Discord Rich Presence, and a sleep timer — built with Python and Qt.

> Unofficial third-party client. Not affiliated with or endorsed by SoundCloud.

## Features

- 🎧 **Native desktop player** — SoundCloud running in its own window, no browser tabs required
- 🚫 **Ad blocking** — network-level filtering of ad and tracker domains
- 🎮 **Discord Rich Presence** — shows what you're listening to on your Discord profile, with a "Listen on SoundCloud" button
- 😴 **Sleep timer** — automatically pause playback after a set time (15 min to several hours, or a custom duration)
- 🌍 **Multi-language** — English and French, with automatic detection based on your system language
- 🛠️ **Built-in DevTools** — for troubleshooting, toggle-able from the menu

## Installation

### Option A — Download the release (recommended)

Grab the latest `.exe` from the [Releases](../../releases) page and run it. No installation of Python or dependencies required.

### Option B — Run from source

Requires Python 3.9+.

```bash
git clone <this-repo-url>
cd soundcloud-desktop
pip install -r requirements.txt
python main.py
```

## Building your own executable

If you want to build the `.exe` yourself instead of using a release build:

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --windowed --icon=soundcloud.ico --name "SoundCloud-v2.0" main.py
```

The compiled executable will be in the `dist/` folder. Make sure `soundcloud.ico` is in the project root before building.

## How it works

| Component | Technology |
|---|---|
| App window / renderer | Qt WebEngine (Chromium-based) |
| Ad blocking | Network request interception |
| Discord Rich Presence | [pypresence](https://github.com/qwertyquerty/pypresence) |
| UI / menus / dialogs | PySide6 (Qt for Python) |

## Requirements

- Python 3.9+ (only needed if running from source)
- Windows (built and tested for `.exe` distribution; the source also runs on macOS/Linux)
- A Discord desktop client running, if you want Rich Presence to show up

## Known limitations

- Discord Rich Presence requires the Discord desktop app to be open and logged in.
- Ad-blocking works by filtering known ad/tracker domains — if SoundCloud changes their ad delivery infrastructure, the pattern list may need updating.

## Credits

Developed by **Soul_Nova**.

## License

Copyright © 2026 Soul_Nova. For personal use.
