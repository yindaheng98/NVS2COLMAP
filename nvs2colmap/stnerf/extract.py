"""Extract an ST-NeRF zip into per-frame image folders."""

from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

from nvs2colmap.utils import select_frame_indices


def count_frame_dirs(output_pattern: Path, start_number: int = 1) -> int:
    output_pattern = str(output_pattern)
    frame = start_number
    while Path(output_pattern % frame).is_dir():
        frame += 1
    n_frames = frame - start_number
    if n_frames == 0:
        raise FileNotFoundError(f"No frame directories found from pattern: {output_pattern}")
    return n_frames


def find_zip(folder: Path) -> Path:
    zips = sorted(path for path in Path(folder).iterdir() if path.is_file() and path.suffix.lower() == ".zip")
    if len(zips) != 1:
        found = ", ".join(path.name for path in zips) or "none"
        raise FileNotFoundError(f"Expected one zip file in {folder}, found {len(zips)}: {found}")
    return zips[0]


def relative_parts(name: str) -> list[str]:
    parts = [part for part in name.split("/") if part and part != "."]
    if not parts or parts[0] == "__MACOSX":
        return []
    if parts[0] != "pose" and not parts[0].startswith("frame"):
        parts = parts[1:]
    return parts


def extract_member(archive: zipfile.ZipFile, member: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(member) as src, dest.open("wb") as dst:
        shutil.copyfileobj(src, dst)


def extract_zip(
    folder: Path,
    image_dirname: str,
    start_number: int = 1,
    n_frames: int | None = None,
    frame_skip: int = 1,
) -> int:
    folder = Path(folder)
    archive_path = find_zip(folder)
    with zipfile.ZipFile(archive_path) as archive:
        pose_members: dict[str, str] = {}
        images: dict[tuple[int, str], str] = {}
        for info in archive.infolist():
            if info.is_dir():
                continue
            parts = relative_parts(info.filename)
            if parts[:1] == ["pose"] and len(parts) == 2 and parts[1] in {"K.txt", "RT_c2w.txt"}:
                pose_members[parts[1]] = info.filename
                continue
            if len(parts) != 3 or parts[1] != "images" or not parts[2].lower().endswith(".png"):
                continue
            frame_match = re.compile(r"frame(\d+)").fullmatch(parts[0])
            if frame_match:
                images[(int(frame_match.group(1)), parts[2])] = info.filename

        for name in ("K.txt", "RT_c2w.txt"):
            member = pose_members.get(name)
            if member is None:
                raise FileNotFoundError(f"Missing pose/{name} in {archive_path}")
            extract_member(archive, member, folder / "pose" / name)

        frame_ids = {frame for frame, _ in images}
        if not frame_ids:
            raise FileNotFoundError(f"No frame images in {archive_path}")
        # Frame folders are frame1, frame2, ... so the 1-based position is the frame id.
        selected = select_frame_indices(range(1, max(frame_ids) + 1), start_number, n_frames, frame_skip)
        output_numbers = range(start_number, start_number + len(selected))
        for frame, output_number in zip(selected, output_numbers):
            members = {filename: member for (frame_id, filename), member in images.items() if frame_id == frame}
            if not members:
                raise FileNotFoundError(f"Missing frame{frame}/images in {archive_path}")
            for filename, member in members.items():
                extract_member(archive, member, folder / f"frame{output_number}" / image_dirname / filename)
    return len(selected)
