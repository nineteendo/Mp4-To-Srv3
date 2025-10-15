"""Convert mp4 to srv3 subtitles using ASCII art."""
from __future__ import annotations

__all__: list[str] = []

import sys
from argparse import ArgumentParser, Namespace
from math import ceil, floor
from os import makedirs
from os.path import exists
from typing import Any

from pysrt import SubRipFile  # type: ignore

from convert_to_ascii import convert_to_ascii
from convert_to_frames import convert_to_frames, print_progress_bar
from split_subtitle import split_subtitle

_OUTPUT_DIR: str = "output"


def _parse_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        description="Convert mp4 to srv3 subtitles using ASCII art."
    )
    parser.add_argument(
        '--msoffset', type=int, default=0, help="Milliseconds offset."
    )
    parser.add_argument('--subfile', help="Path to the subtitle file.")
    parser.add_argument(
        '--submsoffset', type=int, default=0, help="Sub-milliseconds offset."
    )

    parser.add_argument('file', help="Path to the mp4 file.")
    parser.add_argument('rows', type=int, help="Number of ASCII rows.")
    return parser.parse_args()


def _get_text_styles(rows: int, palette: dict[int, int]) -> list[str]:
    return [
        f'<pen id={palette_id} bo=0 of={2 if rows > 30 else 1} '
        f'fc="#{color_id:03x}" ec="#{color_id:03x}">'
        for color_id, palette_id in palette.items()
    ]


def _get_subtitles(entries: list[dict[str, Any]]) -> list[str]:
    return [
        f"<p t={ceil(entry['start'])} d={floor(entry['duration'])} "
        f"wp=0 ws=0 p={entry['palette_id']}>{entry['ascii_img']}</p>"
        for entry in entries
    ]


def _main() -> None:
    args: Namespace = _parse_args()
    if not exists(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)

    frames_list, fps = convert_to_frames(args.file, args.msoffset, args.rows)
    meta_subtitles: list[str] = []
    if args.subfile is not None:
        with open(args.subfile, "r", encoding="utf-8") as fp:
            for sub in SubRipFile.stream(fp):
                meta_subtitles.extend(
                    split_subtitle(sub, fps, args.submsoffset)
                )

    entries: list[dict[str, Any]] = []
    palette: dict[int, int] = {}
    print('Generating ASCII art...')
    for idx, frames in enumerate(frames_list):
        print_progress_bar(idx + 1, len(frames_list))
        entry: dict[str, Any] = convert_to_ascii(
            palette, frames, idx, fps, args.rows, args.submsoffset
        )
        if (
            entries
            and entry['palette_id'] == entries[-1]['palette_id']
            and entry['ascii_img'] == entries[-1]['ascii_img']
        ):
            entries[-1]['duration'] += entry['duration']
        else:
            entries.append(entry)

    if portrait := args.rows > 48:
        window_style: str = '<ws id=0 pd=3 sd=0>'
        window_positions: list[str] = [
            '<wp id=0 ap=4 ah=50 av=50>',
            '<wp id=1 ap=5 ah=100 av=50>'
        ]
    else:
        window_style = '<ws id=0 pd=0 sd=0>'
        window_positions = [
            '<wp id=0 ap=4 ah=50 av=50>',
            '<wp id=1 ap=7 ah=50 av=100>'
        ]

    print()
    makedirs(_OUTPUT_DIR, exist_ok=True)
    output_filename: str = (
        f"{_OUTPUT_DIR}/"
        + f"{4 * args.rows}p"
        + (f"{fps:.2g}" if round(fps) != 30 else "")
        + (" (portrait)" if portrait else "")
        + ".srv3"
    )
    with open(output_filename, "w", encoding="utf-8") as fp:
        fp.write("\n".join([
            '<timedtext format="3">',
            '<head>',
            *_get_text_styles(args.rows, palette),
            window_style,
            *window_positions,
            '</head>',
            '<body>', *_get_subtitles(entries), *meta_subtitles, '</body>',
            '</timedtext>',
        ]))

    print(f"Subtitles written to {output_filename}")


if __name__ == "__main__":
    _main()
