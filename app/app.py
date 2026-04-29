"""Page setup and top-level assembly."""

from __future__ import annotations

import flet as ft
import flet_audio as fta

from .constants import APP_TITLE
from .state import AppState
from .ui.bulk_tab import BulkTab
from .ui.helpers import as_controls
from .ui.prosody_panel import ProsodyPanel
from .ui.single_tab import SingleTab
from .ui.voice_panel import VoicePanel


def main(page: ft.Page) -> None:
    page.title = APP_TITLE
    page.window.width = 960
    page.window.height = 860
    page.scroll = ft.ScrollMode.AUTO
    page.padding = ft.Padding.symmetric(horizontal=24, vertical=16)
    page.theme_mode = ft.ThemeMode.LIGHT

    state = AppState()

    audio = fta.Audio(
        src="",
        autoplay=False,
        volume=1.0,
        release_mode=fta.ReleaseMode.STOP,
    )

    voice_panel = VoicePanel(page, state)
    prosody_panel = ProsodyPanel(page)
    single_tab = SingleTab(page, state, voice_panel, prosody_panel, audio)
    bulk_tab = BulkTab(page, state, voice_panel, prosody_panel)

    tab_contents: list[ft.Control] = [
        ft.Container(content=single_tab.content, padding=ft.Padding.only(top=16)),
        ft.Container(content=bulk_tab.content, padding=ft.Padding.only(top=16)),
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

    def _toggle_theme() -> None:
        page.theme_mode = (
            ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        )
        page.update()

    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=as_controls(
            ft.Text(APP_TITLE, theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Row(
                controls=as_controls(
                    ft.IconButton(
                        icon=ft.Icons.LIGHT_MODE_OUTLINED,
                        tooltip="Toggle light/dark mode",
                        on_click=_toggle_theme,
                    )
                )
            ),
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
