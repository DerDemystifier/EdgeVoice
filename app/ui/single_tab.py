"""Single-item TTS tab — generate & play or save one audio file."""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

import flet as ft
import flet_audio as fta
from flet_audio.types import AudioStateChangeEvent

from .. import tts
from ..state import AppState
from .helpers import as_controls, pick_save_mp3_path, pick_text_file, snack
from .prosody_panel import ProsodyPanel
from .voice_panel import VoicePanel


class SingleTab:
    """Builds and owns the Single tab UI and its event handlers."""

    def __init__(
        self,
        page: ft.Page,
        state: AppState,
        voice: VoicePanel,
        prosody: ProsodyPanel,
        audio: fta.Audio,
    ) -> None:
        self._page = page
        self._state = state
        self._voice = voice
        self._prosody = prosody
        self._audio = audio

        self._text_field = ft.TextField(
            label="Text to synthesise",
            multiline=True,
            min_lines=8,
            max_lines=16,
            expand=True,
        )
        self._progress = ft.ProgressBar(visible=False)
        self._status = ft.Text("", color=ft.Colors.SECONDARY, italic=True)
        self._output_path_field = ft.TextField(
            label="Save MP3 to…",
            expand=True,
            read_only=True,
            hint_text="Click Browse… to choose a path",
        )
        self._srt_check = ft.Checkbox(label="Also save subtitles (.srt)", value=False)
        self._stop_btn = ft.IconButton(
            icon=ft.Icons.STOP_CIRCLE_OUTLINED,
            icon_color=ft.Colors.ERROR,
            tooltip="Stop playback",
            visible=False,
            on_click=self._on_stop_click,
        )

        audio.on_state_change = self._on_audio_state_change

        self._content = self._build()

    # ── Public interface ──────────────────────────────────────────────

    @property
    def content(self) -> ft.Column:
        return self._content

    # ── Audio callbacks ───────────────────────────────────────────────

    def _on_audio_state_change(self, e: AudioStateChangeEvent) -> None:
        state_str = str(e.state).lower()
        if "stopped" in state_str or "completed" in state_str or "disposed" in state_str:
            self._stop_btn.visible = False
            if self._status.value == "Playing…":
                self._status.value = "Finished."
            self._page.update()

    # ── Event handlers ────────────────────────────────────────────────

    def _set_busy(self, busy: bool) -> None:
        self._progress.visible = busy
        self._page.update()

    async def _on_stop_click(self) -> None:
        try:
            await self._audio.pause()
        except Exception:
            pass
        self._stop_btn.visible = False
        self._status.value = "Stopped."
        self._page.update()

    async def _on_load_txt_click(self) -> None:
        path = await pick_text_file(self._page, "Load Text File")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    self._text_field.value = fh.read()
                self._page.update()
            except Exception as ex:
                snack(self._page, f"Could not read file: {ex}")

    async def _on_browse_mp3_click(self) -> None:
        try:
            path = await pick_save_mp3_path(self._page, "Save audio as…", "output.mp3")
            if path:
                self._output_path_field.value = path
                self._page.update()
        except Exception as ex:
            snack(self._page, str(ex))

    async def _on_generate_play_click(self) -> None:
        txt = (self._text_field.value or "").strip()
        voice = self._voice.selected_voice

        if not txt:
            snack(self._page, "Please enter some text first.")
            return
        if not voice:
            snack(self._page, "Please select a voice.")
            return

        self._set_busy(True)
        self._status.value = "Generating audio…"
        self._page.update()

        try:
            if self._state.prev_tmp:
                try:
                    os.unlink(self._state.prev_tmp[0])
                except Exception:
                    pass
                self._state.prev_tmp.clear()

            fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            await tts.generate(
                txt,
                voice,
                self._prosody.rate,
                self._prosody.vol,
                self._prosody.pitch,
                tmp_path,
                srt=bool(self._srt_check.value),
            )
            self._state.prev_tmp.append(tmp_path)

            try:
                await self._audio.pause()
            except Exception:
                pass
            self._audio.src = Path(tmp_path).as_uri()
            self._page.update()
            await asyncio.sleep(0.25)
            await self._audio.play()

            self._stop_btn.visible = True
            self._status.value = "Playing…"
        except Exception as ex:
            snack(self._page, f"Error generating audio: {ex}")
            self._status.value = "Error."
        finally:
            self._set_busy(False)
            self._page.update()

    async def _on_save_mp3_click(self) -> None:
        txt = (self._text_field.value or "").strip()
        voice = self._voice.selected_voice
        out_path = (self._output_path_field.value or "").strip()

        if not txt:
            snack(self._page, "Please enter some text first.")
            return
        if not voice:
            snack(self._page, "Please select a voice.")
            return
        if not out_path:
            snack(self._page, "Please choose a save location (click Browse…).")
            return

        self._set_busy(True)
        self._status.value = "Saving…"
        self._page.update()

        try:
            await tts.generate(
                txt,
                voice,
                self._prosody.rate,
                self._prosody.vol,
                self._prosody.pitch,
                out_path,
                srt=bool(self._srt_check.value),
            )
            self._page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(f"Saved: {out_path}"),
                    bgcolor=ft.Colors.SECONDARY_CONTAINER,
                )
            )
            self._status.value = "Saved."
        except Exception as ex:
            snack(self._page, f"Error saving: {ex}")
            self._status.value = "Error."
        finally:
            self._set_busy(False)
            self._page.update()

    # ── Layout ────────────────────────────────────────────────────────

    def _build(self) -> ft.Column:
        text_input_controls = as_controls(
            ft.Text("Text Input", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            self._text_field,
            ft.OutlinedButton("📂  Load from .txt File", on_click=self._on_load_txt_click),
        )
        output_controls = as_controls(
            ft.Text("Output", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Row(
                controls=as_controls(
                    self._output_path_field,
                    ft.OutlinedButton("Browse…", on_click=self._on_browse_mp3_click),
                ),
                spacing=8,
            ),
            self._srt_check,
        )
        action_controls = as_controls(
            ft.FilledButton(
                "▶  Generate & Play", on_click=self._on_generate_play_click, expand=True
            ),
            ft.OutlinedButton("💾  Save to File", on_click=self._on_save_mp3_click, expand=True),
            self._stop_btn,
        )
        tab_controls: list[ft.Control] = [
            ft.Card(
                content=ft.Container(
                    padding=16,
                    content=ft.Column(spacing=8, controls=text_input_controls),
                ),
            ),
            ft.Card(
                content=ft.Container(
                    padding=16,
                    content=ft.Column(spacing=8, controls=output_controls),
                ),
            ),
            ft.Row(spacing=10, controls=action_controls),
            self._progress,
            self._status,
        ]
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            controls=tab_controls,
        )
