"""Read Dynamic 3D Gaussians train and test camera metadata."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import torch

from nvs2colmap.utils import matrix_to_quaternion
from nvs2colmap.write_model import CameraModel


@dataclass(frozen=True)
class ParsedCameraMeta:
    """One static camera and the image filenames for each frame."""

    camera: CameraModel
    filenames: list[str]


def read_meta(folder: Path, meta_name: str) -> tuple[list[ParsedCameraMeta], int]:
    folder = Path(folder)
    meta_path = folder / meta_name
    with meta_path.open() as f:
        camera_meta = json.load(f)

    n_frames = len(camera_meta["fn"])
    if n_frames == 0:
        raise ValueError(f"No frames found in {meta_path}")
    for key in ("k", "w2c", "cam_id"):
        if any(camera_meta[key][frame_index] != camera_meta[key][0] for frame_index in range(n_frames)):
            raise ValueError(f"{meta_name} {key} changes across frames.")

    width = int(camera_meta["w"])
    height = int(camera_meta["h"])
    cameras = []
    seen_ids = set()
    for camera_index, (k, w2c, camera_id) in enumerate(
        zip(camera_meta["k"][0], camera_meta["w2c"][0], camera_meta["cam_id"][0])
    ):
        camera_id = int(camera_id)
        if camera_id in seen_ids:
            raise ValueError(f"{meta_name} lists camera {camera_id} more than once.")
        seen_ids.add(camera_id)
        filenames = [camera_meta["fn"][frame_index][camera_index] for frame_index in range(n_frames)]
        w2c_tensor = torch.tensor(w2c, dtype=torch.float64)
        quaternion = matrix_to_quaternion(w2c_tensor[:3, :3])
        cameras.append(
            ParsedCameraMeta(
                camera=CameraModel(
                    name=f"cam{camera_id:02d}{Path(filenames[0]).suffix}",
                    width=width,
                    height=height,
                    fx=float(k[0][0]),
                    fy=float(k[1][1]),
                    cx=float(k[0][2]),
                    cy=float(k[1][2]),
                    qvec=quaternion.detach().cpu().numpy(),
                    tvec=w2c_tensor[:3, 3].detach().cpu().numpy(),
                ),
                filenames=filenames,
            )
        )
    return cameras, n_frames


def read_camera_meta(
    folder: Path,
    include_train: bool = True,
    include_test: bool = True,
) -> tuple[list[ParsedCameraMeta], int]:
    if not include_train and not include_test:
        raise ValueError("At least one of train and test cameras must be included.")

    n_frames = None
    train_cameras, train_n_frames = [], None
    if include_train:
        train_cameras, train_n_frames = read_meta(folder, "train_meta.json")
        n_frames = train_n_frames
    test_cameras, test_n_frames = [], None
    if include_test:
        test_cameras, test_n_frames = read_meta(folder, "test_meta.json")
        n_frames = test_n_frames

    if include_train and include_test and train_n_frames != test_n_frames:
        raise ValueError("train_meta.json and test_meta.json list different frame counts.")
    cameras = train_cameras + test_cameras

    merged: dict[str, ParsedCameraMeta] = {}
    for camera in cameras:
        if camera.camera.name in merged:
            raise ValueError(f"Camera {camera.camera.name} appears in more than one metadata file.")
        merged[camera.camera.name] = camera
    if not merged:
        raise ValueError("No cameras selected.")
    return [merged[name] for name in sorted(merged)], n_frames
