"""Convert a video to images."""
from __future__ import annotations

__all__: list[str] = ["convert_to_frames", "print_progress_bar"]

from math import ceil, floor, inf

# pylint: disable-next=E0611
from cv2 import (
    CAP_PROP_FPS, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, CAP_PROP_POS_MSEC,
    COLOR_BGR2RGB, VideoCapture, cvtColor
)
from PIL import Image

_CHAR_ARS: dict[float, dict[str, float]] = {
    4 / 3: {"narrow": 14 / 23},
    16 / 9: {"standard": 14 / 23, "portrait": 20 / 33},
    64 / 27: {"wide": 7 / 12}
}
_CHAR_AR_LARGE_TEXT: dict[str, float] = {
    "standard": 32 / 53, "portrait": 34 / 57
}
_THRESHOLDS: dict[float, dict[str, int]] = {
    4 / 3: {"landscape": 63, "large_text": 33, "standard": 49},
    16 / 9: {"landscape": 47, "large_text": 33, "large_text_portrait": 58},
    64 / 27: {"landscape": 45, "large_text": 25, "standard": 35}
}


def _calculate_settings(
    width: int, height: int, rows: int
) -> tuple[str, str, float]:
    min_ar: float = (width - 0.5) / (height + 0.5)
    max_ar: float = (width + 0.5) / (height - 0.5)
    for ar, threshold in _THRESHOLDS.items():
        if min_ar <= ar <= max_ar:
            break
    else:
        raise SystemExit(f"Unknown aspect ratio: {min_ar} <= ar <= {max_ar}")

    if rows <= threshold["landscape"]:
        large_text_threshold: float = threshold["large_text"]
        if rows <= threshold.get("standard", inf) or ar == 16 / 9:
            ar = 16 / 9
            display_mode: str = "standard"
        else:
            display_mode = "narrow" if ar < 16 / 9 else "wide"
    else:
        large_text_threshold = threshold.get("large_text_portrait", -inf)
        ar = 16 / 9
        display_mode = "portrait"

    if rows <= large_text_threshold:
        char_ar: float = _CHAR_AR_LARGE_TEXT[display_mode]
        font_size: str = "default"
    else:
        char_ar = _CHAR_ARS[ar][display_mode]
        font_size = "small"

    return display_mode, font_size, char_ar


def print_progress_bar(iteration: int, total: int) -> None:
    """Print an in-place progress bar."""
    percentage: float = 100 * iteration / total
    progress: str = f"Progress: {iteration}/{total} - {percentage:.1f}%"
    print(progress, end='\r', flush=True)


# pylint: disable-next=R0914
def convert_to_frames(
    file: str, startms: int, rows: int, layers: int, targetsize: int
) -> tuple[list[list[Image.Image]], float, str, str, float]:
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

    display_mode, font_size, char_ar = _calculate_settings(
        img.width, img.height, rows
    )
    if display_mode == "portrait":
        cols: int = round(rows / char_ar)
        rows = round(cols * char_ar * img.width / img.height)
    else:
        cols = round(rows / char_ar * img.width / img.height)

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
        return frames_list, fps / step, display_mode, font_size, char_ar

    return frames_list, 1 / 5, display_mode, font_size, char_ar
