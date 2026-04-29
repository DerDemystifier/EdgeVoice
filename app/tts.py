"""Pure TTS helper functions — no Flet dependency."""

from __future__ import annotations

import re
from pathlib import Path

import edge_tts


def fmt_rate(v: float) -> str:
    vi = int(v)
    return f"+{vi}%" if vi >= 0 else f"{vi}%"


def fmt_vol(v: float) -> str:
    vi = int(v)
    return f"+{vi}%" if vi >= 0 else f"{vi}%"


def fmt_pitch(v: float) -> str:
    vi = int(v)
    return f"+{vi}Hz" if vi >= 0 else f"{vi}Hz"


def sanitize_name(text: str) -> str:
    """Return a filesystem-safe snippet (max 20 chars) for use in filenames."""
    s = re.sub(r"[^\w\s-]", "", text[:20]).strip()
    return re.sub(r"\s+", "_", s) or "output"


async def generate(
    text: str,
    voice: str,
    rate: str,
    vol: str,
    pitch: str,
    out_path: str,
    srt: bool = False,
) -> None:
    """Synthesise *text* and write MP3 (+ optional SRT) to *out_path*."""
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=vol, pitch=pitch)
    sub = edge_tts.SubMaker()
    with open(out_path, "wb") as fh:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                data = chunk.get("data")
                if data:
                    fh.write(data)
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                sub.feed(chunk)
    if srt:
        srt_path = str(Path(out_path).with_suffix(".srt"))
        with open(srt_path, "w", encoding="utf-8") as sh:
            sh.write(sub.get_srt())
