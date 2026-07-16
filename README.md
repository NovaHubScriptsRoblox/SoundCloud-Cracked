<div align="center">

# 🎧 SoundCloud Desktop

**An unofficial desktop client for SoundCloud — ad-free, with Discord Rich Presence and a built-in sleep timer.**

[![Platform](https://img.shields.io/badge/platform-Windows-0078D6)](../../releases)
[![Made with Python](https://img.shields.io/badge/made%20with-Python-3776AB)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Personal%20Use-lightgrey)](#license)

[Download](../../releases) · [Features](#features) · [Installation](#installation) · [Build it yourself](#building-your-own-executable)

</div>

---

## What is this?

SoundCloud Desktop wraps the SoundCloud web player in a native app, strips out ads, and adds a few things the official site doesn't have — like showing your currently playing track on Discord and a sleep timer for late-night listening.

> This is an unofficial, community-made project. It is not affiliated with, endorsed by, or connected to SoundCloud.

## Features

| | |
|---|---|
| 🎧 **Native player** | SoundCloud in its own window — no browser tabs |
| 🚫 **Ad blocking** | Ad and tracker requests are filtered at the network level |
| 🎮 **Discord Rich Presence** | Shows the track you're playing on your Discord profile, with a "Listen on SoundCloud" button |
| 😴 **Sleep timer** | Auto-pause after 15 minutes to a few hours, or a custom duration |
| 🌍 **Multi-language** | English and French, auto-detected from your system |
| 🛠️ **DevTools toggle** | For debugging playback or display issues |

## Installation

### Download (recommended)

Head to the **[Releases](../../releases)** page and download the latest `SoundCloud-v2.0.exe`. No Python or setup required — just run it.

### Run from source

Requires Python 3.9+.

```bash
git clone <this-repo-url>
cd soundcloud-desktop
pip install -r requirements.txt
python main.py
```

## Building your own executable

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --windowed --icon=soundcloud.ico --name "SoundCloud-v2.0" main.py
```

Your `.exe` will be in the `dist/` folder. Keep `soundcloud.ico` in the project root before building.

## Requirements

- **To run the `.exe`:** Windows, nothing else.
- **To run from source:** Python 3.9+
- **For Discord Rich Presence:** the Discord desktop app must be open and logged in.

## Under the hood

| Piece | Tech |
|---|---|
| App window & renderer | Qt WebEngine (Chromium-based) |
| Ad blocking | Network request interception |
| Discord Rich Presence | [pypresence](https://github.com/qwertyquerty/pypresence) |
| UI, menus, dialogs | PySide6 (Qt for Python) |

## Known limitations

- Rich Presence won't appear if Discord isn't running.
- Ad blocking relies on a domain pattern list — if SoundCloud changes its ad infrastructure, the list may need an update.

## Credits

Developed by **Soul_Nova**.

## License

Copyright © 2026 Soul_Nova. For personal use.
