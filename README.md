# SoundCloud v2.0 (Python port)

Portage de l'app Electron d'origine vers Python, avec :

| Fonction Electron | Equivalent Python |
|---|---|
| `BrowserWindow` (Chromium) | `QWebEngineView` (PySide6, aussi base sur Chromium) |
| `webRequest.onBeforeRequest` (bloqueur de pubs) | `QWebEngineUrlRequestInterceptor` |
| `discord-rpc` (npm) | `pypresence` (lib Python maintenue pour Discord Rich Presence) |
| `dialog.showMessageBox` | `QMessageBox` / `QInputDialog` |
| `Menu.buildFromTemplate` | `QMenuBar` / `QAction` |

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

Placez `soundcloud.ico` dans le meme dossier que `main.py` si vous voulez
l'icone de fenetre/executable.

## Compiler en .exe (equivalent de electron-builder)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=soundcloud.ico --name "SoundCloud-v2.0" main.py
```

L'executable sera genere dans `dist/`.

## Notes sur le portage

- Le bouton "minuteur de sommeil" injecte dans l'interface web (mutation
  observer + bouton flottant) a ete remplace par une entree de menu native.
  Fonctionnellement identique (arret automatique de la lecture), mais plus
  robuste : il ne depend pas de la structure DOM interne de SoundCloud, qui
  change regulierement et cassait le selecteur CSS de la version Electron.
- Les DevTools s'ouvrent dans une fenetre separee via `setDevToolsPage`
  (Qt WebEngine ne propose pas d'inspecteur integre dans la meme fenetre).
- La liste de domaines publicitaires bloques a ete legerement etendue
  (criteo, media.net, adroll, pubmatic) par rapport a la version d'origine.
