"""Link scene point clouds into per-frame COLMAP points3D.ply files."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .link_frames import link_file


def link_point_clouds(
    folder: Path,
    output_pattern: Path,
    output_numbers: Sequence[int],
) -> None:
    source = Path(folder) / "pcds" / "000000.ply"
    if not source.is_file():
        return
    output_pattern = str(output_pattern)
    for output_number in output_numbers:
        link_file(source, Path(output_pattern % output_number))
