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


def first_frame_number(folder: Path) -> int:
    numbers = []
    for path in Path(folder).iterdir():
        if path.is_dir() and path.name.startswith("frame") and path.name[5:].isdigit():
            numbers.append(int(path.name[5:]))
    if not numbers:
        raise FileNotFoundError(f"No frame directories found in {folder}")
    return min(numbers)


def select_frame_indices(
    frame_indices: Sequence[int],
    start_number: int | None,
    n_frames: int | None,
) -> list[int]:
    available = list(frame_indices)
    if not available:
        raise ValueError("No frames available.")
    if start_number is None:
        start_number = min(available) + 1
    elif start_number < 1:
        raise ValueError("--start-number is 1-based and must be at least 1.")
    start_index = start_number - 1
    if start_index not in available:
        raise FileNotFoundError(
            "Source frame "
            f"{start_index:06d} is not in this scene. Frames on disk run from "
            f"{min(available):06d} to {max(available):06d}; "
            f"pass --start-number {min(available) + 1} to begin at the first frame."
        )
    if n_frames is None:
        n_frames = max(available) - start_index + 1
    if n_frames < 1:
        raise ValueError("--n-frames must be at least 1.")
    selected = list(range(start_index, start_index + n_frames))
    missing = [index for index in selected if index not in available]
    if missing:
        raise FileNotFoundError(
            f"Missing source frame {missing[0]:06d}. Frames on disk run from "
            f"{min(available):06d} to {max(available):06d}."
        )
    return selected


def link_file(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise FileNotFoundError(f"Missing source file: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    os.link(src, dst)


def mask_path(folder: Path, camera: ParsedCamera, frame_index: int) -> Path | None:
    image_path = camera.frames[frame_index]
    candidate = folder / "masks" / camera.view / f"{image_path.stem}.png"
    if candidate.is_file():
        return candidate
    return None


def link_frames(
    folder: Path,
    frame_pattern: Path,
    cameras: Sequence[ParsedCamera],
    frame_indices: Sequence[int],
    image_dirname: str = "images",
    mask_dirname: str = "image_masks",
) -> None:
    folder = Path(folder)
    frame_pattern = str(frame_pattern)
    distorted = any(camera.dist is not None for camera in cameras)
    for frame_index in frame_indices:
        frame_dir = Path(frame_pattern % (frame_index + 1))
        image_dir = frame_dir / image_dirname
        mask_dir = frame_dir / mask_dirname
        for camera in cameras:
            image_src = camera.frames[frame_index]
            image_name = camera.camera.name
            if distorted:
                link_file(image_src, frame_dir / "input" / image_name)
            else:
                link_file(image_src, image_dir / image_name)
            mask_src = mask_path(folder, camera, frame_index)
            if mask_src is None:
                continue
            mask_name = f"{image_name}.png"
            if distorted:
                link_file(mask_src, frame_dir / "input_mask" / mask_name)
            else:
                link_file(mask_src, mask_dir / mask_name)
