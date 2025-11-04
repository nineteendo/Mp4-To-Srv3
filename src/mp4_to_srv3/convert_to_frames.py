"""Convert a video to images."""
from __future__ import annotations

__all__: list[str] = [
    "CHAR_ASPECT_RATIO", "convert_to_frames", "print_progress_bar"
]

from math import ceil, floor, inf

# pylint: disable-next=E0611
from cv2 import (
    CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, CAP_PROP_POS_MSEC,
    COLOR_BGR2RGB, VideoCapture, cvtColor
)
from PIL import Image

_THRESHOLDS: dict[float, dict[str, int]] = {
    4 / 3:   {"landscape": 63, "large_text": 33, "standard": 48},
    16 / 9:  {"landscape": 46, "large_text": 33, "large_text_portrait": 58},
    64 / 27: {"landscape": 46, "large_text": 25, "standard": 35}
}
CHAR_ASPECT_RATIO: float = 35 / 58


def print_progress_bar(iteration: int, total: int) -> None:
    """Print an in-place progress bar."""
    percentage: float = 100 * iteration / total
    progress: str = f"Progress: {iteration}/{total} - {percentage:.1f}%"
    print(progress, end='\r', flush=True)


# pylint: disable-next=R0913, R0914, R0917
def convert_to_frames(
    file: str, startms: int, rows: int, layers: int, targetsize: int
) -> tuple[list[list[Image.Image]], float, str, str]:
    """Extract frames list from an mp4 file."""
    frames_list: list[list[Image.Image]] = []
    cam: VideoCapture = VideoCapture(file)
    fps: float = cam.get(CAP_PROP_FPS)

    cam.set(CAP_PROP_POS_MSEC, startms)
    pos_after_offset: int = int(cam.get(CAP_PROP_POS_FRAMES))
    total_frames: int = max(
        1, int(cam.get(CAP_PROP_FRAME_COUNT) - pos_after_offset)
    )

    print('Extracting Frames...')
    ret, frame = cam.read()
    img: Image.Image = Image.fromarray(cvtColor(frame, COLOR_BGR2RGB))

    min_ar: float = (img.width - 0.5) / (img.height + 0.5)
    max_ar: float = (img.width + 0.5) / (img.height - 0.5)
    for ar, threshold in _THRESHOLDS.items():
        if min_ar <= ar <= max_ar:
            if rows <= threshold["landscape"]:
                if rows <= threshold.get("standard", inf) or ar == 16 / 9:
                    display_mode: str = "standard"
                else:
                    display_mode = "narrow" if ar < 16 / 9 else "wide"

                large_text_threshold: float = threshold["large_text"]
            else:
                display_mode = "portrait"
                large_text_threshold = threshold.get(
                    "large_text_portrait", -inf
                )

            break
    else:
        raise SystemExit(f"Unknown aspect ratio: {min_ar} <= ar <= {max_ar}")

    font_size: str = "default" if rows <= large_text_threshold else "small"
    if display_mode == "portrait":
        cols: int = round(rows / CHAR_ASPECT_RATIO)
        rows = round(cols * CHAR_ASPECT_RATIO * img.width / img.height)
    else:
        cols = round(rows / CHAR_ASPECT_RATIO * img.width / img.height)

    step: int = ceil(total_frames * layers * (
        len(
            f"<p t={ceil(1000 * (total_frames - 1) / fps)} "
            f"d={floor(1000 / fps)} wp=0 ws=0>"
        )
        + rows * len((cols * "<s p=4095>\u28ff" + "\n").encode())
        + len("</p>\n")
    ) / (1024 * 1024 * targetsize))

    frames: list[Image.Image] = []
    while ret:
        frames.append(Image.fromarray(cvtColor(frame, COLOR_BGR2RGB)))
        frame_num: int = int(cam.get(CAP_PROP_POS_FRAMES)) - pos_after_offset
        if not frame_num % step:
            frames_list.append(frames)
            frames = []

        print_progress_bar(frame_num, total_frames)
        ret, frame = cam.read()

    print()
    cam.release()
    if total_frames > 1:
        return frames_list, fps / step, display_mode, font_size

    return frames_list, 1 / 5, display_mode, font_size
