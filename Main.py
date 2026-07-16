"""
SoundCloud v2.0
Developer Soul_Nova
Copyright (c) 2026 Soul_Nova
"""

import re
import sys
import time
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl, Qt, QLocale
from PySide6.QtGui import QIcon, QAction, QActionGroup
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QInputDialog
)
from PySide6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide6.QtWebEngineWidgets import QWebEngineView

try:
    from pypresence import Presence
    from pypresence.exceptions import PyPresenceException
except ImportError:
    Presence = None
    PyPresenceException = Exception

APP_DIR = Path(__file__).resolve().parent
ICON_PATH = APP_DIR / "soundcloud.ico"

DISCORD_CLIENT_ID = "1090770350251458592"
RPC_UPDATE_INTERVAL_MS = 10_000
RPC_RECONNECT_DELAY_MS = 20_000
MAX_RECONNECT_ATTEMPTS = 5

# ---------------------------------------------------------------------------
# Textes multilingues (identiques a la version Electron d'origine)
# ---------------------------------------------------------------------------
LOCALES = {
    "fr": {
        "app_title": "SoundCloud - by Soul_Nova v2.0",
        "menu": {
            "home": "Accueil",
            "sleep_timer": "Minuteur de sommeil",
            "official_site": "Site officiel",
            "github": "Github",
            "about": "A propos",
            "refresh": "Rafraichir",
            "quit": "Quitter",
            "devtools": "Activer/Desactiver DevTools",
            "language": "Langue",
            "language_fr": "Francais",
            "language_en": "Anglais",
            "language_auto": "Automatique",
        },
        "about_dialog": {
            "title": "A propos de SoundCloud v2.0",
            "message": "SoundCloud v2.0 - Client optimise",
            "detail": (
                "Developpe par Soul_Nova\n"
                "Portage Python (PySide6 + pypresence)\n"
                "Copyright (c) 2026 Soul_Nova\n\n"
                "Application permettant d'ecouter de la musique depuis "
                "SoundCloud avec des fonctionnalites avancees."
            ),
        },
        "sleep_timer": {
            "title": "Minuteur de sommeil",
            "message": "Arreter la lecture apres :",
            "custom_title": "Duree personnalisee",
            "custom_message": "Entrez la duree en minutes :",
            "activated_title": "Minuteur active",
            "activated_message": "La lecture s'arretera dans {minutes} minutes",
            "stopped_title": "Minuteur de sommeil",
            "stopped_message": "La lecture a ete mise en pause par le minuteur",
        },
        "options": {
            "min15": "15 minutes",
            "min30": "30 minutes",
            "min45": "45 minutes",
            "hour1": "1 heure",
            "hour1_30": "1h30",
            "hour2": "2 heures",
            "custom": "Personnalise...",
            "disable": "Desactiver",
            "cancel": "Annuler",
        },
    },
    "en": {
        "app_title": "SoundCloud - Player v2.0",
        "menu": {
            "home": "Home",
            "sleep_timer": "Sleep Timer",
            "official_site": "Official Website",
            "github": "Github",
            "about": "About",
            "refresh": "Refresh",
            "quit": "Quit",
            "devtools": "Toggle DevTools",
            "language": "Language",
            "language_fr": "French",
            "language_en": "English",
            "language_auto": "Automatic",
        },
        "about_dialog": {
            "title": "About SoundCloud v2.0",
            "message": "SoundCloud v2.0 - Optimized Client",
            "detail": (
                "Developed by Soul_Nova\n"
                "Python port (PySide6 + pypresence)\n"
                "Copyright (c) 2026 Soul_Nova\n\n"
                "Application allowing you to listen to music from "
                "SoundCloud with advanced features."
            ),
        },
        "sleep_timer": {
            "title": "Sleep Timer",
            "message": "Stop playback after:",
            "custom_title": "Custom Duration",
            "custom_message": "Enter duration in minutes:",
            "activated_title": "Timer Activated",
            "activated_message": "Playback will stop in {minutes} minutes",
            "stopped_title": "Sleep Timer",
            "stopped_message": "Playback has been paused by the timer",
        },
        "options": {
            "min15": "15 minutes",
            "min30": "30 minutes",
            "min45": "45 minutes",
            "hour1": "1 hour",
            "hour1_30": "1h30",
            "hour2": "2 hours",
            "custom": "Custom...",
            "disable": "Disable",
            "cancel": "Cancel",
        },
    },
}

