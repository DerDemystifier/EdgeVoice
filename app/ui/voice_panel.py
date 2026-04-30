"""Voice selection panel."""

from __future__ import annotations

import edge_tts
import flet as ft

from ..state import AppState


class VoicePanel:
    """Card that lets the user pick language, gender, and voice."""

    def __init__(
        self,
        page: ft.Page,
        state: AppState,
        initial_settings: dict[str, object] | None = None,
    ) -> None:
        self._page = page
        self._state = state
        self._initial_settings = initial_settings or {}

        self._loading_text = ft.Text(
            "Loading voices…",
            color=ft.Colors.SECONDARY,
            italic=True,
            visible=True,
        )

        self._lang_dd = ft.Dropdown(
            label="Language / Locale",
            value="All",
            expand=True,
            options=[ft.DropdownOption(key="All", text="All")],
            disabled=True,
        )
        self._gender_dd = ft.Dropdown(
            label="Gender",
            value="All",
            width=160,
            options=[
                ft.DropdownOption(key="All", text="All"),
                ft.DropdownOption(key="Female", text="Female ♀"),
                ft.DropdownOption(key="Male", text="Male ♂"),
            ],
            disabled=True,
        )
        self._voice_dd = ft.Dropdown(
            label="Voice",
            expand=True,
            options=[ft.DropdownOption(key="", text="Loading…")],
            value="",
            disabled=True,
            hint_text="Select a voice…",
        )

        self._lang_dd.on_select = self._refresh_voice_options
        self._gender_dd.on_select = self._refresh_voice_options

        col_controls: list[ft.Control] = [
            ft.Text("Voice Selection", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            self._loading_text,
            ft.Row(controls=[self._lang_dd, self._gender_dd], spacing=10),
            self._voice_dd,
        ]
        self._card = ft.Card(
            margin=ft.Margin.symmetric(vertical=0, horizontal=24),
            content=ft.Container(
                padding=16,
                content=ft.Column(spacing=10, controls=col_controls),
            ),
        )

    # ── Public interface ──────────────────────────────────────────────

    @property
    def card(self) -> ft.Card:
        return self._card

    @property
    def selected_voice(self) -> str | None:
        v = self._voice_dd.value
        return v if v else None

    @property
    def selected_language(self) -> str:
        return self._lang_dd.value or "All"

    @property
    def selected_gender(self) -> str:
        return self._gender_dd.value or "All"

    async def load_voices(self) -> None:
        """Fetch voices from edge-tts and populate the dropdowns."""
        try:
            voices = await edge_tts.list_voices()
        except Exception as ex:
            self._loading_text.value = f"Failed to load voices: {ex}"
            self._loading_text.color = ft.Colors.ERROR
            self._page.update()
            return

        self._state.all_voices.extend(voices)
        locales = sorted({v["Locale"] for v in voices})
        self._lang_dd.options = [ft.DropdownOption(key="All", text="All")] + [
            ft.DropdownOption(key=loc, text=loc) for loc in locales
        ]
        self._lang_dd.value = self._saved_language(locales)
        self._gender_dd.value = self._saved_gender()
        self._lang_dd.disabled = False
        self._gender_dd.disabled = False
        self._voice_dd.disabled = False
        self._loading_text.visible = False
        saved_voice = self._initial_settings.get("voice")
        if isinstance(saved_voice, str):
            self._voice_dd.value = saved_voice
        self._refresh_voice_options()

    # ── Private helpers ───────────────────────────────────────────────

    def _filtered_voices(self) -> list:
        lang = self._lang_dd.value or "All"
        gender = self._gender_dd.value or "All"
        result = self._state.all_voices
        if lang != "All":
            result = [v for v in result if v["Locale"] == lang]
        if gender != "All":
            result = [v for v in result if v["Gender"] == gender]
        return result

    def _refresh_voice_options(self) -> None:
        filtered = self._filtered_voices()
        self._voice_dd.options = [
            ft.DropdownOption(
                key=v["ShortName"],
                text=f"{v['ShortName']}  —  {', '.join(v['VoiceTag']['VoicePersonalities'])}",
            )
            for v in filtered
        ]
        current_keys = {v["ShortName"] for v in filtered}
        if self._voice_dd.value not in current_keys:
            self._voice_dd.value = filtered[0]["ShortName"] if filtered else None
        self._page.update()

    def _saved_gender(self) -> str:
        value = self._initial_settings.get("gender")
        return value if value in {"All", "Female", "Male"} else "All"

    def _saved_language(self, locales: list[str]) -> str:
        value = self._initial_settings.get("language")
        if value == "All":
            return "All"
        return value if isinstance(value, str) and value in locales else "All"
