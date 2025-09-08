"""Convert an image to ASCII art."""
from __future__ import annotations

__all__: list[str] = ["convert_to_ascii"]

from typing import TYPE_CHECKING
import sys
from math import ceil, floor

import numpy as np
from PIL import Image

from convert_to_frames import CHAR_ASPECT_RATIO

if TYPE_CHECKING:
    _Box = tuple[float, float, float, float]


def _get_avg_brightness(img: Image.Image, box: _Box) -> float:
    x1, y1, x2, y2 = box
    box = floor(x1), floor(y1), ceil(x2), ceil(y2)
    return np.average(np.array(img.crop(box)))


# pylint: disable-next=R0914
def _get_avg_brightnesses(img: Image.Image, box: _Box) -> list[float]:
    x1, y1, x2, y2 = box
    sub_pixel_width: float = (x2 - x1) / 2
    sub_pixel_height: float = (y2 - y1) / 4
    arr: list[float] = []
    for j in range(4):
        sub_y1: float = y1 + j * sub_pixel_height
        sub_y2: float = y1 + (j + 1) * sub_pixel_height
        for i in range(2):
            sub_x1: float = x1 + i * sub_pixel_width
            sub_x2: float = x1 + (i + 1) * sub_pixel_width
            sub_box: _Box = sub_x1, sub_y1, sub_x2, sub_y2
            arr.append(_get_avg_brightness(img, sub_box))

    return arr


def _get_char(img: Image.Image, box: _Box) -> str:
    dots: int = round(_get_avg_brightness(img, box) / 255 * 8)
    value: int = 0
    for idx in np.argsort(_get_avg_brightnesses(img, box))[8 - dots:]:
        value |= 1 << idx

    return f"<font color='#fff'>{chr(0x2800 + value)}</font>"


def _convert_img_to_ascii(img: Image.Image, rows: int) -> str:
    img = img.convert('L')
    cols: int = round(rows / CHAR_ASPECT_RATIO * img.width / img.height)
    pixel_height: float = img.height / rows
    pixel_width: float = img.width / cols
    if cols > img.width or rows > img.height:
        print("Image too small for specified rows!")
        sys.exit(1)

    ascii_img: list[str] = []
    for j in range(rows):
        if j:
            ascii_img.append('<br>\n')

        y1: float = j * pixel_height
        y2: float = (j + 1) * pixel_height
        for i in range(cols):
            x1: float = i * pixel_width
            x2: float = (i + 1) * pixel_width
            ascii_img.append(_get_char(img, (x1, y1, x2, y2)))

    return ''.join(ascii_img)


def convert_to_ascii(
    frame: Image.Image,
    frame_num: int,
    ms_per_frame: float,
    rows: int,
    submsoffset: int
) -> str:
    """Convert a video frame to an SAMI subtitle entry with ASCII art."""
    start: float = floor(frame_num * ms_per_frame + submsoffset)
    ascii_img: str = _convert_img_to_ascii(frame, rows)
    return f'<sync start={start}>\n{ascii_img}\n</sync>'
