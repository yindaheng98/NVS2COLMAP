"""Run COLMAP processing for generated per-frame folders."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

import numpy as np

from nvs2colmap.write_model import CameraModel
from nvs2colmap.utils.colmap import (
    bundle_adjuster,
    exhaustive_matcher,
    feature_extractor,
    image_undistorter,
    mapper,
    mask_undistorter,
    point_triangulator,
    pose_prior_mapper,
    read_db,
    write_pose_priors,
)


def camera_center(camera: CameraModel) -> np.ndarray:
    """World-space camera center from a COLMAP cam-from-world pose."""
    qw, qx, qy, qz = (float(value) for value in camera.qvec)
    rotation = np.array(
        [
            [1 - 2 * qy * qy - 2 * qz * qz, 2 * qx * qy - 2 * qz * qw, 2 * qx * qz + 2 * qy * qw],
            [2 * qx * qy + 2 * qz * qw, 1 - 2 * qx * qx - 2 * qz * qz, 2 * qy * qz - 2 * qx * qw],
            [2 * qx * qz - 2 * qy * qw, 2 * qy * qz + 2 * qx * qw, 1 - 2 * qx * qx - 2 * qy * qy],
        ]
    )
    return -rotation.T @ np.asarray(camera.tvec, dtype=float)


def pose_prior_std(centers: Sequence[np.ndarray]) -> float:
    """Half the median spacing between cameras, so an inaccurate prior stays loose."""
    if len(centers) < 2:
        return 1.0
    points = np.stack(centers)
    distances = np.linalg.norm(points[:, None, :] - points[None, :, :], axis=-1)
    np.fill_diagonal(distances, np.inf)
    spacing = float(np.median(distances.min(axis=1)))
    if not np.isfinite(spacing) or spacing <= 0:
        return 1.0
    return 0.5 * spacing


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
    refine_poses: bool = False,
    reestimate_poses: bool = False,
) -> None:
    folder = Path(folder)

    if feature_extractor(str(folder), use_gpu=use_gpu, colmap_executable=colmap_executable) != 0:
        raise RuntimeError("Feature extraction failed")
    if exhaustive_matcher(str(folder), use_gpu=use_gpu, colmap_executable=colmap_executable) != 0:
        raise RuntimeError("Feature matching failed")

    if reestimate_poses:
        centers = {
            f"{camera.name}{image_extension}": camera_center(camera)
            for camera in cameras
        }
        write_pose_priors(
            str(folder),
            {name: tuple(center) for name, center in centers.items()},
        )
        if pose_prior_mapper(
            str(folder),
            pose_prior_std(list(centers.values())),
            colmap_executable=colmap_executable,
        ) != 0:
            raise RuntimeError("Mapping failed")
    else:
        colmap_cameras, colmap_images = build_colmap_records(cameras, image_extension)
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
        if refine_poses and bundle_adjuster(str(mapper_input_path), colmap_executable=colmap_executable) != 0:
            raise RuntimeError("Pose refinement failed")
        if mapper(str(folder), str(mapper_input_path), colmap_executable=colmap_executable) != 0:
            raise RuntimeError("Mapping failed")

    if image_undistorter(str(folder), colmap_executable=colmap_executable) != 0:
        raise RuntimeError("Undistortion failed")
    image_names = [f"{camera.name}{image_extension}" for camera in cameras]
    if mask_undistorter(folder, image_names, colmap_executable=colmap_executable) != 0:
        raise RuntimeError("Mask undistortion failed")


def run_video_colmap(
    output_pattern: Path,
    cameras: Sequence[CameraModel],
    n_frames: int,
    start_number: int = 1,
    image_extension: str = ".png",
    colmap_executable: str = "colmap",
    use_gpu: str = "1",
    refine_poses: bool = False,
    reestimate_poses: bool = False,
) -> None:
    output_pattern = str(output_pattern)
    for frame in range(start_number, start_number + n_frames):
        run_colmap(
            folder=Path(output_pattern % frame),
            cameras=cameras,
            image_extension=image_extension,
            colmap_executable=colmap_executable,
            use_gpu=use_gpu,
            refine_poses=refine_poses,
            reestimate_poses=reestimate_poses,
        )
