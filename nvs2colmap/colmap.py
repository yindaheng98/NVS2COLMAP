"""Base COLMAP data structures and text model writers."""

import os
from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class CameraModel:
    """A static camera model converted from one row of poses_bounds.npy."""

    name: str
    width: int
    height: int
    fx: float
    fy: float
    cx: float
    cy: float
    qvec: np.ndarray
    tvec: np.ndarray


def write_colmap_text_model(
    path,
    cameras: Sequence[CameraModel],
    image_extension: str = ".png",
) -> None:
    colmap_cameras, colmap_images = {}, {}
    for camera in cameras:
        img_name = f"{camera.name}{image_extension}"
        height, width = camera.height, camera.width
        fx, fy = camera.fx, camera.fy
        cx, cy = camera.cx, camera.cy
        colmap_cameras[img_name] = f"PINHOLE {width} {height} {fx} {fy} {cx} {cy}"
        q, t = camera.qvec, camera.tvec
        colmap_images[img_name] = f"{q[0]} {q[1]} {q[2]} {q[3]} {t[0]} {t[1]} {t[2]}"

    cam_ids = {f"{camera.name}{image_extension}": i for i, camera in enumerate(cameras, start=1)}
    image_ids = {f"{camera.name}{image_extension}": i for i, camera in enumerate(cameras, start=1)}

    mapper_input_path = path
    os.makedirs(mapper_input_path, exist_ok=True)
    with open(os.path.join(mapper_input_path, "cameras.txt"), "w") as f:
        for img_name, cam_id in sorted(cam_ids.items(), key=lambda i: i[1]):
            f.write(f"{cam_id} {colmap_cameras[img_name]}\n")
    with open(os.path.join(mapper_input_path, "images.txt"), "w") as f:
        for img_name, image_id in sorted(image_ids.items(), key=lambda i: i[1]):
            f.write(f"{image_id} {colmap_images[img_name]} {cam_ids[img_name]} {img_name}\n\n")
    open(os.path.join(mapper_input_path, "points3D.txt"), "w").close()


def write_video_colmap_text_model(
    output_pattern,
    cameras: Sequence[CameraModel],
    n_frames: int,
    start_number: int = 1,
    image_extension: str = ".png",
) -> None:
    output_pattern = str(output_pattern)
    for frame in range(start_number, start_number + n_frames):
        write_colmap_text_model(
            output_pattern % frame,
            cameras,
            image_extension=image_extension,
        )
