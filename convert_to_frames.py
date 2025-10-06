"""Convert a video to images."""
from __future__ import annotations

__all__: list[str] = [
    "CHAR_ASPECT_RATIO", "convert_to_frames", "print_progress_bar"
]

from math import ceil, floor

# pylint: disable-next=E0611
from cv2 import (
    CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, CAP_PROP_POS_MSEC,
    COLOR_BGR2RGB, VideoCapture, cvtColor
)
from PIL import Image

_TARGET_SIZE: float = 1.4 * 9 * 1024 * 1024

CHAR_ASPECT_RATIO: float = 35 / 58


def print_progress_bar(iteration: int, total: int) -> None:
    """Prints an in-place progress bar."""
    percentage: float = 100 * iteration / total
    progress: str = f"Progress: {iteration}/{total} - {percentage:.1f}%"
    print(progress, end='\r', flush=True)


# pylint: disable-next=R0914
def convert_to_frames(
    vidfile: str, startms: int, rows: int
) -> tuple[list[Image.Image], float]:
    """
    Extract frames from an mp4 file starting at a given offset.
    Returns a list of PIL Images and ms per frame.
    """
    frames: list[Image.Image] = []
    cam: VideoCapture = VideoCapture(vidfile)
    fps: float = cam.get(CAP_PROP_FPS)

    cam.set(CAP_PROP_POS_MSEC, startms)
    pos_after_offset: int = int(cam.get(CAP_PROP_POS_FRAMES))
    total_frames: int = max(
        1, int(cam.get(CAP_PROP_FRAME_COUNT) - pos_after_offset)
    )

    print('Extracting Frames...')
    frame_num: int = int(cam.get(CAP_PROP_POS_FRAMES)) - pos_after_offset
    print_progress_bar(frame_num, total_frames)
    ret, frame = cam.read()
    img: Image.Image = Image.fromarray(cvtColor(frame, COLOR_BGR2RGB))

    cols: int = round(rows / CHAR_ASPECT_RATIO * img.width / img.height)
    step: int = ceil(total_frames * (
        len(
            f"<p t={ceil(1000 * (total_frames - 1) / fps)} "
            f"d={floor(1000 / fps)} wp=0 ws=0>"
        )
        + rows * len((cols * "<s p=4095>\u28ff" + "\n").encode())
        + len("</p>\n")
    ) / _TARGET_SIZE)

    while ret:
        if not frame_num % step:
            frames.append(Image.fromarray(cvtColor(frame, COLOR_BGR2RGB)))

        frame_num = int(cam.get(CAP_PROP_POS_FRAMES)) - pos_after_offset
        print_progress_bar(frame_num, total_frames)
        ret, frame = cam.read()

    print()
    cam.release()
    if total_frames > 1:
        return frames, fps / step

    return frames, 1 / 5
