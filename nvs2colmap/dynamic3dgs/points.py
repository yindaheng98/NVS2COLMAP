"""Write Dynamic 3D Gaussians init_pt_cld.npz as COLMAP points3D.ply."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from nvs2colmap.write_pcd import write_pcd

from .link_frames import link_file


def write_init_point_cloud(
    npz_path: Path,
    output_pattern: Path,
    n_frames: int,
    start_number: int = 1,
) -> None:
    data = np.load(npz_path)["data"]
    output_pattern = str(output_pattern)
    paths = [Path(output_pattern % frame) for frame in range(start_number, start_number + n_frames)]
    write_pcd(paths[0], data[:, :3], data[:, 3:6] * 255.0)
    for path in paths[1:]:
        link_file(paths[0], path)
