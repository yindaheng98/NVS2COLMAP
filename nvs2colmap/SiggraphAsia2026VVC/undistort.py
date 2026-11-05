"""Undistort known-pose frames with COLMAP when the source cameras have distortion."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Sequence

import numpy as np

from nvs2colmap.utils.colmap import execute, image_undistorter, mask_undistorter

from .cameras import ParsedCamera


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
        model_dir = frame_dir / "distorted" / "sparse" / "0"
        model_dir.mkdir(parents=True, exist_ok=True)
        with open(model_dir / "cameras.txt", "w") as output:
            for camera_id, camera in enumerate(cameras, start=1):
                model = camera.camera
                base = f"{model.width} {model.height} {model.fx} {model.fy} {model.cx} {model.cy}"
                if camera.dist is None:
                    params = f"PINHOLE {base}"
                else:
                    k1, k2, p1, p2 = np.asarray(camera.dist, dtype=np.float64).reshape(-1)[:4]
                    params = f"OPENCV {base} {k1} {k2} {p1} {p2}"
                output.write(f"{camera_id} {params}\n")
        with open(model_dir / "images.txt", "w") as output:
            for image_id, camera in enumerate(cameras, start=1):
                q, t = camera.camera.qvec, camera.camera.tvec
                pose = f"{q[0]} {q[1]} {q[2]} {q[3]} {t[0]} {t[1]} {t[2]}"
                output.write(f"{image_id} {pose} {image_id} {camera.camera.name}\n\n")
        (model_dir / "points3D.txt").write_text("")
        if image_undistorter(str(frame_dir), colmap_executable=colmap_executable) != 0:
            raise RuntimeError(f"Undistortion failed for {frame_dir}")
        if mask_undistorter(frame_dir, image_names, colmap_executable=colmap_executable) != 0:
            raise RuntimeError(f"Mask undistortion failed for {frame_dir}")
        staging = frame_dir / ".sparse_txt"
        shutil.rmtree(staging, ignore_errors=True)
        staging.mkdir()
        if execute([
            colmap_executable, "model_converter",
            "--input_path", str(frame_dir / "sparse"),
            "--output_path", str(staging),
            "--output_type", "TXT",
        ]) != 0:
            raise RuntimeError(f"Could not convert the undistorted model in {frame_dir}")
        published = frame_dir / "sparse" / "0"
        if published.exists():
            shutil.rmtree(published)
        published.mkdir(parents=True)
        for name in ("cameras.txt", "images.txt", "points3D.txt"):
            shutil.move(staging / name, published / name)
        shutil.rmtree(staging)