# Domaines / motifs publicitaires bloques (liste mise a jour)
AD_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r".*ads.*",
        r".*advert.*",
        r".*doubleclick\.net.*",
        r".*googlesyndication\.com.*",
        r".*adservice\.google.*",
        r".*pagead.*",
        r".*ad-delivery.*",
        r".*exponential\.com.*",
        r".*amazon-adsystem\.com.*",
        r".*adnxs\.com.*",
        r".*taboola\.com.*",
        r".*outbrain\.com.*",
        r".*sponsor.*",
        r".*adserver.*",
        r".*banners?.*",
        r".*promotions.*",
        r".*criteo\.(com|net).*",
        r".*media\.net.*",
        r".*adroll\.com.*",
        r".*pubmatic\.com.*",
    ]
]


def detect_system_language() -> str:
    """Detecte la langue du systeme (equivalent app.getLocale() Electron)."""
    locale_name = QLocale.system().name()  # ex: "fr_FR", "en_US"
    return "fr" if locale_name.lower().startswith("fr") else "en"


class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    """Bloque les requetes reseau correspondant aux motifs publicitaires,
    equivalent de session.webRequest.onBeforeRequest cote Electron."""

    def interceptRequest(self, info):
        url = info.requestUrl().toString().lower()
        if any(pattern.search(url) for pattern in AD_PATTERNS):
            info.block(True)


class DiscordRPCManager:
    """Gere la connexion / reconnexion / mise a jour de la Discord Rich
    Presence, equivalent du module discord-rpc cote Electron."""

    def __init__(self, client_id: str):
        self.client_id = client_id
        self.rpc = None
        self.connected = False
        self.reconnect_attempts = 0
        self.last_update = 0.0
        self.cached_state = None

    def connect(self):
        if Presence is None:
            print("pypresence n'est pas installe - Discord RPC desactive.")
            return
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.connected = True
            self.reconnect_attempts = 0
            print("Discord RPC connecte avec succes")
        except Exception as exc:
            print(f"Echec de la connexion a Discord RPC : {exc}")
            self.connected = False
            self._schedule_reconnect()

    def _schedule_reconnect(self):
        if self.reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
            self.reconnect_attempts += 1
            print(
                f"Tentative de reconnexion "
                f"({self.reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS})..."
            )
            QTimer.singleShot(RPC_RECONNECT_DELAY_MS, self.connect)

    def set_default_activity(self, lang: str):
        if not self.connected or not self.rpc:
            return
        is_en = lang == "en"
        try:
            self.rpc.update(
                details="listening on Soundcloud" if is_en else "ecoute sur Soundcloud",
                state="Waiting..." if is_en else "En attente...",
                large_image="soundcloud-logo",
                large_text="by Soul_Nova",
                buttons=[
                    {
                        "label": "Listen on SoundCloud" if is_en else "Ecouter sur SoundCloud",
                        "url": "https://soundcloud.com/",
                    }
                ],
            )
        except Exception as exc:
            print(f"Echec de la definition de l'activite par defaut : {exc}")

    def update(self, is_playing: bool, track: dict | None, lang: str):
        if not self.connected or not self.rpc:
            return

        now = time.time() * 1000
        if now - self.last_update < RPC_UPDATE_INTERVAL_MS:
            return

        state_key = (
            track.get("title") if track else None,
            track.get("artist") if track else None,
            is_playing,
        )
        if state_key == self.cached_state:
            return
        self.cached_state = state_key
        self.last_update = now

        is_en = lang == "en"
        try:
            if is_playing and track:
                title = (track.get("title") or "")[:80]
                artist = (track.get("artist") or "")[:30]
                self.rpc.update(
                    details=title or ("Unknown track" if is_en else "Piste inconnue"),
                    state=(f"By {artist}" if is_en else f"Par {artist}"),
                    large_image="soundcloud-logo",
                    large_text="By Soul_Nova",
                    buttons=[
                        {
                            "label": "Listen on SoundCloud" if is_en else "Ecouter sur SoundCloud",
                            "url": track.get("url") or "https://soundcloud.com/",
                        }
                    ],
                )
            else:
                self.rpc.update(
                    details="listening on Soundcloud" if is_en else "ecoute sur Soundcloud",
                    state="Paused" if is_en else "En pause",
                    large_image="idling",
                    large_text="by Soul_Nova",
                )
        except Exception as exc:
            print(f"Erreur lors de la mise a jour de Discord RPC : {exc}")
            self.connected = False
            self._schedule_reconnect()

    def close(self):
        if self.rpc and self.connected:
            try:
                self.rpc.close()
            except Exception:
                pass


