"""Extract Neural 3D Video camera videos into frame input folders."""

from pathlib import Path

from nvs2colmap.write_model import CameraModel
from nvs2colmap.utils import extract_video_frames


def count_frame_dirs(output_pattern: Path, start_number: int = 1) -> int:
    output_pattern = str(output_pattern)
    frame = start_number
    while Path(output_pattern % frame).is_dir():
        frame += 1
    n_frames = frame - start_number
    if n_frames == 0:
        raise FileNotFoundError(f"No frame directories found from pattern: {output_pattern}")
    return n_frames


def extract_videos(
    folder: Path,
    output_pattern: Path,
    cameras: list[CameraModel],
    n_frames: int | None = None,
    ffmpeg_executable: str = "ffmpeg",
    ffprobe_executable: str = "ffprobe",
    video_extension: str = ".mp4",
    image_extension: str = ".png",
) -> int:
    if not video_extension.startswith("."):
        video_extension = f".{video_extension}"

    extracted_n_frames = 0
    for camera in cameras:
        video_path = folder / f"{camera.name}{video_extension}"
        if not video_path.is_file():
            raise FileNotFoundError(f"Missing camera video: {video_path}")
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
