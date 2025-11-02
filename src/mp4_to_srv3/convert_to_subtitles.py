"""Convert an image to ASCII art."""
from __future__ import annotations

__all__: list[str] = ["convert_to_subtitles"]

from typing import TYPE_CHECKING, Any
from math import ceil, floor, inf

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from mp4_to_srv3.convert_to_frames import CHAR_ASPECT_RATIO, print_progress_bar

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


def _get_best_idxs_list(colors: NDArray, layers: int) -> list[NDArray]:
    all_brightnesses: NDArray = colors.dot([0.299, 0.587, 0.114])
    all_idxs: NDArray = all_brightnesses.argsort()
    best_k: int = 0
    best_idxs_list: list[NDArray] = []
    layer_step: float = 8 / layers
    for layer_idx in range(layers)[::-1]:
        idxs: NDArray = all_idxs[
            round(layer_step * layer_idx):
            round(layer_step * (layer_idx + 1)) + best_k
        ]
        brightnesses = all_brightnesses[idxs]
        rem_dev: float = 0
        best_dev: float = inf
        for k, brightness in enumerate(brightnesses):
            if (dev := _get_dev(brightnesses[k:]) + rem_dev) < best_dev:
                best_dev = dev
                best_k = k

            rem_dev += brightness

        best_idxs_list.append(idxs[best_k:])

    return best_idxs_list


def _color2id(color: _Color) -> int:
    r, g, b = color
    r = round(r / 255 * 15)
    g = round(g / 255 * 15)
    b = round(b / 255 * 15)
    return 256 * r + 16 * g + b


def _get_colored_char(
    sub_arr: NDArray, layers: int, layer_idx: int
) -> tuple[int, str]:
    colors: NDArray = sub_arr.reshape(-1, 3)
    idxs: NDArray = _get_best_idxs_list(colors, layers)[layer_idx]
    avg_color: NDArray = colors[idxs].mean(0)
    value: int = 0x2800
    for idx in idxs:
        value |= _DOT_POSITIONS[idx]

    return _color2id(avg_color), chr(value)


# pylint: disable-next=R0913, R0914, R0917
def _convert_img_to_ascii(
    palette: dict[int, int],
    img: Image.Image,
    portrait: bool,
    rows: int,
    layers: int,
    layer_idx: int
) -> tuple[int, str]:
    if portrait:
        cols: int = round(rows / CHAR_ASPECT_RATIO)
        rows = round(cols * CHAR_ASPECT_RATIO * img.width / img.height)
        img = img.rotate(90, expand=True)
    else:
        cols = round(rows / CHAR_ASPECT_RATIO * img.width / img.height)

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
            color_id, char = _get_colored_char(sub_arr, layers, layer_idx)
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
    portrait: bool,
    rows: int,
    layers: int,
    layer_idx: int
) -> dict[str, Any]:
    start: float = 1000 * frame_num / fps + submsoffset
    duration: float = 1000 / fps
    frame: Image.Image = _blend_frames(frames)
    palette_id, ascii_img = _convert_img_to_ascii(
        palette, frame, portrait, rows, layers, layer_idx
    )
    return {
        "start": start,
        "duration": duration,
        "palette_id": palette_id,
        "ascii_img": ascii_img
    }


# pylint: disable-next=R0913, R0917
def convert_to_subtitles(
    frames_list: list[list[Image.Image]],
    fps: float,
    submsoffset: int,
    portrait: bool,
    rows: int,
    layers: int
) -> tuple[list[str], dict[int, int]]:
    """Convert video frames list to SRV3 subtitles with ASCII art."""
    print('Generating ASCII art...')
    palette: dict[int, int] = {}
    subtitles: list[str] = []
    iteration: int = 0
    for layer_idx in range(layers)[::-1]:
        entries: list[dict[str, Any]] = []
        for idx, frames in enumerate(frames_list):
            entry: dict[str, Any] = _convert_to_subtitle_entry(
                palette, frames, idx, fps, submsoffset, portrait, rows, layers,
                layer_idx
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
