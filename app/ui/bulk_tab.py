"""Bulk TTS tab — generate many MP3 files from a list of text items."""

from __future__ import annotations

import asyncio
import math
import os
from functools import partial
from time import perf_counter

import flet as ft

from .. import tts
from ..state import AppState
from .helpers import as_controls, pick_directory, pick_text_file, snack
from .prosody_panel import ProsodyPanel
from .voice_panel import VoicePanel

BULK_DELAY_SECONDS = 1.0


class BulkTab:
    """Builds and owns the Bulk tab UI and its event handlers."""

    def __init__(
        self,
        page: ft.Page,
        state: AppState,
        voice: VoicePanel,
        prosody: ProsodyPanel,
    ) -> None:
        self._page = page
        self._state = state
        self._voice = voice
        self._prosody = prosody

        self._srt_check = ft.Checkbox(label="Also save subtitles (.srt)", value=False)
        self._status = ft.Text("", color=ft.Colors.SECONDARY, italic=True)
        self._progress = ft.ProgressBar(visible=False, value=0)
        self._count_text = ft.Text("0 / 0", color=ft.Colors.SECONDARY)
        self._eta_field = ft.TextField(label="ETA", value="—", width=130, read_only=True)
        self._folder_field = ft.TextField(
            label="Output folder",
            expand=True,
            read_only=True,
            hint_text="Click Browse… to choose a folder",
        )

        self._table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("#"), numeric=True),
                ft.DataColumn(label=ft.Text("Text Preview"), numeric=False),
                ft.DataColumn(label=ft.Text("Status"), numeric=False),
                ft.DataColumn(label=ft.Text(""), numeric=False),
            ],
            rows=[],
            show_checkbox_column=False,
            column_spacing=16,
            data_row_min_height=44,
            heading_row_height=40,
        )

        self._generate_btn = ft.FilledButton(
            "▶  Bulk Generate",
            expand=True,
            on_click=self._on_generate_click,
        )

        self._content = self._build()

    # ── Public interface ──────────────────────────────────────────────

    @property
    def content(self) -> ft.Column:
        return self._content

    # ── Table helpers ─────────────────────────────────────────────────

    @staticmethod
    def _status_color(status: str) -> str:
        if status == "Done":
            return ft.Colors.GREEN
        if status == "Generating":
            return ft.Colors.BLUE
        if status.startswith("Error"):
            return ft.Colors.ERROR
        return ft.Colors.SECONDARY

    def _rebuild_table(self) -> None:
        rows: list[ft.DataRow] = []
        done_count = 0
        for i, item in enumerate(self._state.bulk_items):
            preview = item["text"][:70].replace("\n", " ")
            if len(item["text"]) > 70:
                preview += "…"
            status = item["status"]
            if status == "Done":
                done_count += 1

            action_controls: list[ft.Control] = [
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    icon_size=18,
                    tooltip="Edit",
                    on_click=partial(self._open_edit_dialog, i),
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=18,
                    icon_color=ft.Colors.ERROR,
                    tooltip="Delete",
                    on_click=partial(self._delete_row, i),
                ),
            ]
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(i + 1))),
                        ft.DataCell(ft.Text(preview)),
                        ft.DataCell(ft.Text(status, color=self._status_color(status))),
                        ft.DataCell(ft.Row(action_controls, spacing=0)),
                    ],
                )
            )

        self._table.rows = rows
        self._count_text.value = f"{done_count} / {len(self._state.bulk_items)}"

    @staticmethod
    def _format_eta(seconds: float) -> str:
        total_seconds = max(0, math.ceil(seconds))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def _set_eta(self, seconds: float | None) -> None:
        self._eta_field.value = "Estimating…" if seconds is None else self._format_eta(seconds)

    def _invalidate_eta(self) -> None:
        self._eta_field.value = "—"

    # ── Dialog helpers ────────────────────────────────────────────────

    def _open_edit_dialog(self, idx: int) -> None:
        item = self._state.bulk_items[idx]
        edit_field = ft.TextField(
            value=item["text"],
            multiline=True,
            min_lines=4,
            max_lines=10,
            label="Text",
        )

        def on_save() -> None:
            text = (edit_field.value or "").strip()
            if text:
                self._state.bulk_items[idx]["text"] = text
                self._state.bulk_items[idx]["status"] = "Pending"
            self._invalidate_eta()
            self._rebuild_table()
            self._page.update()
            self._page.pop_dialog()

        self._page.show_dialog(
            ft.AlertDialog(
                title=ft.Text(f"Edit Row {idx + 1}"),
                content=ft.Container(content=edit_field, width=520),
                actions=as_controls(
                    ft.FilledButton("Save", on_click=on_save),
                    ft.TextButton("Cancel", on_click=self._page.pop_dialog),
                ),
            )
        )

    def _delete_row(self, idx: int) -> None:
        def confirm() -> None:
            self._state.bulk_items.pop(idx)
            self._invalidate_eta()
            self._rebuild_table()
            self._page.update()
            self._page.pop_dialog()

        self._page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Delete Row?"),
                content=ft.Text(f"Delete row {idx + 1}? This cannot be undone.", width=380),
                actions=as_controls(
                    ft.FilledButton(
                        "Delete",
                        on_click=confirm,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR),
                    ),
                    ft.TextButton("Cancel", on_click=self._page.pop_dialog),
                ),
            )
        )

    def _open_add_dialog(self) -> None:
        add_field = ft.TextField(
            label="Text for this item",
            multiline=True,
            min_lines=4,
            max_lines=10,
            autofocus=True,
        )

        def on_add() -> None:
            txt = (add_field.value or "").strip()
            if txt:
                self._state.bulk_items.append({"text": txt, "status": "Pending"})
                self._invalidate_eta()
                self._rebuild_table()
                self._page.update()
            self._page.pop_dialog()

        self._page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Add Bulk Item"),
                content=ft.Container(content=add_field, width=520),
                actions=as_controls(
                    ft.FilledButton("Add", on_click=on_add),
                    ft.TextButton("Cancel", on_click=self._page.pop_dialog),
                ),
            )
        )

    # ── Event handlers ────────────────────────────────────────────────

    async def _on_import_txt_click(self) -> None:
        path = await pick_text_file(self._page, "Import .txt (one entry per line)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    lines = [ln.strip() for ln in fh if ln.strip()]
                for line in lines:
                    self._state.bulk_items.append({"text": line, "status": "Pending"})
                self._invalidate_eta()
                self._rebuild_table()
                self._page.update()
                added_count = len(lines)
                line_label = "line" if added_count == 1 else "lines"
                snack(
                    self._page,
                    f"Added {added_count} {line_label} from {os.path.basename(path)}.",
                    error=False,
                )
            except Exception as ex:
                snack(self._page, f"Could not read file: {ex}")

    async def _on_folder_click(self) -> None:
        try:
            path = await pick_directory(self._page, "Select Output Folder")
            if path:
                self._folder_field.value = path
                self._page.update()
        except Exception as ex:
            snack(self._page, str(ex))

    def _on_clear_all_click(self) -> None:
        if not self._state.bulk_items:
            return

        def do_clear() -> None:
            self._state.bulk_items.clear()
            self._invalidate_eta()
            self._rebuild_table()
            self._page.update()
            self._page.pop_dialog()

        self._page.show_dialog(
            ft.AlertDialog(
                title=ft.Text("Clear All?"),
                content=ft.Text(f"Remove all {len(self._state.bulk_items)} item(s)?", width=300),
                actions=as_controls(
                    ft.FilledButton(
                        "Clear All",
                        on_click=do_clear,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR),
                    ),
                    ft.TextButton("Cancel", on_click=self._page.pop_dialog),
                ),
            )
        )

    async def _on_generate_click(self) -> None:
        voice = self._voice.selected_voice
        folder = (self._folder_field.value or "").strip()

        if not self._state.bulk_items:
            snack(self._page, "No items to generate.")
            return
        if not voice:
            snack(self._page, "Please select a voice.")
            return
        if not folder:
            snack(self._page, "Please choose an output folder.")
            return
        if not os.path.isdir(folder):
            snack(self._page, "Output folder does not exist.")
            return

        total = len(self._state.bulk_items)
        done = 0
        self._generate_btn.disabled = True
        self._progress.visible = True
        self._progress.value = 0
        self._status.value = "Starting…"
        self._set_eta(None)
        self._page.update()

        rate = self._prosody.rate
        vol = self._prosody.vol
        pitch = self._prosody.pitch
        make_srt = bool(self._srt_check.value)
        total_generation_seconds = 0.0

        for i, item in enumerate(self._state.bulk_items):
            item["status"] = "Generating"
            self._rebuild_table()
            self._status.value = f"Processing {i + 1} / {total}…"
            self._page.update()

            filename = f"{i + 1:03d}_{tts.sanitize_name(item['text'])}.mp3"
            out_path = os.path.join(folder, filename)
            item_started = perf_counter()

            try:
                await tts.generate(item["text"], voice, rate, vol, pitch, out_path, srt=make_srt)
                item["status"] = "Done"
                done += 1
            except Exception as ex:
                item["status"] = f"Error: {str(ex)[:50]}"
            finally:
                total_generation_seconds += perf_counter() - item_started

            self._progress.value = (i + 1) / total
            remaining_items = total - (i + 1)
            if remaining_items > 0:
                average_generation_seconds = total_generation_seconds / (i + 1)
                self._set_eta(
                    (average_generation_seconds * remaining_items)
                    + (BULK_DELAY_SECONDS * remaining_items)
                )
            else:
                self._set_eta(0)
            self._rebuild_table()
            self._page.update()

            if remaining_items > 0:
                self._status.value = (
                    f"Cooling down for {self._format_eta(BULK_DELAY_SECONDS)} before next item…"
                )
                self._page.update()
                await asyncio.sleep(BULK_DELAY_SECONDS)

        self._generate_btn.disabled = False
        self._progress.visible = False
        self._status.value = f"✓ Done — {done}/{total} file(s) generated in {folder}"
        self._page.update()

    # ── Layout ────────────────────────────────────────────────────────

    def _build(self) -> ft.Column:
        items_header = as_controls(
            ft.Text("Bulk Items", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, expand=True),
            ft.OutlinedButton("➕  Add Row", on_click=self._open_add_dialog),
            ft.OutlinedButton("📂  Import .txt", on_click=self._on_import_txt_click),
            ft.TextButton(
                "Clear All",
                on_click=self._on_clear_all_click,
                style=ft.ButtonStyle(color=ft.Colors.ERROR),
            ),
        )
        output_controls = as_controls(
            ft.Text("Output", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Row(
                controls=as_controls(
                    self._folder_field,
                    ft.OutlinedButton("Browse…", on_click=self._on_folder_click),
                ),
                spacing=8,
            ),
            self._srt_check,
        )
        action_controls = as_controls(
            self._generate_btn,
            self._count_text,
            self._eta_field,
        )
        tab_controls: list[ft.Control] = [
            ft.Card(
                # margin=ft.Margin.symmetric(vertical=0, horizontal=24),
                content=ft.Container(
                    padding=16,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(spacing=8, controls=items_header),
                            ft.Container(
                                content=ft.Column([self._table], scroll=ft.ScrollMode.AUTO),
                                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                                border_radius=8,
                                height=300,
                            ),
                        ],
                    ),
                ),
            ),
            ft.Card(
                # margin=ft.Margin.symmetric(vertical=0, horizontal=24),
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
            width=800,
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            controls=tab_controls,
        )
