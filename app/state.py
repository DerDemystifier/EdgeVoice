"""Shared mutable application state."""

from __future__ import annotations

from dataclasses import dataclass, field

from edge_tts.typing import Voice


@dataclass
class AppState:
    all_voices: list[Voice] = field(default_factory=list)
    prev_tmp: list[str] = field(default_factory=list)
    bulk_items: list[dict] = field(default_factory=list)
