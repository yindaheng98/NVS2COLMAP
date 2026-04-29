"""ffmpeg helpers."""

from concurrent.futures import ProcessPoolExecutor
import os
import subprocess


def count_video_frames(
    video_path,
    start_number: int = 1,
    n_frames: int | None = None,
    ffprobe_executable: str = "ffprobe",
) -> int:
    assert start_number >= 1, f"start_number must be >= 1, got {start_number}."

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
    video_frame_count = int(output)
    available_frame_count = video_frame_count - start_number + 1
    assert available_frame_count > 0, f"start_number {start_number} is outside {video_frame_count} frames in {video_path}."

    if n_frames is None:
        return available_frame_count

    assert n_frames >= 1, f"n_frames must be >= 1, got {n_frames}."
    return min(n_frames, available_frame_count)


def extract_video_frames(
    video_path, output_pattern,
    start_number: int = 1, n_frames: int | None = None,
    ffmpeg_executable: str = "ffmpeg", ffprobe_executable: str = "ffprobe",
) -> int:
    frame_count = count_video_frames(
        video_path,
        start_number=start_number,
        n_frames=n_frames,
        ffprobe_executable=ffprobe_executable,
    )

    for frame in range(start_number, start_number + frame_count):
        os.makedirs(os.path.dirname(output_pattern % frame), exist_ok=True)

    cmd = [
        ffmpeg_executable,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video_path),
        "-vf",
        f"trim=start_frame={start_number - 1}",
        "-frames:v", str(frame_count),
        "-start_number", str(start_number),
        str(output_pattern), "-y",
    ]
    print(" ".join(str(part) for part in cmd))
    subprocess.run(cmd, check=True)
    return frame_count


def extract_video_frames_task(args) -> int:
    return extract_video_frames(*args)


def extract_video_frames_parallel(
    jobs,
    start_number: int = 1,
    n_frames: int | None = None,
    ffmpeg_executable: str = "ffmpeg",
    ffprobe_executable: str = "ffprobe",
    process_count: int = 1,
) -> list[int]:
    """Extract frames from multiple videos using multiple ffmpeg processes."""
    assert process_count >= 1, f"process_count must be >= 1, got {process_count}."

    tasks = [
        (
            video_path,
            output_pattern,
            start_number,
            n_frames,
            ffmpeg_executable,
            ffprobe_executable,
        )
        for video_path, output_pattern in jobs
    ]
    if process_count == 1:
        return [extract_video_frames_task(task) for task in tasks]

    if not tasks:
        return []

    max_workers = min(process_count, len(tasks))
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(extract_video_frames_task, tasks))
