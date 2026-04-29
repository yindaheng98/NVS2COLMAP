# NVS2COLMAP

Utilities for converting novel view synthesis datasets to COLMAP format.

## Supported Formats

- **Neural 3D Video Dataset**: scenes with `poses_bounds.npy` and one `mp4`
  file per camera. See `nvs2colmap/n3dv/README.md`.

## Quick Start

Install the Python runtime dependencies:

```bash
pip install numpy torch
```

For Neural 3D Video scenes, the command also needs `ffmpeg` and `ffprobe` on
`PATH`, or explicit paths via `--ffmpeg` and `--ffprobe`. If you want to run
the full COLMAP pipeline, also provide a COLMAP executable via
`--colmap-executable`.

Extract a Neural 3D Video scene and write per-frame COLMAP text models:

```bash
python -m nvs2colmap.n3dv \
  --path data/coffee_martini \
  --ffmpeg ffmpeg \
  --ffprobe ffprobe \
  --n-frames 300
```

Run the full COLMAP pipeline for each frame:

```bash
python -m nvs2colmap.n3dv \
  --path data/Robo360/xarm6_gold_rope_in_basket_2 \
  --ffmpeg D:/MyPrograms/ffmpeg.exe \
  --ffprobe D:/MyPrograms/ffprobe.exe \
  --video-extension MP4 \
  --n-frames 1 \
  --use-colmap \
  --colmap-executable data/colmap/COLMAP.bat \
  --colmap-use-gpu 1
```

By default, decoded frames are written to `frame*/images`, and the command also
writes `frame*/sparse/0` text models. With `--use-colmap`, decoded frames are
written to `frame*/input`, and each frame additionally gets the standard
COLMAP outputs such as `distorted/`, `images/`, `sparse/`, and `stereo/`.