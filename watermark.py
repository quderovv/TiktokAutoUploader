"""Watermark overlay utilities using ffmpeg-python."""

from pathlib import Path
from typing import Tuple

import ffmpeg


def apply_watermark(
    video_path: str,
    image_path: str,
    output_path: str,
    position: Tuple[int, int] = (0, 0),
    scale: float = 1.0,
) -> str:
    """Apply a watermark image over ``video_path``.

    Parameters
    ----------
    video_path: str
        Input video file.
    image_path: str
        Watermark image path.
    output_path: str
        Where to write the resulting video.
    position: Tuple[int, int]
        X/Y coordinates for the watermark.
    scale: float
        Scaling factor for the watermark image.
    """

    video = ffmpeg.input(video_path)
    wm = ffmpeg.input(image_path)
    if scale != 1.0:
        wm = wm.filter("scale", f"iw*{scale}", f"ih*{scale}")
    overlaid = ffmpeg.overlay(video, wm, x=position[0], y=position[1])
    ffmpeg.output(overlaid, output_path).overwrite_output().run()
    return output_path
