"""Run COLMAP processing for generated per-frame folders."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

from nvs2colmap.write_model import CameraModel
from nvs2colmap.utils.colmap import (
    exhaustive_matcher,
    feature_extractor,
    image_undistorter,
    mapper,
    point_triangulator,
    read_db,
)


def build_colmap_records(
    cameras: Sequence[CameraModel],
    image_extension: str = ".png",
) -> tuple[dict[str, str], dict[str, str]]:
    colmap_cameras, colmap_images = {}, {}
    for camera in cameras:
        img_name = f"{camera.name}{image_extension}"
        colmap_cameras[img_name] = (
            f"PINHOLE {camera.width} {camera.height} "
            f"{camera.fx} {camera.fy} {camera.cx} {camera.cy}"
        )
        q, t = camera.qvec, camera.tvec
        colmap_images[img_name] = f"{q[0]} {q[1]} {q[2]} {q[3]} {t[0]} {t[1]} {t[2]}"
    return colmap_cameras, colmap_images


def run_colmap(
    folder: Path,
    cameras: Sequence[CameraModel],
    image_extension: str = ".png",
    colmap_executable: str = "colmap",
    use_gpu: str = "1",
) -> None:
    folder = Path(folder)
    colmap_executable = os.path.abspath(colmap_executable)
    colmap_cameras, colmap_images = build_colmap_records(cameras, image_extension)

    if feature_extractor(str(folder), use_gpu=use_gpu, colmap_executable=colmap_executable) != 0:
        raise RuntimeError("Feature extraction failed")
    if exhaustive_matcher(str(folder), use_gpu=use_gpu, colmap_executable=colmap_executable) != 0:
        raise RuntimeError("Feature matching failed")

    cam_ids, image_ids = read_db(str(folder))

    mapper_input_path = folder / "distorted" / "sparse" / "loading"
    os.makedirs(mapper_input_path, exist_ok=True)
    with open(mapper_input_path / "cameras.txt", "w") as f:
        for img_name, cam_id in sorted(cam_ids.items(), key=lambda i: i[1]):
            f.write(f"{cam_id} {colmap_cameras[img_name]}\n")
    with open(mapper_input_path / "images.txt", "w") as f:
        for img_name, image_id in sorted(image_ids.items(), key=lambda i: i[1]):
            f.write(f"{image_id} {colmap_images[img_name]} {cam_ids[img_name]} {img_name}\n\n")
    open(mapper_input_path / "points3D.txt", "w").close()

    if point_triangulator(str(folder), str(mapper_input_path), colmap_executable=colmap_executable) != 0:
        raise RuntimeError("Triangulation failed")
    if mapper(str(folder), str(mapper_input_path), colmap_executable=colmap_executable) != 0:
        raise RuntimeError("Mapping failed")

    # To fit sparse init in instantsplat
    if image_undistorter(str(folder), colmap_executable=colmap_executable) != 0:
        raise RuntimeError("Image undistortion failed")


def run_video_colmap(
    output_pattern: Path,
    cameras: Sequence[CameraModel],
    n_frames: int,
    start_number: int = 1,
    image_extension: str = ".png",
    colmap_executable: str = "colmap",
    use_gpu: str = "1",
) -> None:
    output_pattern = str(output_pattern)
    for frame in range(start_number, start_number + n_frames):
        run_colmap(
            folder=Path(output_pattern % frame),
            cameras=cameras,
            image_extension=image_extension,
            colmap_executable=colmap_executable,
            use_gpu=use_gpu,
        )
