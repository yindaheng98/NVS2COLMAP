"""Extract Neural 3D Video Dataset scenes into per-frame COLMAP folders."""

from __future__ import annotations

import argparse
from pathlib import Path

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
        help="Only convert poses_bounds.npy into COLMAP text files for existing frame*/input folders.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    folder = args.path.resolve()

    cameras = read_poses_bounds(folder, args.video_extension)

    n_frames = args.n_frames
    if not args.skip_video_extraction:
        n_frames = extract_videos(
            folder=folder,
            output_pattern=folder / "frame%d",
            cameras=cameras,
            n_frames=n_frames,
            ffmpeg_executable=args.ffmpeg_executable,
            ffprobe_executable=args.ffprobe_executable,
            video_extension=args.video_extension,
            image_extension=args.image_extension,
        )
    elif n_frames is None:
        n_frames = count_frame_dirs(folder / "frame%d")

    write_video_colmap_text_model(
        output_pattern=folder / "frame%d" / "sparse" / "0",
        cameras=cameras,
        n_frames=n_frames,
        image_extension=args.image_extension,
    )

    print(f"Done: {folder}")


if __name__ == "__main__":
    main()
