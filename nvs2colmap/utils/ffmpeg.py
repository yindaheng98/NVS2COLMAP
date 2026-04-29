"""ffmpeg helpers."""

import os
import subprocess


def get_video_frame_count(video_path, ffprobe_executable: str = "ffprobe") -> int:
    cmd = [
        ffprobe_executable,
        "-v",
        "error",
        "-count_frames",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=nb_read_frames",
        "-of",
        "default=nokey=1:noprint_wrappers=1",
        str(video_path),
    ]
    output = subprocess.check_output(cmd, text=True).strip()
    return int(output)


def extract_video_frames(
    video_path, output_pattern,
    start_number: int = 1, n_frames: int | None = None,
    ffmpeg_executable: str = "ffmpeg", ffprobe_executable: str = "ffprobe",
) -> int:
    assert start_number >= 1, f"start_number must be >= 1, got {start_number}."

    video_frame_count = get_video_frame_count(video_path, ffprobe_executable)
    available_frame_count = video_frame_count - start_number + 1
    assert available_frame_count > 0, f"start_number {start_number} is outside {video_frame_count} frames in {video_path}."

    if n_frames is None:
        frame_count = available_frame_count
    else:
        assert n_frames >= 1, f"n_frames must be >= 1, got {n_frames}."
        frame_count = min(n_frames, available_frame_count)

    for frame in range(start_number, start_number + frame_count):
        os.makedirs(os.path.dirname(output_pattern % frame), exist_ok=True)

    cmd = [
        ffmpeg_executable,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video_path),
        "-frames:v", str(frame_count),
        "-start_number", str(start_number),
        str(output_pattern), "-y",
    ]
    print(" ".join(str(part) for part in cmd))
    subprocess.run(cmd, check=True)
    return frame_count
