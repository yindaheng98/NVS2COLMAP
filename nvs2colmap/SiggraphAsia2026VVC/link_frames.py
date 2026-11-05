"""Link Siggraph Asia volumetric-video images and masks into per-frame folders."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from .cameras import ParsedCamera


def count_frame_dirs(output_pattern: Path, start_number: int = 1) -> int:
    output_pattern = str(output_pattern)
    frame = start_number
    while Path(output_pattern % frame).is_dir():
        frame += 1
    n_frames = frame - start_number
    if n_frames == 0:
        raise FileNotFoundError(f"No frame directories found from pattern: {output_pattern}")
    return n_frames


def select_frame_indices(
    frame_indices: Sequence[int],
    start_number: int,
    n_frames: int | None,
) -> list[int]:
    available = sorted(frame_indices)
    if start_number > len(available):
        raise FileNotFoundError(
            f"--start-number {start_number} is past the {len(available)} frames on disk "
            f"({available[0]:06d} through {available[-1]:06d})."
        )
    selected = available[start_number - 1 :]
    if n_frames is not None:
        if n_frames > len(selected):
            raise FileNotFoundError(
                f"--n-frames {n_frames} runs past the {len(selected)} frames "
                f"left from frame {start_number}."
            )
        selected = selected[:n_frames]
    return selected


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
