"""Prosody (rate / volume / pitch) sliders panel."""

from __future__ import annotations

import flet as ft

from .. import tts
from .helpers import as_controls


class ProsodyPanel:
    """Card with Rate, Volume, and Pitch sliders."""

    def __init__(self, page: ft.Page) -> None:
        self._page = page

        self._rate_label = ft.Text("+0%", width=60, text_align=ft.TextAlign.RIGHT)
        self._vol_label = ft.Text("+0%", width=60, text_align=ft.TextAlign.RIGHT)
        self._pitch_label = ft.Text("+0Hz", width=60, text_align=ft.TextAlign.RIGHT)

        self._rate_slider = ft.Slider(
            value=0,
            min=-100,
            max=100,
            divisions=200,
            on_change=self._on_rate_change,
            expand=True,
        )
        self._vol_slider = ft.Slider(
            value=0,
            min=-100,
            max=100,
            divisions=200,
            on_change=self._on_vol_change,
            expand=True,
        )
        self._pitch_slider = ft.Slider(
            value=0,
            min=-200,
            max=200,
            divisions=400,
            on_change=self._on_pitch_change,
            expand=True,
        )

        rows: list[ft.Control] = [
            ft.Text("Prosody", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Row(
                as_controls(ft.Text("Rate", width=52), self._rate_slider, self._rate_label),
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Row(
                as_controls(ft.Text("Volume", width=52), self._vol_slider, self._vol_label),
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Row(
                as_controls(ft.Text("Pitch", width=52), self._pitch_slider, self._pitch_label),
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ]
        self._card = ft.Card(
            content=ft.Container(
                padding=16,
                content=ft.Column(spacing=6, controls=rows),
            ),
        )

    # ── Public interface ──────────────────────────────────────────────

    @property
    def card(self) -> ft.Card:
        return self._card

    @property
    def rate(self) -> str:
        return tts.fmt_rate(float(self._rate_slider.value or 0))

    @property
    def vol(self) -> str:
        return tts.fmt_vol(float(self._vol_slider.value or 0))

    @property
    def pitch(self) -> str:
        return tts.fmt_pitch(float(self._pitch_slider.value or 0))

    # ── Slider callbacks ──────────────────────────────────────────────

    def _on_rate_change(self) -> None:
        self._rate_label.value = tts.fmt_rate(float(self._rate_slider.value or 0))
        self._page.update()

    def _on_vol_change(self) -> None:
        self._vol_label.value = tts.fmt_vol(float(self._vol_slider.value or 0))
        self._page.update()

    def _on_pitch_change(self) -> None:
        self._pitch_label.value = tts.fmt_pitch(float(self._pitch_slider.value or 0))
        self._page.update()
