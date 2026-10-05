"""Extract Dynamic 3D Gaussians scenes into per-frame COLMAP folders."""

from __future__ import annotations

import argparse
from pathlib import Path

from nvs2colmap.colmap import run_video_colmap
from nvs2colmap.write_model import write_video_colmap_text_model

from .camera_meta import read_camera_meta
from .link_frames import count_frame_dirs, link_frames
from .points import write_init_point_cloud


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract a Dynamic 3D Gaussians scene and convert train_meta.json "
            "and test_meta.json to per-frame COLMAP text models."
        )
    )
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Scene directory containing train_meta.json, test_meta.json, ims/, and seg/.",
    )
    parser.add_argument(
        "--n-frames",
        type=int,
        help="Number of frames to extract and write. Defaults to the frames listed in the camera metadata.",
    )
    parser.add_argument(
        "--start-number",
        type=int,
        default=1,
        help="1-based source frame to start extracting from; output frame folders use the same starting number.",
    )
    parser.add_argument(
        "--no-train-camera",
        action="store_true",
        help="Do not extract cameras listed in train_meta.json.",
    )
    parser.add_argument(
        "--no-test-camera",
        action="store_true",
        help="Do not extract cameras listed in test_meta.json.",
    )
    parser.add_argument(
        "--skip-frame-linking",
        action="store_true",
        help="Only convert camera metadata for existing frame folders.",
    )
    parser.add_argument(
        "--use-colmap",
        action="store_true",
        help=(
            "Run COLMAP feature extraction, matching, triangulation, mapping, "
            "and undistortion instead of only writing sparse/0 text models."
        ),
    )
    parser.add_argument(
        "--colmap-executable",
        default="colmap",
        help="COLMAP executable used when --use-colmap is set.",
    )
    parser.add_argument(
        "--colmap-use-gpu",
        dest="colmap_use_gpu",
        default="1",
        help="Whether COLMAP SIFT extraction/matching should use GPU when --use-colmap is set.",
    )
    args = parser.parse_args()
    if args.no_train_camera and args.no_test_camera:
        parser.error("Cannot set both --no-train-camera and --no-test-camera.")
    return args


def main() -> None:
    args = parse_args()
    folder = args.path.resolve()

    cameras, available_frames = read_camera_meta(
        folder,
        include_train=not args.no_train_camera,
        include_test=not args.no_test_camera,
    )

    n_frames = args.n_frames
    frame_output_pattern = folder / "frame%d"
    image_dir_name = "input" if args.use_colmap else "images"
    mask_dir_name = "input_mask" if args.use_colmap else "image_masks"
    if not args.skip_frame_linking:
        if n_frames is None:
            n_frames = available_frames - args.start_number + 1
        link_frames(
            folder=folder,
            frame_pattern=frame_output_pattern,
            cameras=cameras,
            n_frames=n_frames,
            start_number=args.start_number,
            image_dirname=image_dir_name,
            mask_dirname=mask_dir_name,
        )
    elif n_frames is None:
        n_frames = count_frame_dirs(frame_output_pattern, start_number=args.start_number)

    colmap_cameras = [camera.camera for camera in cameras]
    if not args.use_colmap:
        write_video_colmap_text_model(
            output_pattern=frame_output_pattern / "sparse" / "0",
            cameras=colmap_cameras,
            n_frames=n_frames,
            start_number=args.start_number,
            image_extension="",
        )
    else:
        run_video_colmap(
            output_pattern=frame_output_pattern,
            cameras=colmap_cameras,
            n_frames=n_frames,
            start_number=args.start_number,
            image_extension="",
            colmap_executable=args.colmap_executable,
            use_gpu=args.colmap_use_gpu,
        )

    write_init_point_cloud(
        npz_path=folder / "init_pt_cld.npz",
        output_pattern=frame_output_pattern / "sparse" / "0" / "points3D.ply",
        n_frames=n_frames,
        start_number=args.start_number,
    )

    print(f"Done: {folder}")


if __name__ == "__main__":
    main()