# JS injecte periodiquement pour lire l'etat du lecteur SoundCloud dans la page
TRACK_INFO_JS = """
(function() {
    try {
        const playButton = document.querySelector('.playControls__play');
        const isPlaying = !!(playButton && playButton.classList.contains('playing'));

        const titleEl = document.querySelector('.playbackSoundBadge__titleLink');
        const artistEl = document.querySelector('.playbackSoundBadge__lightLink');

        let trackInfo = null;
        if (titleEl && artistEl) {
            trackInfo = {
                title: titleEl.innerText || 'Unknown',
                artist: artistEl.innerText || 'Unknown',
                url: titleEl.href || 'https://soundcloud.com/'
            };
        }
        return { isPlaying: isPlaying, trackInfo: trackInfo };
    } catch (e) {
        return { isPlaying: false, trackInfo: null };
    }
})();
"""

PAUSE_PLAYBACK_JS = """
(function() {
    const playButton = document.querySelector('.playControls__play');
    if (playButton && playButton.classList.contains('playing')) {
        playButton.click();
    }
})();
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_language = detect_system_language()
        self.devtools_view = None
        self.sleep_timer_active = None  # QTimer instance or None

        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        self.resize(1280, 720)

        # --- WebView + ad block interceptor -------------------------------
        self.webview = QWebEngineView(self)
        profile = self.webview.page().profile()
        self.interceptor = AdBlockInterceptor()
        profile.setUrlRequestInterceptor(self.interceptor)

        self.webview.load(QUrl("https://soundcloud.com/"))
        self.setCentralWidget(self.webview)

        # --- Discord RPC ----------------------------------------------------
        self.rpc_manager = DiscordRPCManager(DISCORD_CLIENT_ID)
        QTimer.singleShot(3000, self._start_rpc)

        self.rpc_poll_timer = QTimer(self)
        self.rpc_poll_timer.timeout.connect(self._poll_track_info)
        self.rpc_poll_timer.start(RPC_UPDATE_INTERVAL_MS)

        self.setWindowTitle(self.texts()["app_title"])
        self.build_menu()

    # ------------------------------------------------------------------
    def texts(self):
        return LOCALES[self.current_language]

    def _start_rpc(self):
        self.rpc_manager.connect()
        QTimer.singleShot(500, lambda: self.rpc_manager.set_default_activity(self.current_language))

    def _poll_track_info(self):
        self.webview.page().runJavaScript(TRACK_INFO_JS, self._on_track_info)

    def _on_track_info(self, result):
        if not result:
            return
        self.rpc_manager.update(
            result.get("isPlaying", False),
            result.get("trackInfo"),
            self.current_language,
        )

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------
    def build_menu(self):
        texts = self.texts()
        menubar = self.menuBar()
        menubar.clear()

        main_menu = menubar.addMenu("SoundCloud v2.0")

        act_home = QAction(texts["menu"]["home"], self)
        act_home.triggered.connect(lambda: self.webview.load(QUrl("https://soundcloud.com/")))
        main_menu.addAction(act_home)

        act_sleep = QAction(texts["menu"]["sleep_timer"], self)
        act_sleep.triggered.connect(self.show_sleep_timer)
        main_menu.addAction(act_sleep)

        act_site = QAction(texts["menu"]["official_site"], self)
        act_site.triggered.connect(
            lambda: QApplication.instance().property("open_url")
            or self._open_external("https://soundcloud-desktop.web.app/")
        )
        main_menu.addAction(act_site)

        act_github = QAction(texts["menu"]["github"], self)
        act_github.triggered.connect(
            lambda: self._open_external("https://github.com/Soul-Nova/SoundCloud-desktop")
        )
        main_menu.addAction(act_github)

        act_about = QAction(texts["menu"]["about"], self)
        act_about.triggered.connect(self.show_about)
        main_menu.addAction(act_about)

        lang_menu = main_menu.addMenu(texts["menu"]["language"])
        lang_group = QActionGroup(self)
        lang_group.setExclusive(True)

        act_auto = QAction(texts["menu"]["language_auto"], self, checkable=True)
        act_auto.setChecked(self.current_language == detect_system_language())
        act_auto.triggered.connect(lambda: self.change_language("auto"))
        lang_group.addAction(act_auto)
        lang_menu.addAction(act_auto)

        act_fr = QAction(texts["menu"]["language_fr"], self, checkable=True)
        act_fr.setChecked(self.current_language == "fr")
        act_fr.triggered.connect(lambda: self.change_language("fr"))
        lang_group.addAction(act_fr)
        lang_menu.addAction(act_fr)

        act_en = QAction(texts["menu"]["language_en"], self, checkable=True)
        act_en.setChecked(self.current_language == "en")
        act_en.triggered.connect(lambda: self.change_language("en"))
        lang_group.addAction(act_en)
        lang_menu.addAction(act_en)

        act_refresh = QAction(texts["menu"]["refresh"], self)
        act_refresh.triggered.connect(self.webview.reload)
        main_menu.addAction(act_refresh)

        act_quit = QAction(texts["menu"]["quit"], self)
        act_quit.triggered.connect(QApplication.instance().quit)
        main_menu.addAction(act_quit)

        devtools_menu = menubar.addMenu(texts["menu"]["devtools"])
        act_devtools = QAction(texts["menu"]["devtools"], self)
        act_devtools.triggered.connect(self.toggle_devtools)
        devtools_menu.addAction(act_devtools)

    def _open_external(self, url: str):
        from PySide6.QtGui import QDesktopServices

        QDesktopServices.openUrl(QUrl(url))

    def change_language(self, lang: str):
        self.current_language = detect_system_language() if lang == "auto" else lang
        self.setWindowTitle(self.texts()["app_title"])
        self.build_menu()

    def show_about(self):
        texts = self.texts()["about_dialog"]
        QMessageBox.information(self, texts["title"], f"{texts['message']}\n\n{texts['detail']}")

    def toggle_devtools(self):
        if self.devtools_view is None:
            self.devtools_view = QWebEngineView()
            self.devtools_view.setWindowTitle("DevTools")
            self.webview.page().setDevToolsPage(self.devtools_view.page())
            self.devtools_view.resize(1000, 700)
            self.devtools_view.show()
        else:
            if self.devtools_view.isVisible():
                self.devtools_view.hide()
            else:
                self.devtools_view.show()

    # ------------------------------------------------------------------
    # Minuteur de sommeil
    # ------------------------------------------------------------------
    def show_sleep_timer(self):
        texts = self.texts()

        options = [
            (15, texts["options"]["min15"]),
            (30, texts["options"]["min30"]),
            (45, texts["options"]["min45"]),
            (60, texts["options"]["hour1"]),
            (90, texts["options"]["hour1_30"]),
            (120, texts["options"]["hour2"]),
            (-1, texts["options"]["custom"]),
            (0, texts["options"]["disable"]),
        ]
        labels = [label for _, label in options]

        choice, ok = QInputDialog.getItem(
            self,
            texts["sleep_timer"]["title"],
            texts["sleep_timer"]["message"],
            labels,
            0,
            False,
        )
        if not ok:
            return

        minutes = dict((label, mins) for mins, label in options)[choice]

        if minutes == -1:
            custom, ok2 = QInputDialog.getInt(
                self,
                texts["sleep_timer"]["custom_title"],
                texts["sleep_timer"]["custom_message"],
                30,
                1,
                600,
            )
            if not ok2:
                return
            minutes = custom

        if minutes == 0:
            if self.sleep_timer_active:
                self.sleep_timer_active.stop()
                self.sleep_timer_active = None
            return

        if minutes > 0:
            self._set_sleep_timer(minutes)

    def _set_sleep_timer(self, minutes: int):
        texts = self.texts()["sleep_timer"]

        if self.sleep_timer_active:
            self.sleep_timer_active.stop()

        QMessageBox.information(
            self,
            texts["activated_title"],
            texts["activated_message"].format(minutes=minutes),
        )

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_sleep_timer_fired)
        timer.start(minutes * 60 * 1000)
        self.sleep_timer_active = timer

    def _on_sleep_timer_fired(self):
        texts = self.texts()["sleep_timer"]
        self.webview.page().runJavaScript(PAUSE_PLAYBACK_JS)
        QMessageBox.information(self, texts["stopped_title"], texts["stopped_message"])
        self.sleep_timer_active = None

    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self.rpc_manager.close()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SoundCloud v2.0")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
