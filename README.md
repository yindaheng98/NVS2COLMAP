# NVS2COLMAP

Utilities for converting novel view synthesis datasets to COLMAP format.

## Supported Formats

- **Neural 3D Video Dataset**: scenes with `poses_bounds.npy` and one `mp4`
  file per camera. See `nvs2colmap/n3dv/README.md`.

## Supported Datasets

- **Neural 3D Video Dataset**: dataset
  [facebookresearch/Neural_3D_Video](https://github.com/facebookresearch/Neural_3D_Video),
  paper
  [Neural 3D Video Synthesis from Multi-view Video](https://arxiv.org/abs/2103.02597).
- **StreamRF / Meet Room Dataset**: dataset
  [AlgoHunt/StreamRF](https://github.com/AlgoHunt/StreamRF), paper
  [Streaming Radiance Fields for 3D Video Synthesis](https://arxiv.org/abs/2210.14831).
- **Robo360**: dataset
  [liuyubian/Robo360](https://huggingface.co/datasets/liuyubian/Robo360),
  paper
  [Robo360: A 3D Omnispective Multi-Material Robotic Manipulation Dataset](https://arxiv.org/abs/2312.06686).

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

Start from source frame 10 and keep output frame numbering aligned with it:

```bash
python -m nvs2colmap.n3dv \
  --path data/coffee_martini \
  --ffmpeg ffmpeg \
  --ffprobe ffprobe \
  --start-number 10 \
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
COLMAP outputs such as `distorted/`, `images/`, `sparse/`, and `stereo/`. When
`--start-number N` is provided, decoding starts from source video frame `N`, and
the generated folders/images are also numbered from `N`.