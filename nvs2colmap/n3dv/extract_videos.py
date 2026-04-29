"""Extract Neural 3D Video camera videos into frame input folders."""

from pathlib import Path

from nvs2colmap.colmap import CameraModel
from nvs2colmap.utils.ffmpeg import extract_video_frames


def find_camera_video(dataset_path: Path, camera: CameraModel) -> Path:
    video_path = dataset_path / f"{camera.name}.mp4"
    if video_path.is_file():
        return video_path

    matches = [
        path
        for path in dataset_path.iterdir()
        if path.is_file()
        and path.stem == camera.name
        and path.suffix.lower() == ".mp4"
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise FileExistsError(f"Multiple camera videos match {camera.name}.mp4: {matches}")
    raise FileNotFoundError(f"Missing camera video: {video_path}")


def extract_videos(
    dataset_path: Path,
    output_pattern: Path,
    cameras: list[CameraModel],
    n_frames: int | None,
    ffmpeg_executable: str = "ffmpeg",
    ffprobe_executable: str = "ffprobe",
    image_extension: str = ".png",
) -> int:
    extracted_n_frames = 0
    for camera in cameras:
        video_path = find_camera_video(dataset_path, camera)
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
