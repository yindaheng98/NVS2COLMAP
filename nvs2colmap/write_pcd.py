"""Write xyz/rgb point clouds as PLY files."""

from pathlib import Path

import numpy as np
from plyfile import PlyData, PlyElement


def write_pcd(path, points, colors) -> None:
    """Write a point cloud in the InstantSplat ``points3D.ply`` layout.

    ``points`` and ``colors`` are ``(N, 3)`` arrays. Colors are already 8-bit
    RGB values in ``[0, 255]``.
    """
    xyz = np.asarray(points)
    rgb = np.asarray(colors)
    dtype = [
        ("x", "f4"),
        ("y", "f4"),
        ("z", "f4"),
        ("nx", "f4"),
        ("ny", "f4"),
        ("nz", "f4"),
        ("red", "u1"),
        ("green", "u1"),
        ("blue", "u1"),
    ]
    normals = np.zeros_like(xyz)
    elements = np.empty(xyz.shape[0], dtype=dtype)
    attributes = np.concatenate((xyz, normals, rgb), axis=1)
    elements[:] = list(map(tuple, attributes))

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    PlyData([PlyElement.describe(elements, "vertex")]).write(path)
