"""Convert an image to ASCII art."""
from __future__ import annotations

__all__: list[str] = ["convert_to_subtitles"]

from typing import TYPE_CHECKING, Any
from math import ceil, floor, inf

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from convert_to_frames import CHAR_ASPECT_RATIO, print_progress_bar

if TYPE_CHECKING:
    _Color = NDArray

_DECAY: float = 0.5 ** (1 / 2)
_DOT_POSITIONS: NDArray = np.array([
    1 << 0, 1 << 3,
    1 << 1, 1 << 4,
    1 << 2, 1 << 5,
    1 << 6, 1 << 7
])


def _blend_frames(frames: list[Image.Image]) -> Image.Image:
    weights: NDArray = _DECAY ** np.arange(len(frames), 0, -1)
    arr: NDArray = np.average(np.array(frames), 0, weights)
    return Image.fromarray(arr.round().astype(np.uint8))


def _get_dev(x: NDArray) -> float:
    n: int = len(x)
    mid: int = n // 2
    med: float = x[mid] if n % 2 else (x[mid - 1] + x[mid]) / 2
    return np.abs(x - med).sum()


def _get_best_idxs(colors: NDArray, layer_mask: slice) -> NDArray:
    brightnesses: NDArray = colors.dot([0.299, 0.587, 0.114])
    all_idxs: NDArray = brightnesses.argsort()[layer_mask]
    brightnesses = brightnesses[all_idxs]
    rem_dev: float = 0
    best_dev: float = inf
    best_k: int = 0
    for k, brightness in enumerate(brightnesses):
        if (dev := _get_dev(brightnesses[k:]) + rem_dev) < best_dev:
            best_dev = dev
            best_k = k

        rem_dev += brightness

    return all_idxs[best_k:]


def _color2id(color: _Color) -> int:
    r, g, b = color
    r = round(r / 255 * 15)
    g = round(g / 255 * 15)
    b = round(b / 255 * 15)
    return 256 * r + 16 * g + b


def _get_colored_char(sub_arr: NDArray, layer_mask: slice) -> tuple[int, str]:
    colors: NDArray = sub_arr.reshape(-1, 3)
    idxs: NDArray = _get_best_idxs(colors, layer_mask)
    avg_color: NDArray = colors[idxs].mean(0)
    value: int = 0x2800
    for idx in idxs:
        value |= _DOT_POSITIONS[idx]

    return _color2id(avg_color), chr(value)


# pylint: disable-next=R0914
def _convert_img_to_ascii(
    palette: dict[int, int], img: Image.Image, rows: int, layer_mask: slice
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
            sub_arr: NDArray = arr[4 * j: 4 * j + 4, 2 * i: 2 * i + 2]
            color_id, char = _get_colored_char(sub_arr, layer_mask)
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
def _convert_to_subtitle_entry(
    palette: dict[int, int],
    frames: list[Image.Image],
    frame_num: int,
    fps: float,
    submsoffset: int,
    rows: int,
    layer_mask: slice,
) -> dict[str, Any]:
    start: float = 1000 * frame_num / fps + submsoffset
    duration: float = 1000 / fps
    frame: Image.Image = _blend_frames(frames)
    palette_id, ascii_img = _convert_img_to_ascii(
        palette, frame, rows, layer_mask
    )
    return {
        "start": start,
        "duration": duration,
        "palette_id": palette_id,
        "ascii_img": ascii_img
    }


def convert_to_subtitles(
    frames_list: list[list[Image.Image]],
    fps: float,
    submsoffset: int,
    rows: int,
    layers: int
) -> tuple[list[str], dict[int, int]]:
    """Convert video frames list to SRV3 subtitles with ASCII art."""
    print('Generating ASCII art...')
    palette: dict[int, int] = {}
    subtitles: list[str] = []
    iteration: int = 0
    layer_step: float = 8 / layers
    for layer_idx in range(layers):
        layer_mask: slice = slice(
            round(layer_step * layer_idx), round(layer_step * (layer_idx + 1))
        )
        entries: list[dict[str, Any]] = []
        for idx, frames in enumerate(frames_list):
            entry: dict[str, Any] = _convert_to_subtitle_entry(
                palette, frames, idx, fps, submsoffset, rows, layer_mask
            )
            iteration += 1
            print_progress_bar(iteration, len(frames_list) * layers)
            if (
                entries
                and entry['palette_id'] == entries[-1]['palette_id']
                and entry['ascii_img'] == entries[-1]['ascii_img']
            ):
                entries[-1]['duration'] += entry['duration']
            else:
                entries.append(entry)

        subtitles.extend([
            f"<p t={ceil(entry['start'])} d={floor(entry['duration'])} "
            f"wp=0 ws=0 p={entry['palette_id']}>{entry['ascii_img']}</p>"
            for entry in entries
        ])

    print()
    return subtitles, palette
