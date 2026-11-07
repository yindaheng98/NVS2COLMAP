"""Convert ST-NeRF scenes into per-frame COLMAP folders."""

from __future__ import annotations

import argparse
from pathlib import Path

from nvs2colmap.colmap import run_video_colmap, run_video_colmap_refine_poses
from nvs2colmap.write_model import write_video_colmap_text_model

from .extract import extract_zip
from .pose import read_cameras


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert an ST-NeRF scene with pose/K.txt and pose/RT_c2w.txt "
            "to per-frame COLMAP text models."
        )
    )
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Scene directory containing one zip file.",
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
        help="1-based source frame to start from. frame1 in the zip is frame 1. Output folders are renumbered from frame1.",
    )
    parser.add_argument(
        "--frame-skip",
        type=int,
        default=1,
        help="Keep every Nth source frame after --start-number. 1 keeps every frame.",
    )
    parser.add_argument(
        "--use-colmap",
        action="store_true",
        help=(
            "Run COLMAP feature extraction, matching, triangulation, mapping, "
            "and image undistortion instead of only writing sparse/0 text models."
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

    frame_output_pattern = folder / "frame%d"
    image_dir_name = "input" if args.use_colmap else "images"
    n_frames = extract_zip(
        folder=folder,
        image_dirname=image_dir_name,
        start_number=args.start_number,
        n_frames=args.n_frames,
        frame_skip=args.frame_skip,
    )

    cameras = read_cameras(folder, 1, image_dir_name)

    if not args.use_colmap:
        write_video_colmap_text_model(
            output_pattern=frame_output_pattern / "sparse" / "0",
            cameras=cameras,
            n_frames=n_frames,
            start_number=1,
            image_extension="",
        )
    else:
        colmap_kwargs = dict(
            output_pattern=frame_output_pattern,
            cameras=cameras,
            n_frames=n_frames,
            start_number=1,
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
