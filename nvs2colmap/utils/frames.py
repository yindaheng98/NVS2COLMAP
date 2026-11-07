"""Choose which source frames to write."""

from __future__ import annotations

from typing import Sequence


def select_frame_indices(
    frame_indices: Sequence[int],
    start_number: int,
    n_frames: int | None,
    frame_skip: int = 1,
) -> list[int]:
    """Return source frame ids to write.

    ``start_number`` is the 1-based position in ``frame_indices`` after sorting.
    ``frame_skip`` keeps every Nth frame from there. ``n_frames`` is how many of
    those kept frames to write. A request past the frames that remain keeps
    those frames.
    """
    if frame_skip < 1:
        raise ValueError(f"frame_skip must be at least 1, got {frame_skip}.")
    available = sorted(frame_indices)
    if not available or start_number > len(available):
        span = (
            f" ({available[0]:06d} through {available[-1]:06d})"
            if available
            else ""
        )
        raise FileNotFoundError(
            f"--start-number {start_number} is past the {len(available)} available frames{span}."
        )
    selected = available[start_number - 1:: frame_skip]
    if n_frames is not None and n_frames > len(selected):
        print(
            f"--n-frames {n_frames} runs past the {len(selected)} frames "
            f"left from frame {start_number} with --frame-skip {frame_skip}; "
            f"writing {len(selected)}."
        )
    if n_frames is not None:
        selected = selected[:n_frames]
    return selected
