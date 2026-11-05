"""Link scene point clouds into per-frame COLMAP points3D.ply files."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .link_frames import link_file


def index_point_clouds(folder: Path) -> dict[int, Path]:
    pcds = Path(folder) / "pcds"
    if not pcds.is_dir():
        return {}
    found = {}
    for path in sorted(pcds.glob("*.ply")):
        if path.stem.isdigit():
            found[int(path.stem)] = path
    return found


def point_cloud_for_frame(point_clouds: dict[int, Path], frame_index: int) -> Path | None:
    if frame_index in point_clouds:
        return point_clouds[frame_index]
    if set(point_clouds) <= {0}:
        return point_clouds.get(0)
    return None


def link_point_clouds(
    folder: Path,
    output_pattern: Path,
    frame_indices: Sequence[int],
) -> None:
    point_clouds = index_point_clouds(folder)
    if not point_clouds:
        return
    output_pattern = str(output_pattern)
    for frame_index in frame_indices:
        source = point_cloud_for_frame(point_clouds, frame_index)
        if source is None:
            continue
        link_file(source, Path(output_pattern % (frame_index + 1)))
