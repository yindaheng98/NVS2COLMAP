# Neural 3D Video Dataset

This package converts scenes in the **Neural 3D Video Dataset** format into
per-frame COLMAP text models.

Runtime dependencies:

```bash
pip install numpy torch
```

The command also needs `ffmpeg` and `ffprobe` on `PATH`, or explicit paths via
`--ffmpeg` and `--ffprobe`.

## Dataset Format

A scene folder is expected to contain one `poses_bounds.npy` file plus one
video per camera:

```text
coffee_martini/
  poses_bounds.npy
  cam00.mp4
  cam01.mp4
  cam02.mp4
  ...
```

`poses_bounds.npy` follows the LLFF-style `poses_bounds` layout:

- Shape: `(num_cameras, 17)`.
- The first 15 values in each row reshape to a `3 x 5` matrix.
- The first `3 x 4` block stores the camera-to-world pose in the dataset's
  LLFF axis convention.
- The last column stores `height`, `width`, and focal length.
- The final 2 values store near/far bounds; this converter keeps the camera
  pose and intrinsics and does not write bounds into COLMAP files.

Videos are read by suffix, default `.mp4`, and sorted by filename. The sorted
videos are matched against `poses_bounds.npy` rows in that order. Output image
names and COLMAP image names use the corresponding video filename stems.

## Output Format

For each time step, the tool writes one frame directory:

```text
coffee_martini/
  frame1/
    input/
      cam00.png
      cam01.png
      ...
    sparse/0/
      cameras.txt
      images.txt
      points3D.txt
  frame2/
    input/
    sparse/0/
  ...
```

The generated COLMAP model uses `PINHOLE` cameras. Every camera has its own
COLMAP camera ID because Neural 3D Video scenes are multi-view captures with
known static camera poses.

If the source videos are named `0001.MP4`, `0002.MP4`, etc., the images and
COLMAP records are named `0001.png`, `0002.png`, etc. Use `--video-extension
MP4` for uppercase video suffixes.

## Usage

Decode videos and write COLMAP text models for an extracted scene:

```bash
python -m nvs2colmap.n3dv \
  --path data/cook_spinach \
  --ffmpeg ffmpeg \
  --ffprobe ffprobe \
  --n-frames 300
```

Decode uppercase `.MP4` videos:

```bash
python -m nvs2colmap.n3dv \
  --path data/Robo360/xarm6_gold_rope_in_basket_2 \
  --ffmpeg D:/MyPrograms/ffmpeg.exe \
  --ffprobe D:/MyPrograms/ffprobe.exe \
  --video-extension MP4 \
  --n-frames 1
```

Only regenerate camera files after frames already exist:

```bash
python -m nvs2colmap.n3dv \
  --path data/coffee_martini \
  --skip-video-extraction
```

## Important Options

- `--path`: scene directory containing `poses_bounds.npy` and camera videos.
- `--n-frames`: number of frames to extract and write. If omitted while
  extracting videos, each video is decoded to its available frame count. For
  best results, use videos with matching frame counts or pass `--n-frames`.
  If omitted with `--skip-video-extraction`, frame directories are counted
  from `frame%d`.
- `--ffmpeg`: path to the `ffmpeg` executable.
- `--ffprobe`: path to the `ffprobe` executable.
- `--image-extension`: image extension written by ffmpeg and referenced by
  COLMAP files, default `.png`.
- `--video-extension`: video file extension to read, default `.mp4`. The dot is
  optional and matching is case-insensitive.
- `--skip-video-extraction`: keep existing `frame*/input` images and only
  write COLMAP text files.