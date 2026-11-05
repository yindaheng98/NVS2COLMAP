"""Undistort known-pose frames with COLMAP when the source cameras have distortion."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Sequence

import numpy as np

from nvs2colmap.utils.colmap import execute, image_undistorter, mask_undistorter

from .cameras import ParsedCamera


def camera_model_params(camera: ParsedCamera) -> str:
    model = camera.camera
    base = f"{model.width} {model.height} {model.fx} {model.fy} {model.cx} {model.cy}"
    if camera.dist is None:
        return f"PINHOLE {base}"
    k1, k2, p1, p2 = np.asarray(camera.dist, dtype=np.float64).reshape(-1)[:4]
    return f"OPENCV {base} {k1} {k2} {p1} {p2}"


def write_distorted_model(path: Path, cameras: Sequence[ParsedCamera]) -> None:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    names = [camera.camera.name for camera in cameras]
    with open(path / "cameras.txt", "w") as output:
        for camera_id, camera in enumerate(cameras, start=1):
            output.write(f"{camera_id} {camera_model_params(camera)}\n")
    with open(path / "images.txt", "w") as output:
        for image_id, camera in enumerate(cameras, start=1):
            q, t = camera.camera.qvec, camera.camera.tvec
            pose = f"{q[0]} {q[1]} {q[2]} {q[3]} {t[0]} {t[1]} {t[2]}"
            output.write(f"{image_id} {pose} {image_id} {names[image_id - 1]}\n\n")
    (path / "points3D.txt").write_text("")


def publish_undistorted_model(frame_dir: Path, colmap_executable: str) -> None:
    source = frame_dir / "sparse"
    output = frame_dir / "sparse" / "0"
    staging = frame_dir / ".sparse_txt"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir()
    if execute([
        colmap_executable, "model_converter",
        "--input_path", str(source),
        "--output_path", str(staging),
        "--output_type", "TXT",
    ]) != 0:
        raise RuntimeError(f"Could not convert the undistorted model in {frame_dir}")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for name in ("cameras.txt", "images.txt", "points3D.txt"):
        shutil.move(staging / name, output / name)
    shutil.rmtree(staging)


def undistort_frames(
    frame_pattern: Path,
    cameras: Sequence[ParsedCamera],
    output_numbers: Sequence[int],
    colmap_executable: str = "colmap",
) -> None:
    frame_pattern = str(frame_pattern)
    image_names = [camera.camera.name for camera in cameras]
    for output_number in output_numbers:
        frame_dir = Path(frame_pattern % output_number)
        write_distorted_model(frame_dir / "distorted" / "sparse" / "0", cameras)
        if image_undistorter(str(frame_dir), colmap_executable=colmap_executable) != 0:
            raise RuntimeError(f"Undistortion failed for {frame_dir}")
        if mask_undistorter(frame_dir, image_names, colmap_executable=colmap_executable) != 0:
            raise RuntimeError(f"Mask undistortion failed for {frame_dir}")
        publish_undistorted_model(frame_dir, colmap_executable)
