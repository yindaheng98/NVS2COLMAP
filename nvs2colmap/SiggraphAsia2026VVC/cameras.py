"""Read Siggraph Asia volumetric-video camera YAML into COLMAP cameras."""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from nvs2colmap.utils import matrix_to_quaternion
from nvs2colmap.write_model import CameraModel

_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")
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


def read_image_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        if signature.startswith(b"\x89PNG\r\n\x1a\n"):
            handle.seek(16)
            width, height = struct.unpack(">II", handle.read(8))
            return int(width), int(height)
        if not signature.startswith(b"\xff\xd8"):
            raise ValueError(f"Unsupported image file: {path}")
        handle.seek(2)
        while True:
            prefix = handle.read(1)
            if prefix != b"\xff":
                break
            marker = handle.read(1)
            while marker == b"\xff":
                marker = handle.read(1)
            if marker in {b"\xd8", b"\xd9"} or not marker:
                continue
            length_bytes = handle.read(2)
            if len(length_bytes) < 2:
                break
            length = struct.unpack(">H", length_bytes)[0]
            if marker in {b"\xc0", b"\xc1", b"\xc2"}:
                handle.read(1)
                height, width = struct.unpack(">HH", handle.read(4))
                return int(width), int(height)
            handle.seek(length - 2, 1)
    raise ValueError(f"Could not read image size: {path}")


def rodrigues(rvec: np.ndarray) -> np.ndarray:
    rvec = np.asarray(rvec, dtype=np.float64).reshape(3)
    theta = float(np.linalg.norm(rvec))
    if theta < 1e-12:
        return np.eye(3, dtype=np.float64)
    axis = rvec / theta
    kx, ky, kz = axis
    skew = np.array(
        [[0.0, -kz, ky], [kz, 0.0, -kx], [-ky, kx, 0.0]],
        dtype=np.float64,
    )
    return np.eye(3) + np.sin(theta) * skew + (1.0 - np.cos(theta)) * (skew @ skew)


def rotation_matrix(extri: dict, view: str) -> np.ndarray:
    rvec = extri.get(f"R_{view}")
    if rvec is not None:
        return rodrigues(rvec)
    rotation = extri.get(f"Rot_{view}")
    if rotation is None:
        raise ValueError(f"Camera {view} has no R_{view} or Rot_{view}.")
    return np.asarray(rotation, dtype=np.float64).reshape(3, 3)


def list_view_frames(view_dir: Path) -> tuple[dict[int, Path], str]:
    frames: dict[int, Path] = {}
    suffix = None
    for path in sorted(view_dir.iterdir()):
        if not path.is_file():
            continue
        extension = path.suffix.lower()
        if extension not in _IMAGE_EXTENSIONS or not path.stem.isdigit():
            continue
        if suffix is None:
            suffix = extension
        elif extension != suffix:
            raise ValueError(f"{view_dir} mixes {suffix} and {extension} frames.")
        frame_index = int(path.stem)
        if frame_index in frames:
            raise ValueError(f"{view_dir} lists frame {frame_index} more than once.")
        frames[frame_index] = path
    if not frames or suffix is None:
        raise FileNotFoundError(f"No frames found in {view_dir}")
    return frames, suffix


def distortion_coeffs(values: dict, view: str) -> np.ndarray | None:
    raw = values.get(f"D_{view}")
    if raw is None:
        return None
    coeffs = np.asarray(raw, dtype=np.float64).reshape(-1)
    if coeffs.size == 0 or float(np.max(np.abs(coeffs))) < 1e-8:
        return None
    return coeffs


def _positive_size(values: dict, view: str) -> tuple[int, int] | None:
    width = values.get(f"W_{view}")
    height = values.get(f"H_{view}")
    if width is None or height is None:
        return None
    width = int(width)
    height = int(height)
    if width <= 0 or height <= 0:
        return None
    return width, height


