"""Check ST-NeRF frame images and link them into COLMAP input folders."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from nvs2colmap.write_model import CameraModel


def count_frame_dirs(output_pattern: Path, start_number: int = 1) -> int:
    output_pattern = str(output_pattern)
    frame = start_number
    while Path(output_pattern % frame).is_dir():
        frame += 1
    n_frames = frame - start_number
    if n_frames == 0:
        raise FileNotFoundError(f"No frame directories found from pattern: {output_pattern}")
    return n_frames


def link_file(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise FileNotFoundError(f"Missing source file: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    os.link(src, dst)


def prepare_frames(
    folder: Path,
    cameras: Sequence[CameraModel],
    n_frames: int,
    start_number: int = 1,
    link_to_input: bool = False,
) -> None:
    folder = Path(folder)
    for frame in range(start_number, start_number + n_frames):
        image_dir = folder / f"frame{frame}" / "images"
        if not image_dir.is_dir():
            raise FileNotFoundError(f"Missing frame directory: {folder / f'frame{frame}'}")
        for camera in cameras:
            src = image_dir / camera.name
            if not src.is_file():
                raise FileNotFoundError(f"Missing source image: {src}")
            if link_to_input:
                link_file(src, folder / f"frame{frame}" / "input" / camera.name)
