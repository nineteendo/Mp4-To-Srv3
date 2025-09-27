"""Convert an image to ASCII art."""
from __future__ import annotations

__all__: list[str] = ["convert_to_ascii"]

from typing import TYPE_CHECKING
import sys
from math import ceil, floor, inf

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from convert_to_frames import CHAR_ASPECT_RATIO

if TYPE_CHECKING:
    _Box = tuple[float, float, float, float]
    _Color = tuple[float, float, float]


def _get_avg_color(arr: NDArray, box: _Box) -> _Color:
    x1, y1, x2, y2 = box
    return arr[floor(y1):ceil(y2), floor(x1):ceil(x2)].mean((0, 1))


def _color2brightness(color: _Color) -> float:
    r, g, b = color
    return 0.299 * r + 0.587 * g + 0.114 * b


# pylint: disable-next=R0914
def _get_avg_colors(arr: NDArray, box: _Box) -> list[_Color]:
    x1, y1, x2, y2 = box
    sub_pixel_width: float = (x2 - x1) / 2
    sub_pixel_height: float = (y2 - y1) / 4
    avg_colors: list[_Color] = []
    for j in range(4):
        sub_y1: float = y1 + j * sub_pixel_height
        sub_y2: float = y1 + (j + 1) * sub_pixel_height
        for i in range(2):
            sub_x1: float = x1 + i * sub_pixel_width
            sub_x2: float = x1 + (i + 1) * sub_pixel_width
            sub_box: _Box = sub_x1, sub_y1, sub_x2, sub_y2
            avg_colors.append(_get_avg_color(arr, sub_box))

    return avg_colors


def _get_best_idxs(colors: NDArray) -> NDArray:
    x: NDArray = np.array(list(map(_color2brightness, colors)))
    all_idxs: NDArray = np.argsort(x)
    best_dev: float = inf
    best_idxs: NDArray = np.array([])
    for k in range(8):
        rem_idxs, idxs = all_idxs[:k], all_idxs[k:]
        dev: float = sum(x[rem_idxs]) + sum(abs(x[idxs] - np.median(x[idxs])))
        if dev < best_dev:
            best_dev = dev
            best_idxs = idxs

    return best_idxs


def _color2id(color: _Color) -> int:
    r, g, b = color
    r = round(r / 255 * 15)
    g = round(g / 255 * 15)
    b = round(b / 255 * 15)
    return 256 * r + 16 * g + b


def _get_colored_char(arr: NDArray, box: _Box) -> tuple[int, str]:
    colors: NDArray = np.array(_get_avg_colors(arr, box))
    idxs: NDArray = _get_best_idxs(colors)
    color: _Color = np.mean(colors[idxs], axis=0) if len(idxs) else (0, 0, 0)
    value: int = 0
    for idx in idxs:
        value |= 1 << idx

    return _color2id(color), chr(0x2800 + value)


# pylint: disable-next=R0914
def _convert_img_to_ascii(
    palette: dict[int, int], img: Image.Image, rows: int
) -> str:
    arr: NDArray = np.array(img)
    cols: int = round(rows / CHAR_ASPECT_RATIO * img.width / img.height)
    pixel_height: float = img.height / rows
    pixel_width: float = img.width / cols
    if cols > img.width or rows > img.height:
        print("Image too small for specified rows!")
        sys.exit(1)

    ascii_img: list[str] = []
    prev_color_id: int = -1
    for j in range(rows):
        if j:
            ascii_img.append('\n')

        y1: float = j * pixel_height
        y2: float = (j + 1) * pixel_height
        for i in range(cols):
            x1: float = i * pixel_width
            x2: float = (i + 1) * pixel_width
            color_id, char = _get_colored_char(arr, (x1, y1, x2, y2))
            if color_id != prev_color_id:
                palette_id: int = palette.setdefault(color_id, len(palette))
                ascii_img.append(f"<s p={palette_id}>")
                prev_color_id = color_id

            ascii_img.append(char)

    return ''.join(ascii_img)


# pylint: disable-next=R0913, R0917
def convert_to_ascii(
    palette: dict[int, int],
    frame: Image.Image,
    frame_num: int,
    fps: float,
    rows: int,
    submsoffset: int,
) -> str:
    """Convert a video frame to an SRV3 subtitle entry with ASCII art."""
    start: float = floor(1000 * frame_num / fps + submsoffset)
    duration: float = floor(1000 / fps)
    ascii_img: str = _convert_img_to_ascii(palette, frame, rows)
    return f'<p t={start} d={duration}>{ascii_img}</p>\n'
