"""Convert subtitles to meta subtitles."""
from __future__ import annotations

__all__: list[str] = ["convert_to_meta_subtitles"]

from math import ceil, floor

from pysrt import SubRipFile, SubRipItem  # type: ignore


def _append_subtitle(
    subtitles: list[str], start: float, duration: float, text: str
) -> None:
    subtitles.append(
        f"<p t={ceil(start)} d={floor(duration)} wp=1 ws=1>{text}</p>"
    )


def _split_subtitle(
    sub: SubRipItem, fps: float, submsoffset: int
) -> list[str]:
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


def convert_to_meta_subtitles(subfile: str, fps: float, submsoffset: int):
    """Convert subtitles to meta subtitles."""
    meta_subtitles: list[str] = []
    with open(subfile, "r", encoding="utf-8") as fp:
        for sub in SubRipFile.stream(fp):
            meta_subtitles.extend(_split_subtitle(sub, fps, submsoffset))

    return meta_subtitles
