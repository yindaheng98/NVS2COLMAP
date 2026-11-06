"""Extract Siggraph Asia 2026 VVC scenes into per-frame COLMAP folders."""

from __future__ import annotations

import argparse
from pathlib import Path

from nvs2colmap.colmap import run_video_colmap, run_video_colmap_refine_poses
from nvs2colmap.write_model import write_video_colmap_text_model

from .cameras import parse_camera_numbers, read_camera_meta
from .link_frames import count_frame_dirs, link_frames, select_frame_indices
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
        default=1,
        help="1-based position in the frames on disk. The first file is frame1.",
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
        "--include-cameras",
        help=(
            "Python expression of camera numbers to keep, such as 0,1,11 or "
            "range(0, 25). Every value must be an int. A number matches the YAML "
            "view name, so 0 selects 00 and 0000. Defaults to every camera."
        ),
    )
    parser.add_argument(
        "--exclude-cameras",
        help=(
            "Python expression of camera numbers to leave out, in the same form as "
            "--include-cameras. Use this to drop close-up views. Applied after --include-cameras."
        ),
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
    parser.add_argument(
        "--refine-init-pose",
        action="store_true",
        help=(
            "On the first frame, bundle-adjust the given camera poses and reuse "
            "them for later frames. Intrinsics stay fixed. Requires --use-colmap."
        ),
    )
    parser.add_argument(
        "--reestimate-init-pose",
        action="store_true",
        help=(
            "On the first frame, run COLMAP mapper from scratch, using the given "
            "camera centers as a soft position prior. Later frames reuse those "
            "poses. Requires --use-colmap."
        ),
    )
    args = parser.parse_args()
    if args.no_train_camera and args.no_test_camera:
        parser.error("Cannot set both --no-train-camera and --no-test-camera.")
    if args.n_frames is not None and args.n_frames < 1:
        parser.error("--n-frames must be at least 1.")
    if args.start_number < 1:
        parser.error("--start-number must be at least 1.")
    if args.refine_init_pose and not args.use_colmap:
        parser.error("--refine-init-pose requires --use-colmap.")
    if args.reestimate_init_pose and not args.use_colmap:
        parser.error("--reestimate-init-pose requires --use-colmap.")
    if args.refine_init_pose and args.reestimate_init_pose:
        parser.error("Cannot set both --refine-init-pose and --reestimate-init-pose.")
    try:
        args.include_camera_numbers = (
            parse_camera_numbers(args.include_cameras) if args.include_cameras else None
        )
        args.exclude_camera_numbers = (
            parse_camera_numbers(args.exclude_cameras) if args.exclude_cameras else None
        )
    except ValueError as exc:
        parser.error(str(exc))
    return args


def main() -> None:
    args = parse_args()
    folder = args.path.resolve()

    cameras, available_frames = read_camera_meta(
        folder,
        include_train=not args.no_train_camera,
        include_test=not args.no_test_camera,
        include_cameras=args.include_camera_numbers,
        exclude_cameras=args.exclude_camera_numbers,
    )
    if args.include_cameras or args.exclude_cameras:
        print("Cameras: " + " ".join(camera.view for camera in cameras))
    start_number = args.start_number
    n_frames = args.n_frames
    if args.skip_frame_linking and n_frames is None:
        n_frames = count_frame_dirs(folder / "frame%d", start_number=start_number)
    frame_indices = select_frame_indices(available_frames, start_number, n_frames)
    output_numbers = list(range(start_number, start_number + len(frame_indices)))

    frame_output_pattern = folder / "frame%d"
    distorted = any(camera.dist is not None for camera in cameras)
    image_dir_name = "input" if args.use_colmap or distorted else "images"
    mask_dir_name = "input_mask" if args.use_colmap or distorted else "image_masks"
    if not args.skip_frame_linking:
        link_frames(
            folder=folder,
            frame_pattern=frame_output_pattern,
            cameras=cameras,
            frame_indices=frame_indices,
            output_numbers=output_numbers,
            image_dirname=image_dir_name,
            mask_dirname=mask_dir_name,
        )

    colmap_cameras = [camera.camera for camera in cameras]
    n_frames = len(frame_indices)
    if not args.use_colmap:
        if distorted:
            if not args.skip_frame_linking:
                undistort_frames(
                    frame_pattern=frame_output_pattern,
                    cameras=cameras,
                    output_numbers=output_numbers,
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
            output_numbers=output_numbers,
        )
    else:
        colmap_kwargs = dict(
            output_pattern=frame_output_pattern,
            cameras=colmap_cameras,
            n_frames=n_frames,
            start_number=start_number,
            image_extension="",
            colmap_executable=args.colmap_executable,
            use_gpu=args.colmap_use_gpu,
        )
        if args.refine_init_pose or args.reestimate_init_pose:
            run_video_colmap_refine_poses(
                refine_init_pose=args.refine_init_pose,
                reestimate_init_pose=args.reestimate_init_pose,
                **colmap_kwargs,
            )
        else:
            run_video_colmap(**colmap_kwargs)

    print(f"Done: {folder}")


if __name__ == "__main__":
    main()
