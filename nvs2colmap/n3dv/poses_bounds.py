"""Read Neural 3D Video poses_bounds.npy camera metadata."""

import numpy as np
import torch

from nvs2colmap.colmap import CameraModel
from nvs2colmap.utils.rotation import matrix_to_quaternion


def read_camera_meta_n3dv(path):
    # Inverse of: https://github.com/Fyusion/LLFF/blob/master/llff/poses/pose_utils.py#L11
    poses_arr = torch.tensor(np.load(path))
    poses = poses_arr[:, :-2].reshape(-1, 3, 5)
    bds = poses_arr[:, -2:]
    hwf = poses[:, :, 4]
    c2w = torch.zeros((poses.shape[0], 4, 4), dtype=poses.dtype)
    # switch from [-y, x, z] (poses_bounds format) back to [x, -y, -z] (colmap format)
    c2w[:, :3, 0:1] = poses[:, :3, 1:2]
    c2w[:, :3, 1:2] = poses[:, :3, 0:1]
    c2w[:, :3, 2:3] = -poses[:, :3, 2:3]
    c2w[:, :3, 3:4] = poses[:, :3, 3:4]
    c2w[:, 3, 3] = 1
    w2c = torch.linalg.inv(c2w)
    Rs = w2c[:, :3, :3]
    Ts = w2c[:, :3, 3]
    return poses.shape[0], Rs, Ts, hwf, bds


def read_poses_bounds(path) -> list[CameraModel]:
    camera_meta = read_camera_meta_n3dv(path)
    n_cameras, Rs, Ts, hwf, bds = camera_meta
    cameras = []
    for i in range(n_cameras):
        img_name = "cam%02d" % i
        height, width = hwf[i, 0], hwf[i, 1]
        fx = fy = hwf[i, 2]
        cx, cy = width / 2, height / 2
        R, T = Rs[i], Ts[i]
        q, t = matrix_to_quaternion(R), T
        cameras.append(
            CameraModel(
                name=img_name,
                width=int(round(float(width))),
                height=int(round(float(height))),
                fx=float(fx),
                fy=float(fy),
                cx=float(cx),
                cy=float(cy),
                qvec=q.detach().cpu().numpy(),
                tvec=t.detach().cpu().numpy(),
            )
        )
    return cameras
