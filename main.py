"""Convert mp4 to srt subtitles using ASCII art."""
from __future__ import annotations

__all__: list[str] = []

import sys
from argparse import ArgumentParser, Namespace
from os import makedirs
from os.path import exists

from convert_to_ascii import convert_to_ascii
from convert_to_png import convert_to_png, print_progress_bar

_OUTPUT_PATH: str = "output/subtitles.srt"


def _parse_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        description="Convert mp4 to srt subtitles using ASCII art."
    )
    parser.add_argument(
        '--msoffset', type=int, default=0, help="Milliseconds offset."
    )
    parser.add_argument(
        '--submsoffset', type=int, default=0, help="Sub-milliseconds offset."
    )
    parser.add_argument('--idoffset', type=int, default=0, help="ID offset.")
    parser.add_argument('file', help="Path to the mp4 file.")
    parser.add_argument('collums', type=int, help="Number of ASCII columns.")
    return parser.parse_args()


def _main() -> None:
    args: Namespace = _parse_args()
    if not exists(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)

    frames, ms_per_frame = convert_to_png(
        args.file, args.msoffset, args.idoffset
    )
    srt: list[str] = []
    print('Generating ASCII art...')
    for idx, frame in enumerate(frames):
        print_progress_bar(idx + 1, len(frames))
        srt.append(convert_to_ascii(
            frame, idx, ms_per_frame, args.collums, args.submsoffset
        ))

    print()
    makedirs("output", exist_ok=True)
    with open(_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(srt))

    print(f"Subtitles written to {_OUTPUT_PATH}")


if __name__ == "__main__":
    _main()