def read_split(
    folder: Path,
    intri_name: str,
    extri_name: str,
    require_images: bool,
) -> list[ParsedCamera]:
    folder = Path(folder)
    intri_path = folder / intri_name
    extri_path = folder / extri_name
    if not intri_path.is_file() or not extri_path.is_file():
        raise FileNotFoundError(f"Missing {intri_name} or {extri_name} in {folder}")
    intri = parse_opencv_yaml(intri_path)
    extri = parse_opencv_yaml(extri_path)
    names = intri.get("names")
    if not names:
        raise ValueError(f"{intri_path} has no camera names.")
    extri_names = extri.get("names")
    if extri_names is not None and set(extri_names) != set(names):
        raise ValueError(f"{intri_name} and {extri_name} list different cameras.")

    cameras = []
    seen = set()
    for view in sorted(names):
        if view in seen:
            raise ValueError(f"{intri_name} lists camera {view} more than once.")
        seen.add(view)
        view_dir = folder / "images" / view
        if not view_dir.is_dir():
            if require_images:
                raise FileNotFoundError(f"Camera {view} is listed in {intri_name} but {view_dir} is missing.")
            continue
        frames, suffix = list_view_frames(view_dir)
        intrinsic = np.asarray(intri[f"K_{view}"], dtype=np.float64).reshape(3, 3)
        rotation = rotation_matrix(extri, view)
        translation = np.asarray(extri[f"T_{view}"], dtype=np.float64).reshape(3)
        size = _positive_size(intri, view)
        if size is None:
            size = read_image_size(frames[min(frames)])
        width, height = size
        quaternion = matrix_to_quaternion(torch.tensor(rotation, dtype=torch.float64))
        cameras.append(
            ParsedCamera(
                camera=CameraModel(
                    name=f"{view}{suffix}",
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
                dist=distortion_coeffs(intri, view),
            )
        )
    return cameras


def _same_camera(left: ParsedCamera, right: ParsedCamera) -> bool:
    return (
        left.camera.width == right.camera.width
        and left.camera.height == right.camera.height
        and np.allclose(
            [left.camera.fx, left.camera.fy, left.camera.cx, left.camera.cy],
            [right.camera.fx, right.camera.fy, right.camera.cx, right.camera.cy],
            rtol=1e-5,
            atol=1e-4,
        )
        and np.allclose(left.camera.qvec, right.camera.qvec, rtol=1e-5, atol=1e-5)
        and np.allclose(left.camera.tvec, right.camera.tvec, rtol=1e-5, atol=1e-4)
        and left.frames.keys() == right.frames.keys()
        and _same_distortion(left.dist, right.dist)
    )


def _same_distortion(left: np.ndarray | None, right: np.ndarray | None) -> bool:
    if left is None or right is None:
        return left is None and right is None
    return np.allclose(left, right, rtol=0.0, atol=1e-8)


def read_camera_meta(
    folder: Path,
    include_train: bool = True,
    include_test: bool = True,
) -> tuple[list[ParsedCamera], list[int]]:
    if not include_train and not include_test:
        raise ValueError("At least one of train and test cameras must be included.")
    folder = Path(folder)
    train_cameras: list[ParsedCamera] = []
    test_cameras: list[ParsedCamera] = []
    if include_train and (folder / "train_intri.yml").is_file():
        train_cameras = read_split(folder, "train_intri.yml", "train_extri.yml", require_images=True)
    elif include_train and (folder / "intri.yml").is_file():
        train_cameras = read_split(folder, "intri.yml", "extri.yml", require_images=False)
    elif include_train:
        raise FileNotFoundError(f"Missing train_intri.yml or intri.yml in {folder}")
    if include_test and (folder / "test_intri.yml").is_file() and (folder / "test_extri.yml").is_file():
        test_cameras = read_split(folder, "test_intri.yml", "test_extri.yml", require_images=False)
    elif include_test and not include_train:
        raise FileNotFoundError(f"Missing test_intri.yml or test_extri.yml in {folder}")

    merged: dict[str, ParsedCamera] = {}
    for camera in train_cameras + test_cameras:
        previous = merged.get(camera.view)
        if previous is not None and not _same_camera(previous, camera):
            raise ValueError(f"Camera {camera.view} disagrees between train and test YAML.")
        if previous is None:
            merged[camera.view] = camera
    if not merged:
        raise ValueError(f"No cameras with images found in {folder}")

    cameras = [merged[view] for view in sorted(merged)]
    frame_sets = [set(camera.frames) for camera in cameras]
    if any(frames != frame_sets[0] for frames in frame_sets):
        raise ValueError(f"Cameras in {folder} do not share the same frame indices.")
    return cameras, sorted(frame_sets[0])
