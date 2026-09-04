"""Page setup and top-level assembly."""

from __future__ import annotations

import sys
from pathlib import Path

import flet as ft

from . import settings
from .constants import APP_TITLE
from .state import AppState
from .ui.bulk_tab import BulkTab
from .ui.helpers import as_controls, snack
from .ui.prosody_panel import ProsodyPanel
from .ui.single_tab import SingleTab
from .ui.voice_panel import VoicePanel


def _icon_path() -> str:
    frozen_root = getattr(sys, "_MEIPASS", None)
    root = Path(frozen_root) if frozen_root else Path(__file__).resolve().parents[1]
    return str(root / "icon.ico")


def main(page: ft.Page) -> None:
    loaded_settings = settings.load()

    def _read_float_setting(name: str) -> float:
        value = loaded_settings.get(name, 0)
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    page.title = APP_TITLE
    icon_path = _icon_path()
    try:
        if Path(icon_path).exists():
            page.window.icon = icon_path
    except Exception:
        # Best-effort only; avoid crashing if Path resolution fails
        pass
    page.window.width = 960
    page.window.height = 860
    page.scroll = ft.ScrollMode.AUTO
    page.padding = ft.Padding.symmetric(horizontal=0, vertical=16)
    page.theme_mode = (
        ft.ThemeMode.DARK if loaded_settings.get("theme") == "dark" else ft.ThemeMode.LIGHT
    )

    state = AppState()

    prosody_panel = ProsodyPanel(page)
    prosody_panel.apply(
        _read_float_setting("rate"),
        _read_float_setting("vol"),
        _read_float_setting("pitch"),
    )
    voice_panel = VoicePanel(
        page,
        state,
        initial_settings=loaded_settings,
    )
    single_tab = SingleTab(page, state, voice_panel, prosody_panel)
    bulk_tab = BulkTab(page, state, voice_panel, prosody_panel)

    tab_contents: list[ft.Control] = [
        ft.Container(
            content=single_tab.content, padding=ft.Padding.symmetric(vertical=8, horizontal=24)
        ),
        ft.Container(
            content=bulk_tab.content, padding=ft.Padding.symmetric(vertical=8, horizontal=24)
        ),
    ]
    tabs = ft.Tabs(
        selected_index=0,
        length=2,
        animation_duration=200,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Single", icon=ft.Icons.RECORD_VOICE_OVER_OUTLINED),
                        ft.Tab(label="Bulk", icon=ft.Icons.QUEUE_MUSIC_OUTLINED),
                    ],
                ),
                ft.Container(
                    height=620,
                    content=ft.TabBarView(controls=tab_contents),
                ),
            ],
        ),
    )

    def _collect_settings() -> dict[str, str | float | None]:
        return {
            "theme": "dark" if page.theme_mode == ft.ThemeMode.DARK else "light",
            "language": voice_panel.selected_language,
            "gender": voice_panel.selected_gender,
            "voice": voice_panel.selected_voice,
            "rate": prosody_panel.raw_rate,
            "vol": prosody_panel.raw_vol,
            "pitch": prosody_panel.raw_pitch,
        }

    def _persist_settings(show_error: bool = False) -> None:
        try:
            settings.save(_collect_settings())
        except OSError as ex:
            if show_error:
                snack(page, f"Failed to save settings: {ex}")

    # Declare theme_button early so static analysis (Pylance) knows the name exists
    theme_button: ft.IconButton | None = None

    def _sync_theme_button() -> None:
        if theme_button is None:
            return
        theme_button.icon = (
            ft.Icons.DARK_MODE_OUTLINED
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.LIGHT_MODE_OUTLINED
        )

    def _toggle_theme() -> None:
        page.theme_mode = (
            ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        )
        _sync_theme_button()
        _persist_settings(show_error=True)
        page.update()

    def _on_close() -> None:
        _persist_settings()

    theme_button = ft.IconButton(
        tooltip="Toggle light/dark mode",
        on_click=_toggle_theme,
    )
    _sync_theme_button()
    page.on_close = _on_close

    # Header with icon next to title
    header = ft.Row(
        margin=ft.Margin.symmetric(vertical=8, horizontal=24),
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=as_controls(
            ft.Row(
                controls=as_controls(
                    # use same icon file as window where possible
                    ft.Image(
                        src=icon_path if "icon_path" in locals() else "icon.ico",
                        width=28,
                        height=28,
                    ),
                    ft.Text(APP_TITLE, theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ),
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Row(controls=as_controls(theme_button)),
        ),
    )

    page.add(
        ft.Column(
            spacing=12,
            controls=[
                header,
                voice_panel.card,
                prosody_panel.card,
                tabs,
            ],
        )
    )

    page.run_task(voice_panel.load_voices)
