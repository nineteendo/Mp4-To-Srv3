"""Convert an image to ASCII art."""
from __future__ import annotations
import sys

__all__: list[str] = ["convert_to_ascii"]

from math import ceil, floor

import numpy as np
from numpy.typing import NDArray
from PIL import Image

_SCALE: float = 0.43
_CHARS: str = '`"+1nuL0qpdbo8$'


def _format_ms(ms: float) -> str:
    hh, remainder = divmod(int(ms), 3_600_000)
    mm, remainder = divmod(remainder, 60_000)
    ss, mss = divmod(remainder, 1_000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{mss:03d}"


def _get_avg_brightness(
    img: Image.Image, box: tuple[int, int, int, int]
) -> float:
    arr: NDArray = np.array(img.crop(box))
    width, height = arr.shape
    return np.average(arr.reshape(width * height))


# pylint: disable-next=R0914
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
            avg_brightness: float = _get_avg_brightness(img, (x1, y1, x2, y2))
            char: str = _CHARS[int(avg_brightness / 255 * (len(_CHARS) - 1))]
            if char in {'"', '`'}:
                char += ' '

            ascii_img.append(char)

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
    start_time: str = _format_ms(ms)
    end_time: str = _format_ms(ms + ms_per_frame)
    return f'{frame_num + 1}\n{start_time} --> {end_time}\n{ascii_img}'
