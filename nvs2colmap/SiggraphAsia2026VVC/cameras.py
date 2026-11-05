"""Read Siggraph Asia volumetric-video camera YAML into COLMAP cameras."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from nvs2colmap.utils import matrix_to_quaternion
from nvs2colmap.write_model import CameraModel

_MATRIX_KEY = re.compile(r"^([A-Za-z0-9_]+):\s*!!opencv-matrix\s*$")
_SCALAR_KEY = re.compile(r"^([A-Za-z0-9_]+):\s*([-+0-9.eE]+)\s*$")
_LIST_KEY = re.compile(r"^([A-Za-z0-9_]+):\s*$")
_LIST_ITEM = re.compile(r"""^-\s+["']?(.*?)["']?\s*$""")


@dataclass(frozen=True)
class ParsedCamera:
    """One static camera and the source image for every frame index."""

    camera: CameraModel
    view: str
    frames: dict[int, Path]
    dist: np.ndarray | None = None


def parse_opencv_yaml(path: Path) -> dict:
    """Parse an EasyVolCap OpenCV YAML file into names, matrices, and scalars."""
    values: dict = {}
    lines = path.read_text().splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line or line.startswith("%") or line == "---" or line.startswith("#"):
            continue
        matrix_match = _MATRIX_KEY.match(line)
        if matrix_match:
            matrix, index = _read_matrix(lines, index)
            values[matrix_match.group(1)] = matrix
            continue
        if _LIST_KEY.match(line) and index < len(lines) and lines[index].strip().startswith("-"):
            key = _LIST_KEY.match(line).group(1)
            items = []
            while index < len(lines):
                item_match = _LIST_ITEM.match(lines[index].strip())
                if not item_match:
                    break
                items.append(item_match.group(1))
                index += 1
            values[key] = items
            continue
        scalar_match = _SCALAR_KEY.match(line)
        if scalar_match:
            values[scalar_match.group(1)] = float(scalar_match.group(2))
    return values


def _read_matrix(lines: list[str], index: int) -> tuple[np.ndarray, int]:
    rows = cols = None
    data: list[float] = []
    while index < len(lines):
        item = lines[index].strip()
        if item.startswith("rows:"):
            rows = int(item.split(":", 1)[1])
            index += 1
        elif item.startswith("cols:"):
            cols = int(item.split(":", 1)[1])
            index += 1
        elif item.startswith("dt:"):
            index += 1
        elif item.startswith("data:"):
            buffer = item.split(":", 1)[1]
            index += 1
            while buffer.count("[") > buffer.count("]") and index < len(lines):
                buffer += lines[index]
                index += 1
            start = buffer.index("[") + 1
            end = buffer.rindex("]")
            data = [float(value) for value in buffer[start:end].split(",") if value.strip()]
            break
        else:
            break
    if rows is None or cols is None or len(data) != rows * cols:
        raise ValueError("Incomplete OpenCV matrix in camera YAML.")
    return np.asarray(data, dtype=np.float64).reshape(rows, cols), index


def rodrigues(rvec: np.ndarray) -> np.ndarray:
    rvec = np.asarray(rvec, dtype=np.float64).reshape(3)
    theta = float(np.linalg.norm(rvec))
    if theta == 0.0:
        return np.eye(3, dtype=np.float64)
    axis = rvec / theta
    kx, ky, kz = axis
    skew = np.array(
        [[0.0, -kz, ky], [kz, 0.0, -kx], [-ky, kx, 0.0]],
        dtype=np.float64,
    )
    return np.eye(3) + np.sin(theta) * skew + (1.0 - np.cos(theta)) * (skew @ skew)


def rotation_matrix(extri: dict, view: str) -> np.ndarray:
    return rodrigues(extri[f"R_{view}"])


def list_view_frames(view_dir: Path) -> dict[int, Path]:
    frames = {
        int(path.stem): path
        for path in sorted(view_dir.glob("*.jpg"))
        if path.stem.isdigit()
    }
    if not frames:
        raise FileNotFoundError(f"No frames found in {view_dir}")
    return frames


def distortion_coeffs(values: dict, view: str) -> np.ndarray | None:
    raw = values.get(f"D_{view}")
    if raw is None:
        return None
    coeffs = np.asarray(raw, dtype=np.float64).reshape(-1)
    if not np.any(coeffs):
        return None
    return coeffs


def read_split(
    folder: Path,
    intri_name: str,
    extri_name: str,
) -> list[ParsedCamera]:
    folder = Path(folder)
    intri_path = folder / intri_name
    extri_path = folder / extri_name
    if not intri_path.is_file() or not extri_path.is_file():
        raise FileNotFoundError(f"Missing {intri_name} or {extri_name} in {folder}")
    intri = parse_opencv_yaml(intri_path)
    extri = parse_opencv_yaml(extri_path)
    cameras = []
    for view in sorted(intri["names"]):
        view_dir = folder / "images" / view
        if not view_dir.is_dir():
            continue
        frames = list_view_frames(view_dir)
        intrinsic = np.asarray(intri[f"K_{view}"], dtype=np.float64).reshape(3, 3)
        rotation = rotation_matrix(extri, view)
        translation = np.asarray(extri[f"T_{view}"], dtype=np.float64).reshape(3)
        quaternion = matrix_to_quaternion(torch.tensor(rotation, dtype=torch.float64))
        cameras.append(
            ParsedCamera(
                camera=CameraModel(
                    name=f"{view}.jpg",
                    width=int(intri[f"W_{view}"]),
                    height=int(intri[f"H_{view}"]),
                    fx=float(intrinsic[0, 0]),
                    fy=float(intrinsic[1, 1]),
                    cx=float(intrinsic[0, 2]),
                    cy=float(intrinsic[1, 2]),
                    qvec=quaternion.detach().cpu().numpy(),
                    tvec=translation,
                ),
                view=view,
                frames=frames,
                dist=distortion_coeffs(intri, view),
            )
        )
    return cameras


def read_camera_meta(
    folder: Path,
    include_train: bool = True,
    include_test: bool = True,
) -> tuple[list[ParsedCamera], list[int]]:
    folder = Path(folder)
    train_cameras: list[ParsedCamera] = []
    test_cameras: list[ParsedCamera] = []
    if include_train:
        train_cameras = read_split(folder, "train_intri.yml", "train_extri.yml")
    if include_test and (folder / "test_intri.yml").is_file():
        test_cameras = read_split(folder, "test_intri.yml", "test_extri.yml")
    elif include_test and not include_train:
        raise FileNotFoundError(f"Missing test_intri.yml or test_extri.yml in {folder}")

    merged: dict[str, ParsedCamera] = {}
    for camera in train_cameras + test_cameras:
        merged.setdefault(camera.view, camera)
    if not merged:
        raise ValueError(f"No cameras with images found in {folder}")

    cameras = [merged[view] for view in sorted(merged)]
    return cameras, sorted(cameras[0].frames)
