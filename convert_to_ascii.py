"""Convert an image to ASCII art."""
from __future__ import annotations

__all__: list[str] = ["convert_to_ascii"]

from typing import TYPE_CHECKING
import sys
from math import ceil, floor

import numpy as np
from PIL import Image

if TYPE_CHECKING:
    _Box = tuple[int, int, int, int]

_SCALE: float = 0.43
_CHARS: str = '⠀⡀⣀⣄⣤⣦⣶⣷⣿'


def _format_ms(ms: int) -> str:
    hh, remainder = divmod(ms, 3_600_000)
    mm, remainder = divmod(remainder, 60_000)
    ss, mss = divmod(remainder, 1_000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{mss:03d}"


def _get_avg_brightness(img: Image.Image, box: _Box) -> float:
    return np.average(np.array(img.crop(box)))


def _get_char(img: Image.Image, box: _Box) -> str:
    avg_brightness: float = _get_avg_brightness(img, box)
    char: str = _CHARS[round(avg_brightness / 255 * (len(_CHARS) - 1))]
    if char in {'"', '`'}:
        char += ' '

    return char


def _convert_img_to_ascii(img: Image.Image, rows: int) -> str:
    img = img.convert('L')
    width, height = img.size
    pixel_height: float = height / rows
    pixel_width: float = pixel_height * _SCALE
    cols: int = int(width / pixel_width)
    if cols > width or rows > height:
        print("Image too small for specified rows!")
        sys.exit(1)

    ascii_img: list[str] = []
    for j in range(rows):
        y1: int = floor(j * pixel_height)
        y2: int = ceil((j + 1) * pixel_height)
        for i in range(cols):
            x1: int = floor(i * pixel_width)
            x2: int = ceil((i + 1) * pixel_width)
            ascii_img.append(_get_char(img, (x1, y1, x2, y2)))

        ascii_img.append('\n')

    return ''.join(ascii_img)


def convert_to_ascii(
    frame: Image.Image,
    frame_num: int,
    ms_per_frame: float,
    rows: int,
    submsoffset: int
) -> str:
    """Convert a video frame to an SRT subtitle entry with ASCII art."""
    ascii_img: str = _convert_img_to_ascii(frame, rows)
    ms: float = frame_num * ms_per_frame + submsoffset
    start_time: str = _format_ms(floor(ms))
    end_time: str = _format_ms(ceil(ms + ms_per_frame))
    return f'{frame_num + 1}\n{start_time} --> {end_time}\n{ascii_img}'
