"""Extract Neural 3D Video Dataset scenes into per-frame COLMAP folders."""

from __future__ import annotations

import argparse
from pathlib import Path

from nvs2colmap.colmap import run_video_colmap
from nvs2colmap.write_model import write_video_colmap_text_model

from .extract_videos import count_frame_dirs, extract_videos
from .poses_bounds import read_poses_bounds


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract a Neural 3D Video Dataset scene and convert poses_bounds.npy "
            "to per-frame COLMAP text models."
        )
    )
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Scene directory containing poses_bounds.npy and camera mp4 files.",
    )
    parser.add_argument(
        "--n-frames",
        type=int,
        help="Number of frames to extract and write. Defaults to the video frame count when extracting.",
    )
    parser.add_argument(
        "--start-number",
        type=int,
        default=1,
        help="1-based source frame to start extracting from; output frame folders and image files use the same starting number.",
    )
    parser.add_argument(
        "--ffmpeg",
        dest="ffmpeg_executable",
        default="ffmpeg",
        help="ffmpeg executable.",
    )
    parser.add_argument(
        "--ffprobe",
        dest="ffprobe_executable",
        default="ffprobe",
        help="ffprobe executable.",
    )
    parser.add_argument(
        "--image-extension",
        default=".png",
        help="Image extension written by ffmpeg and referenced by COLMAP text files.",
    )
    parser.add_argument(
        "--video-extension",
        default=".mp4",
        help="Video extension used to discover camera videos.",
    )
    parser.add_argument(
        "--skip-video-extraction",
        action="store_true",
        help="Only convert poses_bounds.npy for existing frame folders.",
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    folder = args.path.resolve()

    cameras = read_poses_bounds(folder, args.video_extension)

    n_frames = args.n_frames
    frame_output_pattern = folder / "frame%d"
    image_dir_name = "input" if args.use_colmap else "images"
    if not args.skip_video_extraction:
        n_frames = extract_videos(
            folder=folder,
            output_pattern=frame_output_pattern / image_dir_name,
            cameras=cameras,
            start_number=args.start_number,
            n_frames=n_frames,
            ffmpeg_executable=args.ffmpeg_executable,
            ffprobe_executable=args.ffprobe_executable,
            video_extension=args.video_extension,
            image_extension=args.image_extension,
        )
    elif n_frames is None:
        n_frames = count_frame_dirs(frame_output_pattern, start_number=args.start_number)

    if not args.use_colmap:
        write_video_colmap_text_model(
            output_pattern=frame_output_pattern / "sparse" / "0",
            cameras=cameras,
            n_frames=n_frames,
            start_number=args.start_number,
            image_extension=args.image_extension,
        )
    else:
        run_video_colmap(
            output_pattern=frame_output_pattern,
            cameras=cameras,
            n_frames=n_frames,
            start_number=args.start_number,
            image_extension=args.image_extension,
            colmap_executable=args.colmap_executable,
            use_gpu=args.colmap_use_gpu,
        )

    print(f"Done: {folder}")


if __name__ == "__main__":
    main()
