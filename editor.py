"""Batch video editing utilities using ffmpeg-python.

This module provides simple functions for trimming, rotating and changing
playback speed of videos. It processes all videos within a directory and
stores sidecar metadata describing the operations performed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

import ffmpeg


def _apply_basic_filters(stream, start: Optional[float], end: Optional[float],
                         rotate: Optional[int], speed: Optional[float]):
    if start is not None or end is not None:
        stream = stream.trim(start=start or 0, end=end).setpts("PTS-STARTPTS")
    if rotate:
        if rotate == 90:
            stream = stream.transpose(1)
        elif rotate == 180:
            stream = stream.hflip().vflip()
        elif rotate == 270:
            stream = stream.transpose(2)
    if speed and speed > 0:
        stream = stream.filter("setpts", f"{1/speed}*PTS")
    return stream


def process_videos(
    source_dir: str,
    output_dir: str,
    start: Optional[float] = None,
    end: Optional[float] = None,
    rotate: Optional[int] = None,
    speed: Optional[float] = None,
):
    """Process every video under ``source_dir`` recursively.

    Parameters
    ----------
    source_dir: str
        Directory containing input videos.
    output_dir: str
        Directory where processed videos and metadata will be written.
    start, end: float
        Optional start and end times in seconds for trimming.
    rotate: int
        Rotation angle in degrees (90, 180, 270).
    speed: float
        Playback speed multiplier.
    """

    src = Path(source_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for path in src.rglob("*.mp4"):
        input_stream = ffmpeg.input(str(path))
        filtered = _apply_basic_filters(input_stream, start, end, rotate, speed)
        out_path = out / f"{path.stem}_edited.mp4"
        ffmpeg.output(filtered, str(out_path)).overwrite_output().run()

        meta = {
            "source": str(path),
            "output": str(out_path),
            "start": start,
            "end": end,
            "rotate": rotate,
            "speed": speed,
        }
        meta_path = out_path.with_suffix(out_path.suffix + ".json")
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

        yield out_path
