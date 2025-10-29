"""Convert mp4 to srv3 subtitles using ASCII art."""
from __future__ import annotations

__all__: list[str] = []

from argparse import ArgumentParser, Namespace
from math import sqrt
from os import makedirs
from os.path import exists

from convert_to_frames import convert_to_frames
from convert_to_meta_subtitles import convert_to_meta_subtitles
from convert_to_subtitles import convert_to_subtitles

_OUTPUT_DIR: str = "output"


def _parse_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        description="Convert mp4 to srv3 subtitles using ASCII art."
    )
    parser.add_argument('file', help="Input mp4/png file.")
    parser.add_argument('--subfile', help="Input srt file.")
    parser.add_argument(
        '--msoffset',
        type=int,
        default=0,
        help="Millisecond offset of input files."
    )
    parser.add_argument(
        '--submsoffset',
        type=int,
        default=0,
        help="Millisecond offset of output file."
    )
    parser.add_argument(
        '--rows', default=12, type=int, help="Number of characters per column."
    )
    parser.add_argument(
        '--layers', type=int, default=1, help="Number of stacked frames."
    )
    parser.add_argument(
        '--targetsize', type=float, default=12, help="Target size in MB."
    )
    return parser.parse_args()


def _get_text_styles(rows: int, palette: dict[int, int]) -> list[str]:
    return [
        f'<pen id={palette_id} bo=0 of={2 if rows > 30 else 1} '
        f'fc="#{color_id:03x}" ec="#{color_id:03x}">'
        for color_id, palette_id in palette.items()
    ]


def _main() -> None:
    args: Namespace = _parse_args()
    if not exists(args.file):
        raise SystemExit(f"File not found: {args.file}")

    frames_list, fps = convert_to_frames(
        args.file, args.msoffset, args.rows, args.layers, args.targetsize
    )
    if args.subfile is None:
        meta_subtitles: list[str] = []
    else:
        meta_subtitles = convert_to_meta_subtitles(
            args.subfile, fps, args.submsoffset
        )

    subtitles, palette = convert_to_subtitles(
        frames_list, fps, args.submsoffset, args.rows, args.layers
    )
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

    makedirs(_OUTPUT_DIR, exist_ok=True)
    output_filename: str = (
        f"{_OUTPUT_DIR}/"
        + f"{args.rows * (sqrt(args.layers) if len(palette) > 16 else 4):.0f}p"
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
            '<body>', *subtitles, *meta_subtitles, '</body>',
            '</timedtext>',
        ]))

    print(f"Subtitles written to {output_filename}")


if __name__ == "__main__":
    _main()
