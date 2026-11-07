"""Extract Neural 3D Video camera videos into frame image folders."""

import shutil
from pathlib import Path

from nvs2colmap.write_model import CameraModel
from nvs2colmap.utils import extract_video_frames_parallel


def drop_frames_missing_views(output_pattern: Path, start_number: int = 1) -> int:
    """Delete trailing frames whose image count differs from the first frame.

    ``output_pattern`` is the per-frame image directory, for example
    ``scene/frame%d/input``. Scanning starts at the last frame and stops at the
    first frame that already matches. Returns how many frames remain.
    """
    pattern = str(output_pattern)
    image_dir = Path(pattern % start_number)
    n_views = sum(1 for path in image_dir.iterdir() if path.is_file())
    if n_views == 0:
        raise RuntimeError(f"{image_dir} has no views.")

    frame = start_number
    while Path(pattern % frame).is_dir():
        frame += 1
    last = frame - 1

    end = None
    frame = last
    while frame > start_number:
        image_dir = Path(pattern % frame)
        if image_dir.is_dir() and sum(1 for path in image_dir.iterdir() if path.is_file()) == n_views:
            break
        if image_dir.is_dir():
            shutil.rmtree(image_dir)
        directory = image_dir.parent
        while directory != directory.parent and directory.is_dir() and not any(directory.iterdir()):
            parent = directory.parent
            directory.rmdir()
            directory = parent
        if end is None:
            end = frame
        frame -= 1
    if end is not None:
        print(
            f"Removed {end - frame} frames whose view count is not {n_views}: "
            f"frame{frame + 1}..frame{end}"
        )
    return frame - start_number + 1


def extract_videos(
    folder: Path,
    output_pattern: Path,
    cameras: list[CameraModel],
    start_number: int = 1,
    n_frames: int | None = None,
    ffmpeg_executable: str = "ffmpeg",
    ffprobe_executable: str = "ffprobe",
    ffmpeg_processes: int = 1,
    video_extension: str = ".mp4",
    image_extension: str = ".png",
    frame_skip: int = 1,
) -> int:
    if not video_extension.startswith("."):
        video_extension = f".{video_extension}"

    jobs = []
    for camera in cameras:
        video_path = folder / f"{camera.name}{video_extension}"
        if not video_path.is_file():
            raise FileNotFoundError(f"Missing camera video: {video_path}")
        camera_output_pattern = output_pattern / f"{camera.name}{image_extension}"
        jobs.append((video_path, str(camera_output_pattern)))
    if not jobs:
        raise ValueError("No cameras to extract.")

    extract_video_frames_parallel(
        jobs,
        start_number=start_number,
        n_frames=n_frames,
        ffmpeg_executable=ffmpeg_executable,
        ffprobe_executable=ffprobe_executable,
        process_count=ffmpeg_processes,
        output_start_number=1,
        frame_skip=frame_skip,
    )
    return drop_frames_missing_views(output_pattern, start_number=1)
