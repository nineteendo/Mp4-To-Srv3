"""Convert a video to images."""
from __future__ import annotations

__all__: list[str] = ["convert_to_png", "print_progress_bar"]

# pylint: disable-next=E0611
from cv2 import (
    CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, CAP_PROP_POS_MSEC,
    COLOR_BGR2RGB, VideoCapture, cvtColor
)
from PIL import Image


def print_progress_bar(iteration: int, total: int) -> None:
    """Prints an in-place progress bar."""
    percent: str = f"{100 * (iteration / float(total)):.1f}"
    progress: str = f"Progress: {iteration}/{total} - {percent}%"
    print(progress, end='\r', flush=True)


def convert_to_png(
    vidfile: str, startms: int, idoffset: int
) -> tuple[list[Image.Image], float]:
    """
    Extract frames from an mp4 file starting at a given offset.
    Returns a list of PIL Images and ms per frame.
    """
    frames: list[Image.Image] = []
    cam: VideoCapture = VideoCapture(vidfile)
    fps: float = cam.get(CAP_PROP_FPS)
    ms_per_frame: float = 1000 / fps

    cam.set(CAP_PROP_POS_MSEC, startms + idoffset * ms_per_frame)
    pos_after_offset: int = int(cam.get(CAP_PROP_POS_FRAMES))
    total_frames: int = int(cam.get(CAP_PROP_FRAME_COUNT)) - pos_after_offset

    print('Extracting Frames...')
    while True:
        frame_num: int = int(cam.get(CAP_PROP_POS_FRAMES)) - pos_after_offset
        print_progress_bar(frame_num, total_frames)
        ret, frame = cam.read()
        if not ret:
            break

        frames.append(Image.fromarray(cvtColor(frame, COLOR_BGR2RGB)))

    print()
    cam.release()
    return frames, ms_per_frame
