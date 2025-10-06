"""Split up subtitle."""
from __future__ import annotations

__all__: list[str] = ["split_subtitle"]

from math import ceil, floor

from pysrt import SubRipItem  # type: ignore


def _append_subtitle(
    subtitles: list[str], start: float, duration: float, text: str
) -> None:
    subtitles.append(f"<p t={ceil(start)} d={floor(duration)}>{text}</p>\n")


def split_subtitle(sub: SubRipItem, fps: float, submsoffset: int) -> list[str]:
    """Split up subtitle."""
    frame_duration: float = 1000 / fps
    subtitles: list[str] = []
    start: float = sub.start.ordinal
    end: float = sub.end.ordinal
    new_start: float = (
        frame_duration * floor((start - submsoffset) / frame_duration + 1)
        + submsoffset
    )
    while new_start < end:
        _append_subtitle(subtitles, start, new_start - start, sub.text)
        start, new_start = new_start, new_start + frame_duration

    if start < end:
        _append_subtitle(subtitles, start, end - start, sub.text)

    return subtitles
