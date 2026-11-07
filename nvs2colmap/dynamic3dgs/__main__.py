"""Extract Dynamic 3D Gaussians scenes into per-frame COLMAP folders."""

from __future__ import annotations

import argparse
from pathlib import Path

from nvs2colmap.colmap import run_video_colmap, run_video_colmap_refine_poses
from nvs2colmap.utils import select_frame_indices
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
        help=(
            "Number of frames to extract and write after --frame-skip. Defaults to "
            "every kept frame from --start-number through the last frame. A value "
            "past the frames that remain writes those frames."
        ),
    )
    parser.add_argument(
        "--start-number",
        type=int,
        default=1,
        help="1-based source frame to start extracting from; output frame folders use the same starting number.",
    )
    parser.add_argument(
        "--frame-skip",
        type=int,
        default=1,
        help="Keep every Nth source frame after --start-number. 1 keeps every frame.",
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
            "and undistortion of images and masks instead of only writing sparse/0 text models."
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
    if args.frame_skip < 1:
        parser.error("--frame-skip must be at least 1.")
    if args.refine_init_pose and not args.use_colmap:
        parser.error("--refine-init-pose requires --use-colmap.")
    if args.reestimate_init_pose and not args.use_colmap:
        parser.error("--reestimate-init-pose requires --use-colmap.")
    if args.refine_init_pose and args.reestimate_init_pose:
        parser.error("Cannot set both --refine-init-pose and --reestimate-init-pose.")
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
    if args.skip_frame_linking and n_frames is None:
        n_frames = count_frame_dirs(frame_output_pattern, start_number=args.start_number)
    frame_skip = 1 if args.skip_frame_linking else args.frame_skip
    frame_indices = select_frame_indices(
        range(available_frames), args.start_number, n_frames, frame_skip
    )
    output_numbers = list(range(args.start_number, args.start_number + len(frame_indices)))
    n_frames = len(frame_indices)
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
    if not args.use_colmap:
        write_video_colmap_text_model(
            output_pattern=frame_output_pattern / "sparse" / "0",
            cameras=colmap_cameras,
            n_frames=n_frames,
            start_number=args.start_number,
            image_extension="",
        )
        write_init_point_cloud(
            npz_path=folder / "init_pt_cld.npz",
            output_pattern=frame_output_pattern / "sparse" / "0" / "points3D.ply",
            n_frames=n_frames,
            start_number=args.start_number,
        )
    else:
        colmap_kwargs = dict(
            output_pattern=frame_output_pattern,
            cameras=colmap_cameras,
            n_frames=n_frames,
            start_number=args.start_number,
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
