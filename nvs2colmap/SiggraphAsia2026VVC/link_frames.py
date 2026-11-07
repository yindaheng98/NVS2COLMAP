"""Link Siggraph Asia volumetric-video images and masks into per-frame folders."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from .cameras import ParsedCamera


def link_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    os.link(src, dst)


def link_frames(
    folder: Path,
    frame_pattern: Path,
    cameras: Sequence[ParsedCamera],
    frame_indices: Sequence[int],
    output_numbers: Sequence[int],
    image_dirname: str = "images",
    mask_dirname: str = "image_masks",
) -> None:
    folder = Path(folder)
    frame_pattern = str(frame_pattern)
    for frame_index, output_number in zip(frame_indices, output_numbers):
        frame_dir = Path(frame_pattern % output_number)
        for camera in cameras:
            image_src = camera.frames[frame_index]
            link_file(image_src, frame_dir / image_dirname / camera.camera.name)
            mask_src = folder / "masks" / camera.view / f"{image_src.stem}.png"
            if mask_src.is_file():
                link_file(mask_src, frame_dir / mask_dirname / f"{camera.camera.name}.png")
