"""Sample cameras on a spherical cap, write poses_bounds.npy, and place them in Blender."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def cap_direction(axis, cap_angle, rng):
    z = rng.uniform(np.cos(cap_angle), 1.0)
    phi = rng.uniform(0, 2 * np.pi)
    xy = np.sqrt(1 - z * z)
    local = np.array([xy * np.cos(phi), xy * np.sin(phi), z])
    helper = np.array([0.0, 1.0, 0.0]) if abs(axis[2]) > 0.999 else np.array([0.0, 0.0, 1.0])
    tangent = np.cross(helper, axis)
    tangent /= np.linalg.norm(tangent)
    bitangent = np.cross(axis, tangent)
    return tangent * local[0] + bitangent * local[1] + axis * local[2]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--blend", type=Path, required=True, help="Blender file to open when placing the sampled cameras.")
    parser.add_argument("--blender", default="blender", help="Blender executable.")
    parser.add_argument("--n-cameras", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--focal", type=float, required=True, help="Focal length in pixels. fx = fy, principal point at the image center.")
    parser.add_argument("--center", type=float, nargs=3, required=True, help="Shell center and look-at point.")
    parser.add_argument("--radius-min", type=float, default=10.0)
    parser.add_argument("--radius-max", type=float, default=12.0)
    parser.add_argument("--azimuth", type=float, default=0.0, help="Cap axis azimuth in degrees.")
    parser.add_argument("--elevation", type=float, default=90.0, help="Cap axis elevation in degrees. 90 looks straight up.")
    parser.add_argument("--cap-angle", type=float, default=90.0, help="Cap half-angle in degrees. 90 is a hemisphere; smaller clusters cameras on one side.")
    parser.add_argument("--min-angle", type=float, default=10.0, help="Minimum angle in degrees between a camera and its nearest neighbor.")
    parser.add_argument("--max-angle", type=float, default=45.0, help="Maximum angle in degrees between a camera and its nearest neighbor.")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)

    azimuth = np.deg2rad(args.azimuth)
    elevation = np.deg2rad(args.elevation)
    axis = np.array([
        np.cos(elevation) * np.cos(azimuth),
        np.cos(elevation) * np.sin(azimuth),
        np.sin(elevation),
    ])
    cap_angle = np.deg2rad(args.cap_angle)
    min_angle = np.deg2rad(args.min_angle)
    max_angle = np.deg2rad(args.max_angle)
    center = np.array(args.center)
    rng = np.random.default_rng()

    directions = []
    radii = []
    tries = 0
    while len(directions) < args.n_cameras:
        tries += 1
        if tries > 100:
            raise RuntimeError("Could not place that many cameras on this cap.")
        direction = cap_direction(axis, cap_angle, rng)
        if directions:
            nearest = np.arccos(np.clip(np.stack(directions) @ direction, -1.0, 1.0)).min()
            if nearest < min_angle or nearest > max_angle:
                continue
        directions.append(direction)
        radii.append(rng.uniform(args.radius_min, args.radius_max))

    rows = []
    poses = []
    for direction, radius in zip(directions, radii):
        position = center + direction * radius
        forward = center - position
        forward /= np.linalg.norm(forward)
        up = np.array([0.0, 0.0, 1.0])
        right = np.cross(forward, up)
        if np.dot(right, right) == 0:
            up = np.array([0.0, 1.0, 0.0])
            right = np.cross(forward, up)
        right /= np.linalg.norm(right)
        down = np.cross(forward, right)
        c2w = np.eye(4)
        c2w[:3, 0] = right
        c2w[:3, 1] = down
        c2w[:3, 2] = forward
        c2w[:3, 3] = position
        poses.append(c2w)
        # Inverse of read_camera_meta_n3dv: poses_bounds columns are [down, right, back, position, hwf].
        pose = np.zeros((3, 5))
        pose[:3, 0] = c2w[:3, 1]
        pose[:3, 1] = c2w[:3, 0]
        pose[:3, 2] = -c2w[:3, 2]
        pose[:3, 3] = c2w[:3, 3]
        pose[:, 4] = (args.height, args.width, args.focal)
        rows.append(np.concatenate([pose.reshape(-1), [radius * 0.1, radius * 2]]))

    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "poses_bounds.npy"
    np.save(path, np.stack(rows))
    pad = max(2, len(str(args.n_cameras - 1)))
    # OpenCV camera (+Z forward, +Y down) to Blender camera (-Z forward, +Y up).
    blender_from_opencv = np.diag([1.0, -1.0, -1.0, 1.0])
    cameras = [
        [f"cam{i:0{pad}d}", args.height, args.width, args.focal, (c2w @ blender_from_opencv).tolist()]
        for i, c2w in enumerate(poses)
    ]
    preview = args.output / "preview.blend"
    subprocess.run(
        [
            args.blender,
            str(args.blend.absolute()),
            "--background",
            "--python-exit-code",
            "1",
            "--python",
            str(Path(__file__).with_name("preview_cameras.py")),
            "--",
            "--output",
            str(preview.absolute()),
            "--cameras",
            json.dumps(cameras, separators=(",", ":")),
        ],
        check=True,
    )
    print(f"Done: {path}")


if __name__ == "__main__":
    main()
