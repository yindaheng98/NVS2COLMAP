"""Extract one or more videos into per-frame image folders."""

from __future__ import annotations

import argparse
from pathlib import Path

from nvs2colmap.utils import extract_video_frames_parallel


def extract_videos(
    video_paths: list[Path],
    output_pattern: Path,
    start_number: int = 1,
    n_frames: int | None = None,
    ffmpeg_executable: str = "ffmpeg",
    ffprobe_executable: str = "ffprobe",
    ffmpeg_processes: int = 1,
    image_extension: str = ".png",
) -> int:
    if not image_extension.startswith("."):
        image_extension = f".{image_extension}"

    jobs = []
    for index, video_path in enumerate(video_paths, start=1):
        if not video_path.is_file():
            raise FileNotFoundError(f"Missing video file: {video_path}")
        jobs.append((video_path, str(output_pattern / f"{index:04d}{image_extension}")))

    if not jobs:
        raise ValueError("At least one video path is required.")

    extracted_frame_counts = extract_video_frames_parallel(
        jobs,
        start_number=start_number,
        n_frames=n_frames,
        ffmpeg_executable=ffmpeg_executable,
        ffprobe_executable=ffprobe_executable,
        process_count=ffmpeg_processes,
    )
    return max(extracted_frame_counts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract videos into frame folders. For input videos v1.mp4 v2.mp4 "
            "and --output-pattern 'frame%d/images', extracted images are named "
            "frame1/images/0001.png, frame1/images/0002.png, etc."
        )
    )
    parser.add_argument(
        "videos",
        type=Path,
        nargs="+",
        help="Video files to extract. Image names follow this input order.",
    )
    parser.add_argument(
        "--output-pattern",
        type=Path,
        required=True,
        help="Per-frame output directory pattern, for example 'frame%%d/images'.",
    )
    parser.add_argument(
        "--n-frames",
        type=int,
        help="Number of frames to extract. Defaults to each video's available frame count.",
    )
    parser.add_argument(
        "--start-number",
        type=int,
        default=1,
        help="1-based source frame to start extracting from; output frame folders use the same starting number.",
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
        "--ffmpeg-processes",
        type=int,
        default=1,
        help="Number of ffmpeg processes to run in parallel.",
    )
    parser.add_argument(
        "--image-extension",
        default=".png",
        help="Image extension written by ffmpeg.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    n_frames = extract_videos(
        video_paths=args.videos,
        output_pattern=args.output_pattern,
        start_number=args.start_number,
        n_frames=args.n_frames,
        ffmpeg_executable=args.ffmpeg_executable,
        ffprobe_executable=args.ffprobe_executable,
        ffmpeg_processes=args.ffmpeg_processes,
        image_extension=args.image_extension,
    )
    print(f"Done: extracted up to {n_frames} frames per video.")


if __name__ == "__main__":
    main()
