"""Convert an image to ASCII art."""
from __future__ import annotations

__all__: list[str] = ["convert_to_ascii"]

from typing import TYPE_CHECKING, Any
from math import inf

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from convert_to_frames import CHAR_ASPECT_RATIO

if TYPE_CHECKING:
    _Color = NDArray


def _get_dev(x: NDArray) -> float:
    n: int = len(x)
    mid: int = n // 2
    med: float = x[mid] if n % 2 else (x[mid - 1] + x[mid]) / 2
    return abs(x - med).sum()


def _get_best_idxs(colors: NDArray) -> NDArray:
    brightnesses: NDArray = np.dot(colors, [0.299, 0.587, 0.114])
    all_idxs: NDArray = brightnesses.argsort()
    sorted_brightnesses: NDArray = brightnesses[all_idxs]
    rem_dev: float = 0
    best_dev: float = inf
    best_k: int = 0
    for k in range(8):
        if (dev := _get_dev(sorted_brightnesses[k:]) + rem_dev) < best_dev:
            best_dev = dev
            best_k = k

        rem_dev += sorted_brightnesses[k]

    return all_idxs[best_k:]


def _color2id(color: _Color) -> int:
    r, g, b = color
    r = round(r / 255 * 15)
    g = round(g / 255 * 15)
    b = round(b / 255 * 15)
    return 256 * r + 16 * g + b


def _get_colored_char(sub_arr: NDArray) -> tuple[int, str]:
    colors: NDArray = sub_arr.reshape(-1, 3)
    idxs: NDArray = _get_best_idxs(colors)
    color_id: int = _color2id(colors[idxs].mean(0)) if len(idxs) else 0
    value: int = 0x2800
    for idx in idxs:
        value |= 1 << idx

    return color_id, chr(value)


# pylint: disable-next=R0914
def _convert_img_to_ascii(
    palette: dict[int, int], img: Image.Image, rows: int
) -> tuple[int, str]:
    cols: int = round(rows / CHAR_ASPECT_RATIO * img.width / img.height)
    img = img.resize((2 * cols, 4 * rows), Image.Resampling.LANCZOS)
    arr: NDArray = np.array(img)
    ascii_img: list[str] = []
    prev_color_id: int = -1
    first_palette_id: int = -1
    for j in range(rows):
        if j:
            ascii_img.append('\n')

        for i in range(cols):
            sub_arr: NDArray = arr[4 * j:4 * j + 4, 2 * i:2 * i + 2]
            color_id, char = _get_colored_char(sub_arr)
            if color_id != prev_color_id:
                palette_id: int = palette.setdefault(color_id, len(palette))
                if first_palette_id == -1:
                    first_palette_id = palette_id
                elif palette_id == first_palette_id:
                    ascii_img.append("<s>")
                else:
                    ascii_img.append(f"<s p={palette_id}>")

                prev_color_id = color_id

            ascii_img.append(char)

    return first_palette_id, ''.join(ascii_img)


# pylint: disable-next=R0913, R0917
def convert_to_ascii(
    palette: dict[int, int],
    frame: Image.Image,
    frame_num: int,
    fps: float,
    rows: int,
    submsoffset: int,
) -> dict[str, Any]:
    """Convert a video frame to an SRV3 subtitle entry with ASCII art."""
    start: float = 1000 * frame_num / fps + submsoffset
    duration: float = 1000 / fps
    palette_id, ascii_img = _convert_img_to_ascii(palette, frame, rows)
    return {
        "start": start,
        "duration": duration,
        "palette_id": palette_id,
        "ascii_img": ascii_img
    }
