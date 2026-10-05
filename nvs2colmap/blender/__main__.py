"""Render a Blender file into an n3dv scene directory."""

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np

from nvs2colmap.n3dv.poses_bounds import read_camera_meta_n3dv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a .blend file into camera videos next to poses_bounds.npy."
    )
    parser.add_argument("--path", type=Path, required=True, help="Scene directory containing poses_bounds.npy.")
    parser.add_argument("--blend", type=Path, required=True, help="Blender file to render.")
    parser.add_argument("--blender", default="blender", help="Blender executable.")
    parser.add_argument("--n-frames", type=int, help="Number of frames to render. Defaults to the rest of the scene.")
    parser.add_argument("--start-number", type=int, default=1, help="1-based scene frame to start rendering from.")
    args = parser.parse_args()

    folder = args.path.absolute()
    n_cameras, Rs, Ts, hwf, _ = read_camera_meta_n3dv(folder)
    w2c = np.tile(np.eye(4), (n_cameras, 1, 1))
    w2c[:, :3, :3] = Rs.numpy()
    w2c[:, :3, 3] = Ts.numpy()
    # OpenCV camera (+Z forward, +Y down) to Blender camera (-Z forward, +Y up).
    c2w = np.linalg.inv(w2c) @ np.diag([1.0, -1.0, -1.0, 1.0])
    hwf = hwf.numpy()
    pad = max(2, len(str(n_cameras - 1)))
    cameras = [
        [f"cam{i:0{pad}d}", int(round(float(hwf[i, 0]))), int(round(float(hwf[i, 1]))), float(hwf[i, 2]), c2w[i].tolist()]
        for i in range(n_cameras)
    ]
    subprocess.run(
        [
            args.blender,
            str(args.blend.absolute()),
            "--background",
            "--python-exit-code",
            "1",
            "--python",
            str(Path(__file__).with_name("render.py")),
            "--",
            "--output",
            str(folder),
            "--cameras",
            json.dumps(cameras, separators=(",", ":")),
            "--start-number",
            str(args.start_number),
            *(["--n-frames", str(args.n_frames)] if args.n_frames is not None else []),
        ],
        check=True,
    )
    print(f"Done: {folder}")


if __name__ == "__main__":
    main()
