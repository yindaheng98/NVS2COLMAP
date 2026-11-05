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
    available = sorted(frame_indices)
    if not available:
        raise ValueError("No frames available.")
    if start_number is None:
        start_number = 1
    elif start_number < 1:
        raise ValueError("--start-number is 1-based and must be at least 1.")
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
                f"that remain from --start-number {start_number}."
            )
        selected = selected[:n_frames]
    expected = list(range(selected[0], selected[-1] + 1))
    if selected != expected:
        missing = next(index for index in expected if index not in selected)
        raise FileNotFoundError(
            f"Missing source frame {missing:06d}. Frames on disk run from "
            f"{available[0]:06d} to {available[-1]:06d}."
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
    output_numbers: Sequence[int],
    image_dirname: str = "images",
    mask_dirname: str = "image_masks",
) -> None:
    folder = Path(folder)
    frame_pattern = str(frame_pattern)
    distorted = any(camera.dist is not None for camera in cameras)
    for frame_index, output_number in zip(frame_indices, output_numbers):
        frame_dir = Path(frame_pattern % output_number)
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
