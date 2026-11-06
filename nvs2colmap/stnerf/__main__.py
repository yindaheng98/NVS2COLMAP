"""Convert ST-NeRF scenes into per-frame COLMAP folders."""

from __future__ import annotations

import argparse
from pathlib import Path

from nvs2colmap.colmap import run_video_colmap
from nvs2colmap.write_model import write_video_colmap_text_model

from .extract import count_frame_dirs, extract_zip
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
        help="Scene directory containing one zip file, or extracted pose/ and frame images.",
    )
    parser.add_argument(
        "--n-frames",
        type=int,
        help="Number of frames to extract and write. Defaults to the frames in the zip when extracting.",
    )
    parser.add_argument(
        "--start-number",
        type=int,
        default=1,
        help="1-based source frame to start from. frame1 is frame 1.",
    )
    parser.add_argument(
        "--skip-zip-extraction",
        action="store_true",
        help="Only convert pose files for existing frame folders. Skips reading the zip.",
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
        "--refine-poses",
        action="store_true",
        help=(
            "After triangulation, bundle-adjust the given camera poses. "
            "Intrinsics stay fixed. Requires --use-colmap."
        ),
    )
    parser.add_argument(
        "--reestimate-poses",
        action="store_true",
        help=(
            "Run COLMAP mapper from scratch, using the given camera centers "
            "as a soft position prior. Poses can still move. Requires --use-colmap."
        ),
    )
    args = parser.parse_args()
    if args.refine_poses and not args.use_colmap:
        parser.error("--refine-poses requires --use-colmap.")
    if args.reestimate_poses and not args.use_colmap:
        parser.error("--reestimate-poses requires --use-colmap.")
    if args.refine_poses and args.reestimate_poses:
        parser.error("Cannot set both --refine-poses and --reestimate-poses.")
    return args


def main() -> None:
    args = parse_args()
    folder = args.path.resolve()

    n_frames = args.n_frames
    frame_output_pattern = folder / "frame%d"
    image_dir_name = "input" if args.use_colmap else "images"
    if not args.skip_zip_extraction:
        n_frames = extract_zip(
            folder=folder,
            image_dirname=image_dir_name,
            start_number=args.start_number,
            n_frames=n_frames,
        )
    elif n_frames is None:
        n_frames = count_frame_dirs(frame_output_pattern, start_number=args.start_number)

    cameras = read_cameras(folder, args.start_number, image_dir_name)

    if not args.use_colmap:
        write_video_colmap_text_model(
            output_pattern=frame_output_pattern / "sparse" / "0",
            cameras=cameras,
            n_frames=n_frames,
            start_number=args.start_number,
            image_extension="",
        )
    else:
        run_video_colmap(
            output_pattern=frame_output_pattern,
            cameras=cameras,
            n_frames=n_frames,
            start_number=args.start_number,
            image_extension="",
            colmap_executable=args.colmap_executable,
            use_gpu=args.colmap_use_gpu,
            refine_poses=args.refine_poses,
            reestimate_poses=args.reestimate_poses,
        )

    print(f"Done: {folder}")


if __name__ == "__main__":
    main()
