"""Convert mp4 to srt subtitles using ASCII art."""
from __future__ import annotations

__all__: list[str] = []

import sys
from argparse import ArgumentParser, Namespace
from os import makedirs
from os.path import exists

from convert_to_ascii import convert_to_ascii
from convert_to_frames import convert_to_frames, print_progress_bar

_MAX_SIZE: int = 5 * 1024 * 1024
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
    parser.add_argument('rows', type=int, help="Number of ASCII rows.")
    return parser.parse_args()


def _main() -> None:
    args: Namespace = _parse_args()
    if not exists(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)

    frames, ms_per_frame = convert_to_frames(
        args.file, args.msoffset, args.idoffset
    )
    srt: list[bytes] = []
    total_size: int = -1
    print('Generating ASCII art...')
    for idx, frame in enumerate(frames):
        print_progress_bar(idx + 1, len(frames))
        entry: bytes = convert_to_ascii(
            frame, idx, ms_per_frame, args.rows, args.submsoffset
        ).encode()
        entry_size: int = len(entry) + 1
        if total_size + entry_size > _MAX_SIZE:
            print(f"Reached 5 MB limit at frame {idx}")
            print(end="Stopping subtitle generation.")
            break

        srt.append(entry)
        total_size += entry_size

    print()
    makedirs("output", exist_ok=True)
    with open(_OUTPUT_PATH, "wb") as f:
        f.write(b"\n".join(srt))

    print(f"Subtitles written to {_OUTPUT_PATH}")


if __name__ == "__main__":
    _main()
