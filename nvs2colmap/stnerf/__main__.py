"""Convert ST-NeRF scenes into per-frame COLMAP folders."""

from __future__ import annotations

import argparse
from pathlib import Path

from nvs2colmap.colmap import run_video_colmap
from nvs2colmap.write_model import write_video_colmap_text_model

from .link_frames import count_frame_dirs, prepare_frames
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
        help="Scene directory containing pose/K.txt, pose/RT_c2w.txt, and frame*/images.",
    )
    parser.add_argument(
        "--n-frames",
        type=int,
        help="Number of frames to write. Defaults to the consecutive frame directories from --start-number.",
    )
    parser.add_argument(
        "--start-number",
        type=int,
        default=1,
        help="1-based source frame to start from. frame1 is frame 1.",
    )
    parser.add_argument(
        "--skip-frame-linking",
        action="store_true",
        help="Only convert pose files for existing frame folders.",
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    folder = args.path.resolve()
    cameras = read_cameras(folder, args.start_number)

    n_frames = args.n_frames
    frame_output_pattern = folder / "frame%d"
    if not args.skip_frame_linking:
        if n_frames is None:
            n_frames = count_frame_dirs(frame_output_pattern, start_number=args.start_number)
        prepare_frames(
            folder=folder,
            cameras=cameras,
            n_frames=n_frames,
            start_number=args.start_number,
            link_to_input=args.use_colmap,
        )
    elif n_frames is None:
        n_frames = count_frame_dirs(frame_output_pattern, start_number=args.start_number)

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
        )

    print(f"Done: {folder}")


if __name__ == "__main__":
    main()
