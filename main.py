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

_OUTPUT_PATH: str = "output/subtitles.srv3"


def _parse_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        description="Convert mp4 to srv3 subtitles using ASCII art."
    )
    parser.add_argument(
        '--msoffset', type=int, default=0, help="Milliseconds offset."
    )
    parser.add_argument(
        '--submsoffset', type=int, default=0, help="Sub-milliseconds offset."
    )

    parser.add_argument('file', help="Path to the mp4 file.")
    parser.add_argument('subfile', help="Path to the subtitle file.")
    parser.add_argument('rows', type=int, help="Number of ASCII rows.")
    return parser.parse_args()


def _main() -> None:
    args: Namespace = _parse_args()
    if not exists(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)

    frames, fps = convert_to_frames(args.file, args.msoffset, args.rows)
    entries: list[dict[str, Any]] = []
    palette: dict[int, int] = {}
    print('Generating ASCII art...')
    for idx, frame in enumerate(frames):
        print_progress_bar(idx + 1, len(frames))
        entry: dict[str, Any] = convert_to_ascii(
            palette, frame, idx, fps, args.rows, args.submsoffset
        )
        if (
            entries
            and entry['palette_id'] == entries[-1]['palette_id']
            and entry['ascii_img'] == entries[-1]['ascii_img']
        ):
            entries[-1]['duration'] += entry['duration']
        else:
            entries.append(entry)

    meta_subtitles: list[str] = []
    with open(args.subfile, "r", encoding="utf-8") as f:
        for sub in SubRipFile.stream(f):
            meta_subtitles.extend(split_subtitle(sub, fps, args.submsoffset))

    print()
    makedirs("output", exist_ok=True)
    with open(_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write('<timedtext format="3">\n')
        f.write('<head>\n')
        for color_id, palette_id in palette.items():
            offset: int = 2 if args.rows > 30 else 1
            f.write(
                f'<pen id={palette_id} bo=0 et=1 of={offset} '
                f'fc="#{color_id:03x}" ec="#{color_id:03x}">\n'
            )

        if args.rows > 48:
            f.write('<ws id=0 pd=3 sd=0>\n')
        else:
            f.write('<ws id=0>\n')

        f.write('<wp id=0 ap=4 ah=50 av=50>\n')
        f.write('</head>\n')
        f.write('<body>\n')
        for entry in entries:
            f.write(
                f"<p t={ceil(entry['start'])} d={floor(entry['duration'])} "
                f"wp=0 ws=0 p={entry['palette_id']}>{entry['ascii_img']}</p>\n"
            )

        f.writelines(meta_subtitles)
        f.write('</body>\n')
        f.write('</timedtext>')

    print(f"Subtitles written to {_OUTPUT_PATH}")


if __name__ == "__main__":
    _main()
