"""Shared UI helper utilities."""
from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import TypeVar

import flet as ft

try:
    import tkinter as tk
    from tkinter import filedialog
except Exception:  # pragma: no cover - platform-specific availability
    tk = None
    filedialog = None


T = TypeVar("T")


def as_controls(*controls: ft.Control) -> list[ft.Control]:
    """Return a precisely typed list of Flet controls for Pylance."""
    return list(controls)


def snack(page: ft.Page, msg: str, error: bool = True) -> None:
    """Show a SnackBar with *msg*."""
    bg_color = ft.Colors.ERROR_CONTAINER if error else ft.Colors.SECONDARY_CONTAINER
    text_color = ft.Colors.ON_ERROR_CONTAINER if error else ft.Colors.ON_SECONDARY_CONTAINER
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(msg, color=text_color),
            bgcolor=bg_color,
        )
    )


def _run_tk_dialog(dialog: Callable[[], T]) -> T:
    if tk is None or filedialog is None:
        raise RuntimeError("tkinter file dialogs are unavailable in this environment.")

    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
    except tk.TclError:
        pass

    root.update_idletasks()
    try:
        return dialog()
    finally:
        root.destroy()


async def pick_text_file(page: ft.Page, title: str) -> str | None:
    if not page.web and tk is not None and filedialog is not None:
        dialog_api = filedialog
        return await asyncio.to_thread(
            _run_tk_dialog,
            lambda: dialog_api.askopenfilename(
                title=title,
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            )
            or None,
        )

    files = await ft.FilePicker().pick_files(
        dialog_title=title,
        file_type=ft.FilePickerFileType.CUSTOM,
        allowed_extensions=["txt"],
    )
    if files and files[0].path:
        return files[0].path
    return None


async def pick_save_mp3_path(page: ft.Page, title: str, file_name: str) -> str | None:
    if not page.web and tk is not None and filedialog is not None:
        dialog_api = filedialog
        return await asyncio.to_thread(
            _run_tk_dialog,
            lambda: dialog_api.asksaveasfilename(
                title=title,
                initialfile=file_name,
                defaultextension=".mp3",
                filetypes=[("MP3 files", "*.mp3")],
            )
            or None,
        )

    if page.web:
        raise RuntimeError(
            "Choosing a save path is only supported in the desktop app."
        )

    return await ft.FilePicker().save_file(
        dialog_title=title,
        file_name=file_name,
        file_type=ft.FilePickerFileType.CUSTOM,
        allowed_extensions=["mp3"],
    )


async def pick_directory(page: ft.Page, title: str) -> str | None:
    if not page.web and tk is not None and filedialog is not None:
        dialog_api = filedialog
        return await asyncio.to_thread(
            _run_tk_dialog,
            lambda: dialog_api.askdirectory(title=title, mustexist=True) or None,
        )

    if page.web:
        raise RuntimeError(
            "Choosing an output folder is only supported in the desktop app."
        )

    return await ft.FilePicker().get_directory_path(dialog_title=title)
