"""Link Dynamic 3D Gaussians images and masks into per-frame folders."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from .camera_meta import ParsedCameraMeta


def link_file(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise FileNotFoundError(f"Missing source file: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    os.link(src, dst)


def link_frames(
    folder: Path,
    frame_pattern: Path,
    cameras: Sequence[ParsedCameraMeta],
    frame_indices: Sequence[int],
    output_numbers: Sequence[int],
    image_dirname: str = "images",
    mask_dirname: str = "image_masks",
) -> None:
    folder = Path(folder)
    frame_pattern = str(frame_pattern)
    for frame_index, output_number in zip(frame_indices, output_numbers):
        frame_dir = Path(frame_pattern % output_number)
        image_dir = frame_dir / image_dirname
        mask_dir = frame_dir / mask_dirname
        for camera in cameras:
            filename = camera.filenames[frame_index]
            link_file(folder / "ims" / filename, image_dir / camera.camera.name)
            mask_src = folder / "seg" / Path(filename).with_suffix(".png")
            if mask_src.is_file():
                link_file(mask_src, mask_dir / f"{camera.camera.name}.png")
