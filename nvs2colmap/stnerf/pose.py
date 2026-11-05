"""Read ST-NeRF pose/K.txt and pose/RT_c2w.txt into COLMAP cameras."""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
import torch

from nvs2colmap.utils import matrix_to_quaternion
from nvs2colmap.write_model import CameraModel


def read_png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Expected a PNG image: {path}")
        handle.read(4)
        if handle.read(4) != b"IHDR":
            raise ValueError(f"Invalid PNG header: {path}")
        width, height = struct.unpack(">II", handle.read(8))
    return int(width), int(height)


def read_matrix_rows(path: Path, width: int) -> np.ndarray:
    rows = []
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        values = [float(value) for value in line.split()]
        if len(values) != width:
            raise ValueError(f"{path} line {line_number} has {len(values)} values, expected {width}.")
        rows.append(values)
    if not rows:
        raise ValueError(f"No cameras found in {path}")
    return np.asarray(rows, dtype=np.float64)


def read_pose(folder: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return intrinsics (N, 3, 3) and camera-to-world matrices (N, 4, 4)."""
    pose_dir = Path(folder) / "pose"
    intrinsics_path = pose_dir / "K.txt"
    extrinsics_path = pose_dir / "RT_c2w.txt"
    if not intrinsics_path.is_file() or not extrinsics_path.is_file():
        raise FileNotFoundError(f"Missing pose files in {pose_dir}. Expected K.txt and RT_c2w.txt.")

    intrinsics = read_matrix_rows(intrinsics_path, 9).reshape(-1, 3, 3)
    extrinsics = read_matrix_rows(extrinsics_path, 12).reshape(-1, 3, 4)
    if len(intrinsics) != len(extrinsics):
        raise ValueError(
            f"{intrinsics_path.name} has {len(intrinsics)} cameras "
            f"but {extrinsics_path.name} has {len(extrinsics)}."
        )
    camera_to_world = np.tile(np.eye(4, dtype=np.float64), (len(extrinsics), 1, 1))
    camera_to_world[:, :3, :] = extrinsics
    return intrinsics, camera_to_world


def camera_image(folder: Path, frame: int, name: str) -> Path:
    for dirname in ("images", "input"):
        path = folder / f"frame{frame}" / dirname / name
        if path.is_file():
            return path
    raise FileNotFoundError(f"Missing {name} for frame {frame} in {folder}")


def read_cameras(folder: Path, start_number: int) -> list[CameraModel]:
    folder = Path(folder)
    intrinsics, camera_to_world = read_pose(folder)
    cameras = []
    for index, (intrinsic, pose) in enumerate(zip(intrinsics, camera_to_world)):
        name = f"{index}.png"
        width, height = read_png_size(camera_image(folder, start_number, name))
        world_to_camera = np.linalg.inv(pose)
        quaternion = matrix_to_quaternion(torch.tensor(world_to_camera[:3, :3], dtype=torch.float64))
        cameras.append(
            CameraModel(
                name=name,
                width=width,
                height=height,
                fx=float(intrinsic[0, 0]),
                fy=float(intrinsic[1, 1]),
                cx=float(intrinsic[0, 2]),
                cy=float(intrinsic[1, 2]),
                qvec=quaternion.detach().cpu().numpy(),
                tvec=world_to_camera[:3, 3],
            )
        )
    return cameras
