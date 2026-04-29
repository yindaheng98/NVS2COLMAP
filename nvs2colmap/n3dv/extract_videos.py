"""Extract Neural 3D Video camera videos into frame input folders."""

from pathlib import Path

from nvs2colmap.colmap import CameraModel
from nvs2colmap.utils.ffmpeg import extract_video_frames


def count_frame_dirs(output_pattern: Path, start_number: int = 1) -> int:
    output_pattern = str(output_pattern)
    frame = start_number
    while Path(output_pattern % frame).is_dir():
        frame += 1
    n_frames = frame - start_number
    if n_frames == 0:
        raise FileNotFoundError(f"No frame directories found from pattern: {output_pattern}")
    return n_frames


def list_camera_videos(dataset_path: Path, video_extension: str = ".mp4") -> list[Path]:
    if not video_extension.startswith("."):
        video_extension = f".{video_extension}"
    video_extension = video_extension.lower()
    videos = [
        path
        for path in dataset_path.iterdir()
        if path.is_file() and path.suffix.lower() == video_extension
    ]
    if not videos:
        raise FileNotFoundError(f"No {video_extension} camera videos found in {dataset_path}")
    return sorted(videos)


def extract_videos(
    output_pattern: Path,
    cameras: list[CameraModel],
    camera_videos: list[Path],
    n_frames: int | None,
    ffmpeg_executable: str = "ffmpeg",
    ffprobe_executable: str = "ffprobe",
    image_extension: str = ".png",
) -> int:
    if len(camera_videos) != len(cameras):
        raise ValueError(f"Expected {len(cameras)} camera videos, got {len(camera_videos)}.")

    extracted_n_frames = 0
    for camera, video_path in zip(cameras, camera_videos):
        camera_output_pattern = output_pattern / "input" / f"{camera.name}{image_extension}"
        camera_n_frames = extract_video_frames(
            video_path=video_path,
            output_pattern=str(camera_output_pattern),
            n_frames=n_frames,
            ffmpeg_executable=ffmpeg_executable,
            ffprobe_executable=ffprobe_executable,
        )
        extracted_n_frames = max(extracted_n_frames, camera_n_frames)
    if extracted_n_frames == 0:
        raise ValueError("No cameras to extract.")
    return extracted_n_frames
