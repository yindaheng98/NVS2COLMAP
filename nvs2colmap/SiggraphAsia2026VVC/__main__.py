"""Extract Siggraph Asia 2026 VVC scenes into per-frame COLMAP folders."""

from __future__ import annotations

import argparse
from pathlib import Path

from nvs2colmap.colmap import run_video_colmap
from nvs2colmap.write_model import write_video_colmap_text_model

from .cameras import read_camera_meta
from .link_frames import count_frame_dirs, first_frame_number, link_frames, select_frame_indices
from .points import link_point_clouds
from .undistort import undistort_frames


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract a Siggraph Asia 2026 VVC scene and convert train/test "
            "camera YAML to per-frame COLMAP text models."
        )
    )
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Scene directory containing images/, train_intri.yml, and train_extri.yml.",
    )
    parser.add_argument(
        "--n-frames",
        type=int,
        help=(
            "Number of frames to extract and write. Defaults to every frame from "
            "--start-number through the last frame."
        ),
    )
    parser.add_argument(
        "--start-number",
        type=int,
        help=(
            "1-based source frame to start from. Defaults to the first frame file. "
            "Source file 000000.jpg is frame 1, and 000900.jpg is frame 901."
        ),
    )
    parser.add_argument(
        "--no-train-camera",
        action="store_true",
        help="Do not extract cameras listed in train_intri.yml and train_extri.yml.",
    )
    parser.add_argument(
        "--no-test-camera",
        action="store_true",
        help="Do not extract cameras listed in test_intri.yml and test_extri.yml.",
    )
    parser.add_argument(
        "--skip-frame-linking",
        action="store_true",
        help="Only convert camera YAML for existing frame folders.",
    )
    parser.add_argument(
        "--use-colmap",
        action="store_true",
        help=(
            "Run COLMAP feature extraction, matching, triangulation, mapping, "
            "and undistortion of images and masks instead of only writing sparse/0 text models."
        ),
    )
    parser.add_argument(
        "--colmap-executable",
        default="colmap",
        help=(
            "COLMAP executable. Views with nonzero distortion are undistorted with it, "
            "and --use-colmap uses it for the full pipeline."
        ),
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
    if args.n_frames is not None and args.n_frames < 1:
        parser.error("--n-frames must be at least 1.")
    if args.start_number is not None and args.start_number < 1:
        parser.error("--start-number must be at least 1.")
    return args


def main() -> None:
    args = parse_args()
    folder = args.path.resolve()

    cameras, available_frames = read_camera_meta(
        folder,
        include_train=not args.no_train_camera,
        include_test=not args.no_test_camera,
    )
    if args.skip_frame_linking:
        start_number = args.start_number or first_frame_number(folder)
        n_frames = args.n_frames
        if n_frames is None:
            n_frames = count_frame_dirs(folder / "frame%d", start_number=start_number)
        frame_indices = list(range(start_number - 1, start_number - 1 + n_frames))
    else:
        frame_indices = select_frame_indices(available_frames, args.start_number, args.n_frames)

    frame_output_pattern = folder / "frame%d"
    distorted = any(camera.dist is not None for camera in cameras)
    image_dir_name = "input" if args.use_colmap else "images"
    mask_dir_name = "input_mask" if args.use_colmap else "image_masks"
    if not args.skip_frame_linking:
        link_frames(
            folder=folder,
            frame_pattern=frame_output_pattern,
            cameras=cameras,
            frame_indices=frame_indices,
            image_dirname=image_dir_name,
            mask_dirname=mask_dir_name,
        )

    colmap_cameras = [camera.camera for camera in cameras]
    n_frames = len(frame_indices)
    start_number = frame_indices[0] + 1
    if not args.use_colmap:
        if distorted:
            if not args.skip_frame_linking:
                undistort_frames(
                    frame_pattern=frame_output_pattern,
                    cameras=cameras,
                    frame_indices=frame_indices,
                    colmap_executable=args.colmap_executable,
                )
        else:
            write_video_colmap_text_model(
                output_pattern=frame_output_pattern / "sparse" / "0",
                cameras=colmap_cameras,
                n_frames=n_frames,
                start_number=start_number,
                image_extension="",
            )
        link_point_clouds(
            folder=folder,
            output_pattern=frame_output_pattern / "sparse" / "0" / "points3D.ply",
            frame_indices=frame_indices,
        )
    else:
        run_video_colmap(
            output_pattern=frame_output_pattern,
            cameras=colmap_cameras,
            n_frames=n_frames,
            start_number=start_number,
            image_extension="",
            colmap_executable=args.colmap_executable,
            use_gpu=args.colmap_use_gpu,
        )

    print(f"Done: {folder}")


if __name__ == "__main__":
    main()
