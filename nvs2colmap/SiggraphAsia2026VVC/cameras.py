"""Read Siggraph Asia volumetric-video camera YAML into COLMAP cameras."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from nvs2colmap.utils import matrix_to_quaternion
from nvs2colmap.write_model import CameraModel


@dataclass(frozen=True)
class ParsedCamera:
    """One static camera and the source image for every frame index."""

    camera: CameraModel
    view: str
    frames: dict[int, Path]
    dist: np.ndarray | None = None


def read_jpeg_size(path: Path) -> tuple[int, int]:
    """Return width and height. Pillow reads the JPEG header and does not decode pixels."""
    with Image.open(path) as image:
        width, height = image.size
    return int(width), int(height)


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
        matrix_match = re.match(r"^([A-Za-z0-9_]+):\s*!!opencv-matrix\s*$", line)
        if matrix_match:
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
                raise ValueError(f"Incomplete OpenCV matrix {matrix_match.group(1)} in {path}")
            values[matrix_match.group(1)] = np.asarray(data, dtype=np.float64).reshape(rows, cols)
            continue
        list_match = re.match(r"^([A-Za-z0-9_]+):\s*$", line)
        if list_match and index < len(lines) and lines[index].strip().startswith("-"):
            items = []
            while index < len(lines):
                item_match = re.match(r"""^-\s+["']?(.*?)["']?\s*$""", lines[index].strip())
                if not item_match:
                    break
                items.append(item_match.group(1))
                index += 1
            values[list_match.group(1)] = items
            continue
        scalar_match = re.match(r"^([A-Za-z0-9_]+):\s*([-+0-9.eE]+)\s*$", line)
        if scalar_match:
            values[scalar_match.group(1)] = float(scalar_match.group(2))
    return values


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
        frames = {
            int(path.stem): path
            for path in sorted(view_dir.glob("*.jpg"))
            if path.stem.isdigit()
        }
        if not frames:
            raise FileNotFoundError(f"No frames found in {view_dir}")
        intrinsic = np.asarray(intri[f"K_{view}"], dtype=np.float64).reshape(3, 3)
        rvec = np.asarray(extri[f"R_{view}"], dtype=np.float64).reshape(3)
        theta = float(np.linalg.norm(rvec))
        if theta == 0.0:
            rotation = np.eye(3, dtype=np.float64)
        else:
            kx, ky, kz = rvec / theta
            skew = np.array(
                [[0.0, -kz, ky], [kz, 0.0, -kx], [-ky, kx, 0.0]],
                dtype=np.float64,
            )
            rotation = np.eye(3) + np.sin(theta) * skew + (1.0 - np.cos(theta)) * (skew @ skew)
        translation = np.asarray(extri[f"T_{view}"], dtype=np.float64).reshape(3)
        quaternion = matrix_to_quaternion(torch.tensor(rotation, dtype=torch.float64))
        dist = None
        if f"D_{view}" in intri:
            coeffs = np.asarray(intri[f"D_{view}"], dtype=np.float64).reshape(-1)
            if np.any(coeffs):
                dist = coeffs
        width, height = read_jpeg_size(frames[min(frames)])
        cameras.append(
            ParsedCamera(
                camera=CameraModel(
                    name=f"{view}.jpg",
                    width=width,
                    height=height,
                    fx=float(intrinsic[0, 0]),
                    fy=float(intrinsic[1, 1]),
                    cx=float(intrinsic[0, 2]),
                    cy=float(intrinsic[1, 2]),
                    qvec=quaternion.detach().cpu().numpy(),
                    tvec=translation,
                ),
                view=view,
                frames=frames,
                dist=dist,
            )
        )
    return cameras


def read_camera_meta(
    folder: Path,
    include_train: bool = True,
    include_test: bool = True,
    include_cameras: set[int] | None = None,
    exclude_cameras: set[int] | None = None,
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
    # View names are the zero-padded camera numbers: "00" in siga, "0002" in selfcap.
    if include_cameras is not None:
        cameras = [camera for camera in cameras if int(camera.view) in include_cameras]
    if exclude_cameras is not None:
        cameras = [camera for camera in cameras if int(camera.view) not in exclude_cameras]
    if not cameras:
        raise ValueError(f"No cameras with images found in {folder}")
    return cameras, sorted(cameras[0].frames)


def parse_camera_numbers(spec: str) -> set[int]:
    """Evaluate a Python expression whose values are all ints."""
    try:
        value = eval(spec)
    except Exception as exc:
        raise ValueError(f"Camera selection {spec!r} is not a Python expression of ints: {exc}") from exc
    if type(value) is int:
        value = (value,)
    try:
        numbers = list(value)
    except TypeError as exc:
        raise ValueError(f"Camera selection {spec!r} is not a sequence of ints.") from exc
    if any(type(number) is not int for number in numbers):
        raise ValueError(f"Camera selection {spec!r} must contain only ints.")
    if not numbers:
        raise ValueError("Camera selection is empty.")
    return set(numbers)
